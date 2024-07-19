import ipywidgets as w
import traitlets as tr


def bold(text):
    return "<b>{}</b>".format(text)


class MapList(w.HBox):
    """simple widget that takes a list and a set of allowed options, and
    allows the user to map the items in the list to the allowed options."""

    _value = tr.Dict()
    inputs = tr.List(default_value=[])
    options = tr.List(default_value=[])
    input_title = tr.Unicode(default_value="")
    map_title = tr.Unicode(default_value="")

    @tr.observe("inputs")
    def obs_inputs(self, onchange):
        self.vbx_in.children = [w.Label(f"{l} = ".format(l)) for l in self.inputs]
        self.vbx_map.children = [w.Dropdown() for l in self.inputs]
        self.obs_options("")
        self._init_watch()

    @tr.observe("options")
    def obs_options(self, onchange):
        for n in range(0, len(self.vbx_map.children)):
            self.vbx_map.children[n].options = self.options

    @tr.observe("input_title")
    def obs_input_title(self, onchange):
        self.html_input_title.value = bold(self.input_title)

    @tr.observe("map_title")
    def obs_map_title(self, onchange):
        self.html_map_title.value = bold(self.map_title)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.inputs = list(value.keys())
        for c, v in zip(self.vbx_map.children[1:], value.values()):
            c.value = v

    def __init__(self, **kwargs):
        self.vbx_in = w.VBox()
        self.vbx_map = w.VBox()
        self.html_input_title = w.HTML(bold("input title"))
        self.html_map_title = w.HTML(bold("map title"))
        self.vbx_in_title = w.VBox([self.html_input_title, self.vbx_in])
        self.vbx_map_title = w.VBox([self.html_map_title, self.vbx_map])
        super().__init__(**kwargs)
        self.children = [self.vbx_in_title, self.vbx_map_title]
        if "value" in kwargs:
            self.value = kwargs["value"]

    def _init_watch(self):
        for c in self.vbx_map.children:
            c.observe(self._update_value, "value")

    def _update_value(self, onchange):
        self._value = dict(zip(self.inputs, [c.value for c in self.vbx_map.children]))


if __name__ == "__main__":
    from IPython.display import display

    ui = MapList(
        inputs=list("abcd"),
        options=list("abcd"),
        value={"a": "a", "b": "b", "c": "c", "d": "d"},
    )
    display(ui)
