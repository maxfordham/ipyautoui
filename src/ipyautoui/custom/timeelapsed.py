# +
import ipywidgets as w
import traitlets as tr
from datetime import datetime, timedelta
from IPython.display import display


def timedelta_to_str(t_delta: timedelta) -> str:
    total_seconds = int(t_delta.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}mins {seconds}secs"


class TimeElapsed(w.HBox):
    time_string_format = tr.Unicode("%H:%M:%S")
    start_str = tr.Unicode("<b>start-time=</b>")
    end_str = tr.Unicode("<b>end-time=</b>")
    delta_str = tr.Unicode("<b>elapsed-time⏱=</b>")
    start_time = tr.Instance(klass=datetime, allow_none=True, default_value=None)
    end_time = tr.Instance(klass=datetime, allow_none=True, default_value=None)
    time_delta = tr.Instance(klass=timedelta, allow_none=True, default_value=None)
    fn_timedelta_to_str = tr.Callable(default_value=timedelta_to_str)

    @tr.observe("start_time", "end_time")
    def update(self, on_change):
        if self.start_time is not None and self.end_time is not None:
            time_delta = self.end_time - self.start_time
            if time_delta.total_seconds() >= 0:
                self.time_delta = time_delta
            else:
                self.time_delta = None

    @tr.observe("start_str")
    def observe_start_str(self, on_change):
        self.html_start_str.value = self.start_str

    @tr.observe("end_str")
    def observe_start_str(self, on_change):
        self.html_end_str.value = self.end_str

    @tr.observe("delta_str")
    def observe_delta_str(self, on_change):
        if self.delta_str is not None:
            self.html_delta_str.value = self.delta_str
        else:
            self.html_delta_str.value = ""

    @tr.observe("start_time")
    def observe_start_time(self, on_change):
        if self.start_time is not None:
            self.html_start.value = (
                f"{self.start_time.strftime(self.time_string_format)}"
            )
        else:
            self.html_start.value = ""

    @tr.observe("end_time")
    def observe_end_time(self, on_change):
        if self.end_time is not None:
            self.html_end.value = f"{self.end_time.strftime(self.time_string_format)}"
        else:
            self.html_end.value = ""

    @tr.observe("time_delta")
    def observe_time_delta(self, on_change):
        if self.time_delta is not None:
            self.html_delta.value = f"{timedelta_to_str(self.time_delta)}"
        else:
            self.html_delta.value = ""

    def __init__(self, **kwargs):
        self.html_start = w.HTML()
        self.html_end = w.HTML()
        self.html_delta = w.HTML()
        super().__init__(**kwargs)

        self.html_start_str = w.HTML(self.start_str)
        self.html_end_str = w.HTML(self.end_str)
        self.html_delta_str = w.HTML(self.delta_str)

        self.children = [
            w.HBox([self.html_start_str, self.html_start]),
            w.HBox([self.html_end_str, self.html_end]),
            w.HBox([self.html_delta_str, self.html_delta]),
        ]


if __name__ == "__main__":
    te = TimeElapsed(start_time=datetime.now())
    display(te)

# +
if __name__ == "__main__":
    te.end_time = datetime.now()

# +
