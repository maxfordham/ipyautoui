import ipywidgets as w
import traitlets as tr
import typing as ty


# +

def value_type_as_json(value):
    if isinstance(value, str):
        return "string"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, bool):
        return "number"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object"
    elif isinstance(value, None):
        return "null"
    else:
        raise ValueError("value must be: string, integer, number, array, object or None")
    


# -

class AnyOf(w.HBox):
    anyOf = tr.List(trait=tr.Dict())  # TODO: use any_of? how to recursively change keys?
    selected_item = tr.Dict()
    map_value_type = tr.Dict()
    titles = tr.List(trait=tr.Unicode())
    _value = tr.Any()
    
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        t = value_type_as_json(value)
        ti = self.map_type_title[t]
        self.select.value = ti
        self.widget.value = value
        

    @tr.observe("anyOf")
    def _anyOf(self, on_change):
        get_name = lambda l: l["title"] if "title" in l else l["type"]
        self.map_type_title = {get_name(l):l["type"] for l in self.anyOf}
        self.titles = list(self.map_type_title.values())
        self.select.options = self.titles

    @tr.observe("selected_item")
    def _selected_item(self, on_change):
        from ipyautoui.automapschema import get_widget

        self.widget = get_widget(self.selected_item)
        self.children = [self.widget]
        self._init_watch_widget()
        self._watch_widget("")

    def __init__(self, **kwargs):
        self.select = w.Dropdown(description="select widget:")
        super().__init__(**kwargs)
        self.children = [self.select]
        self._init_controls()
        if "value" in kwargs:
            self.value = kwargs["value"]

    def _init_controls(self):
        self.select.observe(self._select, "value")

    def _init_watch_widget(self):
        if self.widget.has_trait("value"):
            self.widget.observe(self._watch_widget, "value")
        elif self.widget.has_trait("_value"):
            self.widget.observe(self._watch_widget, "_value")
        else:
            pass

    def _watch_widget(self, on_change):
        self._value = self.widget.value

    def _select(self, on_change):
        n = self.titles.index(self.select.value)
        self.selected_item = self.anyOf[n]

if __name__ == "__main__":
    
    from pydantic import conint, RootModel
    from enum import Enum

    class MyEnum(str, Enum):
        state1 = 'state1'
        state2 = 'state2'

    class RootSimple(RootModel):
        root: ty.Union[conint(ge=0, le=3), str] = 2

    sch = RootSimple.model_json_schema()

    ui = AnyOf(**sch)
    display(sch)
    display(ui)

if __name__ == "__main__":
    sch["value"] = 2
    ui = AnyOf(**sch)
    display(sch)
    display(ui)


