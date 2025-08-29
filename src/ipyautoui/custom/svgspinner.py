# +
import ipywidgets as w
import traitlets as tr
from IPython.display import SVG, clear_output, display
from ipyautoui._utils import show_hide_widget
from ipyautoui.constants import PATH_SVG


class SvgSpinner(w.VBox):
    show = tr.Bool(default_value=True)
    complete = tr.Bool(default_value=False)

    @tr.observe("show")
    def _show(self, change):
        show_hide_widget(self, self.show)

    @tr.observe("complete")
    def _complete(self, change):
        if self.complete:
            self.display_done()
        else:
            self.display_spinner()

    def __init__(self, path_svg=PATH_SVG, **kwargs):
        super().__init__(**kwargs)
        self.path_svg = path_svg
        self.out = w.Output(layout=dict(width="25px"))
        self.children = [self.out]
        self.display_spinner()

    def display_done(self):
        with self.out:
            clear_output()
            display(w.HTML("✔"))

    def display_spinner(self):
        with self.out:
            clear_output()
            display(SVG(self.path_svg))


if __name__ == "__main__":
    spinner = SvgSpinner()
    display(spinner)

# +
if __name__ == "__main__":
    spinner.complete = True

# +
if __name__ == "__main__":
    spinner.show = False

# +
