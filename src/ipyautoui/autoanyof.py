

import ipywidgets as w
import traitlets as tr
import typing as ty
from ipyautoui._utils import type_as_json


def get_anyOf_type(l):
    if "anyOf" in l:
        return l["anyOf"]
    elif "type" in l and l["type"] != "object":
        return l["type"]
    elif "type" in l and l["type"] == "object":
        return l["type"] + "-" + "".join(l["properties"].keys())
    else:
        raise ValueError(f"could not find widget type:\n{l}")


class AnyOf(w.HBox):
    allOf = tr.List(allow_none=True, default_value=None)
    anyOf = tr.List(
        trait=tr.Dict()
    )  # TODO: use any_of? how to recursively change keys?
    selected_item = tr.Dict()
    map_title_type = tr.Dict()
    titles = tr.List(trait=tr.Unicode())
    _value = tr.Any()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        t_in = type_as_json(value)
        ti = None
        try:
            ti = self.map_type_title[t_in]
        except:
            s_in = set(t_in.replace("object-", ""))
            ts = [_ for _ in self.map_title_type.values() if "object" in _]
            for t in ts:
                s_ui = set(t.replace("object-", ""))
                if s_in.issubset(s_ui):
                    ti = self.map_type_title[t]
                    break

        self.select.value = ti
        if not ti is None:
            self.widget.value = value

    @tr.observe("allOf")
    def _allOf(self, on_change):
        if len(self.allOf) != 1:
            raise ValueError("en(self.allOf) != 1")
        else:
            self.anyOf = self.allOf[0]["anyOf"]

    @tr.observe("anyOf")
    def _anyOf(self, on_change):
        get_name = lambda l: l["title"] if "title" in l else l["type"]
        self.map_title_type = {get_name(l): get_anyOf_type(l) for l in self.anyOf}
        self.titles = list(self.map_title_type.keys())
        self.select.options = self.titles

    @property
    def map_type_title(self):
        return {v: k for k, v in self.map_title_type.items()}

    @tr.observe("selected_item")
    def _selected_item(self, on_change):
        from ipyautoui.automapschema import get_widget

        self.widget = get_widget(self.selected_item)
        self.children = [self.widget]
        self._init_watch_widget()
        self._watch_widget("")

    def __init__(self, **kwargs):
        self.select = w.Dropdown(description="select widget:")
        value = kwargs.pop("value", None)
        super().__init__(**kwargs)
        self.children = [self.select]
        self._init_controls()
        if value is not None:
            self.value = value

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
    from pydantic import conint, RootModel, BaseModel, Field
    from enum import Enum
    from ipyautoui.automapschema import _init_model_schema
    from typing_extensions import Annotated
    from IPython.display import display

    class MyEnum(str, Enum):
        state1 = "state1"
        state2 = "state2"

    class MyObj(BaseModel):
        a: int
        b: float
        c: str

    class MyOtherObj(BaseModel):
        d: int
        e: float
        e_: ty.Optional[Annotated[float, Field(ge=1, le=3)]]
        f: str
        g: ty.Optional[bool]

    class RootSimple(RootModel):
        root: ty.Union[conint(ge=0, le=3), str, MyObj, MyOtherObj] = 2

    m, sch = _init_model_schema(RootSimple)

    ui = AnyOf(**sch)
    display(sch)
    display(ui)

if __name__ == "__main__":
    ui.value = {"a": 0, "b": 0.0, "c": ""}

if __name__ == "__main__":
    ui.value = {"d": 0, "e": 0.0, "f": ""}

if __name__ == "__main__":
    from pydantic import conint, RootModel, BaseModel, Field
    from enum import Enum
    from ipyautoui.automapschema import _init_model_schema
    from typing_extensions import Annotated

    class MyEnum(str, Enum):
        state1 = "state1"
        state2 = "state2"

    class MyObj(BaseModel):
        a: int
        b: float
        c: str

    class MyOtherObj(BaseModel):
        d: int
        e: float
        e_: ty.Optional[Annotated[float, Field(ge=1, le=3)]]
        f: str
        g: ty.Optional[bool]

    class RootSimple(RootModel):
        root: ty.Union[conint(ge=0, le=3), str, MyObj, MyOtherObj] = 2

    m, sch = _init_model_schema(RootSimple)

    ui = AnyOf(**sch)
    display(sch)
    display(ui)
