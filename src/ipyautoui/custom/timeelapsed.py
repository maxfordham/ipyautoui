# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
from datetime import datetime, timedelta
import ipywidgets as w
import traitlets as tr

def timedelta_to_str(t_delta: timedelta) -> str:
    total_seconds = int(t_delta.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}mins {seconds}secs"

class TimeElapsed(w.HBox):
    time_string_format = tr.Unicode('%H:%M:%S')
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
            self.time_delta = self.end_time - self.start_time
            
    @tr.observe("start_str")
    def observe_start_str(self, on_change):
        self.html_start_str.value = self.start_str

    @tr.observe("end_str")
    def observe_start_str(self, on_change):
        self.html_end_str.value = self.end_str

    @tr.observe("delta_str")
    def observe_delta_str(self, on_change):
        self.html_delta_str.value = self.delta_str

    @tr.observe("start_time")
    def observe_start_time(self, on_change):
        self.html_start.value = f"{self.start_time.strftime(self.time_string_format)}"

    @tr.observe("end_time")
    def observe_end_time(self, on_change):
        self.html_end.value = f"{self.end_time.strftime(self.time_string_format)}"

    @tr.observe("time_delta")
    def observe_time_delta(self, on_change):
        self.html_delta.value = f"{timedelta_to_str(self.time_delta)}"
    
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
    te = TimeElapsed(start_time = datetime.now())
    display(te)

# %%
if __name__ == "__main__":
    te.end_time = datetime.now()
