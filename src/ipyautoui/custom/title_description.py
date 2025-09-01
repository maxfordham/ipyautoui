
"""generic support for observed title and description"""


# TODO: move to root

import traitlets as tr
import ipywidgets as w
from ipyautoui._utils import show_hide_widget


class TitleDescription(tr.HasTraits):
    title = tr.Unicode(default_value=None, allow_none=True)
    unit = tr.Unicode(default_value=None, allow_none=True)
    description = tr.Unicode(default_value=None, allow_none=True)
    show_title = tr.Bool(default_value=True)
    show_unit = tr.Bool(default_value=True)
    show_description = tr.Bool(default_value=True)

    @tr.observe("title")
    def _observe_title(self, change):
        self.html_title.value = f"<b>{self.title}</b>"

    @tr.observe("unit")
    def _observe_unit(self, change):
        if self.unit:
            self.html_unit.value += f"<b>({self.unit})</b>"
        else:
            self.html_unit.value = ""

    @tr.observe("description")
    def _observe_description(self, change):
        self.html_description.value = f"<i>{self.description}</i>"

    @tr.observe("show_title")
    def _observe_show_title(self, change):
        show_hide_widget(self.html_title, self.show_title)

    @tr.observe("show_unit")
    def _observe_show_unit(self, change):
        show_hide_widget(self.html_unit, self.show_unit)

    @tr.observe("show_description")
    def _observe_show_description(self, change):
        show_hide_widget(self.html_description, self.show_description)

    @property
    def html_title(self):
        self._init_title()
        return self._html_title

    @property
    def html_unit(self):
        self._init_unit()
        return self._html_unit

    @property
    def html_description(self):
        self._init_description()
        return self._html_description

    def _init_title(self):
        if not hasattr(self, "_html_title"):
            self._html_title = w.HTML()

    def _init_unit(self):
        if not hasattr(self, "_html_unit"):
            self._html_unit = w.HTML()

    def _init_description(self):
        if not hasattr(self, "_html_description"):
            self._html_description = w.HTML()

    @property
    def hbx_title_description(self):
        self._init_title()
        self._init_unit()
        self._init_description()
        return w.HBox(
            [
                self.html_title,
                self.html_unit,
                self.html_description,
            ]
        )


if __name__ == "__main__":
    from IPython.display import display

    class Test(w.HBox, TitleDescription):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.children = [w.Button(icon="help"), self.html_title, self.html_unit]

    t = Test(title="title", unit="mm", description="description")
    display(t)
