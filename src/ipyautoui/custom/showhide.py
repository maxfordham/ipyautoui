# +
import ipywidgets as w
import traitlets as tr
from IPython.display import clear_output, display
from ipyautoui.constants import KWARGS_COLLAPSE, KWARGS_DISPLAY
import typing as ty


class ShowHide(w.VBox):
    """simple show/hide widget that displays output of a callable that is pass as the input"""

    fn_display = tr.Callable()
    is_show = tr.Bool()
    title = tr.Unicode()

    @tr.default("fn_display")
    def _fn_display(self):
        return lambda: print("display")

    def __init__(
        self,
        fn_display: ty.Callable = lambda: w.HTML("😲"),
        title: str = "title",
        auto_open: bool = False,
        button_width: str = None,
    ):
        """
        Args:
            fn_display: widget our output to display. it is displayed like this:
                `display(self.fn_display())`
            title:
        """
        self.button_width = button_width
        self._init_form()
        self.fn_display = fn_display
        self.title = title
        if auto_open:
            self.btn_display.value = True
        if button_width is not None:
            self.btn_display.layout.width = "300px"

    def _init_form(self):
        super().__init__(layout=w.Layout(border="solid LightCyan 2px"))
        self.hbx_title = w.HBox()
        self.btn_display = w.ToggleButton(**KWARGS_DISPLAY)
        if self.button_width is not None:
            self.btn_display.layout.width = self.button_width
        self.html_title = w.HTML()
        self.out = w.Output()
        self.out.layout.display = "None"
        self.hbx_title.children = [self.btn_display, self.html_title]
        self.children = [self.hbx_title, self.out]
        self._observe_fn_display("asd")
        self._init_controls()

    def _init_controls(self):
        self.btn_display.observe(self.check_is_show, "value")

    def check_is_show(self, on_change):
        self.is_show = on_change["new"]

    def show(self):
        self.btn_display.value = True

    def hide(self):
        self.btn_display.value = False

    @tr.observe("title")
    def _observe_title(self, change):
        self.html_title.value = self.title

    @tr.observe("fn_display")
    def _observe_fn_display(self, change):
        self.btn_display.unobserve(None)
        self.btn_display.observe(self.display_out, "value")
        self.btn_display.observe(self.check_is_show, "value")

    def display_out(self, click):
        with self.out:
            if self.btn_display.value:
                {
                    setattr(self.btn_display, k, v)
                    for k, v in KWARGS_COLLAPSE.items()
                    if k != "layout"
                }
                self.out.layout.display = ""
                clear_output()
                display(self.fn_display())
            else:
                {
                    setattr(self.btn_display, k, v)
                    for k, v in KWARGS_DISPLAY.items()
                    if k != "layout"
                }
                self.out.layout.display = "None"
                clear_output()


# -
if __name__ == "__main__":
    d = ShowHide(auto_open=True)
    display(d)
