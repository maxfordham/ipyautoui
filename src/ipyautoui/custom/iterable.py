# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# TODO: support arrary / dictionary of length = 0
# TODO: change `align_horizontal` to `align_horizontal` and flip logic
"""A generic iterable object.

Creates an array object where widgets can be added or removed. if the widgets have a "value" or "_value" trait the 
that trait is automatically watched / observed for changes.

This item is used for the AutoObject `array`. 
"""
# TODO: move iterable.py to root
# %run ../_dev_sys_path_append.py
# %run __init__.py
# %load_ext lab_black

# +
import ipywidgets as w
import traitlets as tr
from traitlets import validate
import typing as ty
from IPython.display import display
from ipyautoui.basemodel import BaseModel
from pydantic import model_validator
import uuid
from uuid import UUID
import functools
from ipyautoui.constants import (
    ADD_BUTTON_KWARGS,
    REMOVE_BUTTON_KWARGS,
    BLANK_BUTTON_KWARGS,
    BUTTON_WIDTH_MIN,
    BUTTON_HEIGHT_MIN,
    BUTTON_MIN_SIZE,
)
from ipyautoui._utils import frozenmap
from ipyautoui.autowidgets import create_widget_caller
import logging
from ipyautoui.custom.title_description import TitleDescription
import enum
import string
import random
import inspect
from ipyautoui.automapschema import (
    replace_refs,
    remove_non_present_kwargs,
    widgetcaller,
    map_widget,
)
from ipyautoui.automapschema import from_schema_method
from ipyautoui.automapschema import get_widget


logger = logging.getLogger(__name__)
BOX = frozenmap({True: w.HBox, False: w.VBox})
TOGGLE_BUTTON_KWARGS = frozenmap(
    icon="",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
)


# +
def flip(box, align_horizontal=False):
    if align_horizontal:
        box.layout.display = "flex"
        box.layout.flex_flow = "row"
        box.layout.align_items = "stretch"

    else:
        box.layout.display = "flex"
        box.layout.flex_flow = "column"
        box.layout.align_items = "stretch"


class ItemControl(enum.Enum):
    add_remove = "add_remove"
    append_only = "append_only"
    remove_only = "remove_only"
    none = None


# USE: number (as int)


# TODO: inherit AutoBox ?
class ItemBox(w.Box):
    index = tr.Int()
    key = tr.Union([tr.Int(), tr.Unicode(), tr.Instance(klass=UUID)])
    add_remove_controls = tr.UseEnum(ItemControl, default_value=ItemControl.add_remove)
    obj = tr.Any(
        default_value=w.ToggleButton(description="placeholder")
    )  # TODO: rename widget

    # show_hash = tr.Bool(default_value=True)  # TODO

    @tr.default("key")
    def _default_key(self):
        return uuid.uuid4()

    @tr.observe("add_remove_controls")
    def _add_remove_controls(self, on_change):
        self.map_controls[self.add_remove_controls]()

    @tr.observe("obj")
    def _obj(self, on_change):
        try:
            self.children[2].children = [self.obj]
        except:
            self.set_children()
            self.children[2].children = [self.obj]

    def _remove_only(self):
        self.bn_add.layout.display = "None"
        self.bn_remove.layout.display = ""

    def _append_only(self):  # TODO: remove option?
        self.bn_add.layout.display = "None"
        self.bn_remove.layout.display = ""

    def _add_remove(self):
        self.bn_add.layout.display = ""
        self.bn_remove.layout.display = ""

    def _no_user_controls(self):
        self.bn_add.layout.display = "None"
        self.bn_remove.layout.display = "None"

    def __init__(self, **kwargs):
        self.bn_add = w.Button(**ADD_BUTTON_KWARGS)
        self.bn_remove = w.Button(**REMOVE_BUTTON_KWARGS)
        self.map_controls = {
            ItemControl.append_only: self._append_only,
            ItemControl.add_remove: self._add_remove,
            ItemControl.remove_only: self._remove_only,
            ItemControl.none: self._no_user_controls,
        }
        super().__init__(**kwargs)
        self.set_children()

    def set_children(self):
        self.children = [
            w.Box(
                [self.bn_add, self.bn_remove], layout=w.Layout(flex="1 0 auto")
            ),  # buttons
            w.Box(layout=w.Layout(flex="1 0 auto")),  # label
            w.Box([self.obj], layout=w.Layout(flex="100%")),  # item
        ]


# -


class Array(w.VBox, TitleDescription):
    _value = tr.List()
    fn_add = tr.Callable(
        default_value=lambda **kwargs: w.ToggleButton(
            description=(
                "add test "
                + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            )
        )
    )
    fn_remove = tr.Callable(
        default_value=lambda box: print(f"on remove {str(box.index)}")
    )
    sort_on_index = tr.Bool(default_value=True)  # if False then sort_on_key
    length = tr.Int(default_value=0)
    add_remove_controls = tr.UseEnum(ItemControl, default_value=ItemControl.add_remove)
    align_horizontal = tr.Bool(default_value=False)
    min_items = tr.Int(default_value=0)
    max_items = tr.Int(default_value=None, allow_none=True)
    type = tr.Unicode(default_value="array")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: ty.List):
        self.boxes = []
        self.bx_boxes.children = []
        [self.add_row() for v in value]
        for n, v in enumerate(value):
            self.boxes[n].obj.value = v
        self._update_value("onchange")

    @tr.validate("type")
    def _type(self, proposal):
        if proposal["value"] != "array":
            raise ValueError("type must be array")
        else:
            return "array"

    @tr.observe("length")
    def _length(self, on_change):
        if self.length == 0:
            self.display_bn_add_from_zero(True)
        else:
            if self.add_remove_controls == ItemControl.append_only:
                self.display_bn_add_from_zero(True)
            else:
                self.display_bn_add_from_zero(False)

    @tr.validate("fn_remove")
    def _valid_fn_remove(self, proposal):
        if not len(inspect.signature(proposal["value"]).parameters) == 1:
            raise ValueError(
                "fn_remove must have 1no arg == item box. the item box that is being deleted. i.e. `self.fn_remove(bx)"
            )

    @tr.observe("add_remove_controls")
    def _add_remove_controls(self, on_change):
        for bx in self.boxes:
            bx.add_remove_controls = self.add_remove_controls

        if (
            self.add_remove_controls == ItemControl.remove_only
            or self.add_remove_controls == ItemControl.none
        ):
            self.display_bn_add_from_zero(False)
        else:
            self.display_bn_add_from_zero(True)

    @tr.observe("align_horizontal")
    def _align_horizontal(self, on_change):
        flip(self.bx_boxes, self.align_horizontal)

    def display_bn_add_from_zero(self, display: bool):
        if display:
            self.bn_add_from_zero.layout.display = ""
        else:
            self.bn_add_from_zero.layout.display = "None"

    def __init__(self, **kwargs):
        self.bn_add_from_zero = w.Button(**ADD_BUTTON_KWARGS)
        self.bn_add_from_zero.layout.display = "None"
        if "objects" not in kwargs:  # TODO: objects -> li_widgets ?
            self.objects = []
            self.bn_add_from_zero.layout.display = ""
        else:
            self.objects = kwargs["objects"]
        self.bx_boxes = w.Box()
        self.boxes = [ItemBox(n, obj=obj) for n, obj in enumerate(self.objects)]
        super().__init__(**kwargs)
        self._update_title_description()
        self.children = [self.html_title, self.bn_add_from_zero, self.bx_boxes]
        self._init_controls()
        self._update_boxes()
        self._align_horizontal("on_change")
        self.layout.border = "1px solid #00a3e0"

    def _init_controls(self):
        [self._init_row_controls(key=i.key) for i in self.boxes]
        self.bx_boxes.observe(self.get_length, "children")
        self.bn_add_from_zero.on_click(self._append_row)

    def get_length(self, on_change):
        self.length = len(self.boxes)

    def _get_attribute(self, key, get):
        return [getattr(bx, get) for bx in self.boxes if bx.key == key][0]

    def _init_row_controls(self, key=None):
        self._get_attribute(key, "bn_add").on_click(
            functools.partial(self._add_row, key=key)
        )
        self._get_attribute(key, "bn_remove").on_click(
            functools.partial(self._remove_rows, key=key)
        )
        obj = self._get_attribute(key, "obj")
        if "value" in obj.traits():
            obj.observe(self._update_value, names="value")
        elif "_value" in obj.traits():
            obj.observe(self._update_value, names="_value")
        else:
            logging.info(
                'array item must have either "value" or "_value" trait to be observed'
            )

    def _sort_boxes(self):
        if self.sort_on_index:
            sort = sorted(self.boxes, key=lambda k: k.index)
        else:
            sort = sorted(self.boxes, key=lambda k: str(k.key))
        for n, s in enumerate(sort):
            s.index = n
        self.boxes = sort

    def _update_value(self, on_change):
        self._value = [bx.obj.value for bx in self.boxes]

    def _update_boxes(self):
        self.bx_boxes.children = self.boxes

    def _append_row(self, onclick):
        key = None
        if len(self.boxes) > 0:
            key = self.boxes[-1].key
        self.add_row(key=key)

    def _add_row(self, onclick, key=None):
        self.add_row(key=key)

    def add_row(self, key=None, new_key=None, add_kwargs=None, obj=None):
        """add row to array after key. if key=None then append to end"""
        if self.max_items is not None and len(self.boxes) >= self.max_items:
            logging.warning(
                f"ERROR: you can't have more that {self.max_items} items. len(self.boxes) >= self.max_items"
            )
            return None

        if key is None:
            if len(self.boxes) == 0:
                index = 0
            else:
                # append
                key = self.boxes[-1].key
                index = self._get_attribute(key, "index")
        else:
            index = self._get_attribute(key, "index")
        if new_key is not None:
            if new_key in [i.key for i in self.boxes]:
                logger.warning(f"ERROR: {new_key} already exists in keys")
                return None
        else:
            new_key = uuid.uuid4()

        if add_kwargs is None:
            add_kwargs = {}

        if obj is None:
            new_obj = self.fn_add(**add_kwargs)
        else:
            new_obj = obj

        bx = ItemBox(
            index=index,
            key=new_key,
            obj=new_obj,
            add_remove_controls=self.add_remove_controls,
        )
        self.boxes.insert(index + 1, bx)
        self._sort_boxes()  # update map
        self._init_row_controls(bx.key)  # init controls
        self._update_boxes()

    def _remove_rows(self, onclick, key=None):
        self.remove_row(key=key)

    def remove_row(self, key=None, fn_onremove=None):
        if self.min_items is not None and len(self.boxes) <= self.min_items:
            logging.warning(
                f"ERROR: you can't have more that {self.max_items} items. len(self.boxes) <= self.min_items"
            )
            return None
        if len(self.boxes) <= 1:
            pass
        if key is None:
            print("key is None")
            key = self.iterable[-1].key
        n = self._get_attribute(key, "index")
        bx = self.boxes[n]
        self.fn_remove(bx)
        self.boxes.pop(n)
        self._sort_boxes()
        self._update_boxes()


class AutoArray(Array):
    allOf = tr.List(allow_none=True, default_value=None)
    items = tr.Dict(allow_none=True, default_value=None)
    prefix_items = tr.Dict(allow_none=True, default_value=None)
    # ^ TODO: add functionality: https://json-schema.org/understanding-json-schema/reference/array.html#id7
    #       : adds tuple functionality
    #       : maybe this should be a different widget all together?

    @property
    def value(self):
        return self._value

    @value.setter
    def value(
        self, value: ty.List
    ):  # TODO: should be able to have this in parent `Array` ?
        self.boxes = []
        self.bx_boxes.children = []
        [self.add_row() for v in value]
        for n, v in enumerate(value):
            self.boxes[n].obj.value = v
        self._update_value("onchange")

    @tr.observe("allOf")  # TODO: is this requried?
    def _allOf(self, on_change):
        if self.allOf is not None and len(self.allOf) == 1:
            if "items" in self.allOf[0]:
                self.items = self.allOf[0]["items"]
            else:
                raise ValueError("items not found in allOf[0]")
        else:
            raise ValueError("allOf not supported from iterables")

    @tr.observe("items")
    def _items(self, on_change):
        self.fn_add = functools.partial(get_widget, self.items)

    @classmethod
    def from_schema(cls, schema, value=None):
        return from_schema_method(cls, schema, value=value)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "value" in kwargs.keys():
            self.value = kwargs["value"]


if __name__ == "__main__":
    from pydantic import RootModel, Field, BaseModel
    from ipyautoui.demo_schemas import ArrayWithUnionType, RootArray, RootArrayEnum

    class MyString(RootModel):
        root: str = Field(description="asdfsadf")

    class MyObject(BaseModel):
        stringy: str = Field("stringy", description="asdfsadf")
        inty: int = 1
        floaty: ty.Union[float, str] = 1.5

    class ArrayWithUnionType(RootModel):
        """hl;askdfhas;dlkf"""

        root: list[MyObject]

    s = replace_refs(ArrayWithUnionType.model_json_schema())
    v = MyObject(floaty=0.2).model_dump()
    s["value"] = [v]
    # ui = AutoArrayNew(**{**s, **{"value": v}})
    ui = AutoArray(**s)
    display(ui)


if __name__ == "__main__":
    from typing import ForwardRef
    from pydantic import RootModel, Field, BaseModel

    MyArray = ForwardRef("MyArray")

    class MyObject(BaseModel):
        stringy: str = Field("stringy", description="asdfsadf")
        inty: int = 1
        floaty: float = 1.5

    class MyArray(RootModel):
        """hl;askdfhas;dlkf"""

        root: list[ty.Union[MyArray, MyObject]]

    s = replace_refs(MyArray.model_json_schema())
    ui = AutoArray(**s)
    display(ui)

if __name__ == "__main__":
    import random
    from IPython.display import Markdown

    def get_di():
        words = [
            "a",
            "AAA",
            "AAAS",
            "aardvark",
            "Aarhus",
            "Aaron",
            "ABA",
            "Ababa",
            "aback",
            "abacus",
            "abalone",
            "abandon",
            "abase",
        ]
        n = random.randint(0, len(words) - 1)
        m = random.randint(0, 1)
        _bool = {0: False, 1: True}
        return {words[n]: _bool[m]}

    def fn_add(value=None):
        if value is None:
            return TestItem(di=get_di())
        else:
            return TestItem(di=value)

    class TestItem(w.HBox):
        _value = tr.Dict()

        def __init__(self, di: ty.Dict = get_di()):
            self._value = di
            self._init_form()
            self._init_controls()

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            self._value = value
            k, v = list(value.keys())[0], list(value.values())[0]
            self._label.value = k
            self._bool.value = v

        def _init_form(self):
            self._label = w.HTML(f"{list(self.value.keys())[0]}")
            self._bool = w.ToggleButton(list(self.value.values())[0])
            super().__init__(children=[self._bool, self._label])  # self._acc,

        def _init_controls(self):
            self._bool.observe(self._set_value, names="value")

        def _set_value(self, change):
            self.value = {self._label.value: self._bool.value}

    di_arr = {
        "items": [fn_add()],
        "fn_add": fn_add,
        "maxlen": 10,
        "show_hash": "index",
        "toggle": True,
        "title": "Array",
        "description": "asdf",
        "add_remove_controls": "append_only",
        "orient_rows": False,
    }

    arr = Array(**di_arr)
    display(arr)

if __name__ == "__main__":
    from ipyautoui.autowidgets import create_widget_caller
    from ipyautoui.autoipywidget import AutoObject
    from ipyautoui.demo_schemas import RootArray

    schema = RootArray.model_json_schema()
    ui = AutoArray.from_schema(schema)
    display(ui)

# +
if __name__ == "__main__":
    di_arr = {
        "items": None,
        "fn_add": fn_add,
        "maxlen": 10,
        "show_hash": "index",
        #'toggle':True,
        "title": "Array",
        "add_remove_controls": "append_only",
        "orient_rows": False,
    }

    arr = Array(**di_arr)
    display(arr)

# TODO: add `Dictionary` that uses key not index as item ref
# -
if __name__ == "__main__":
    di_arr = {
        "value": [{"None": False}],
        "fn_add": fn_add,
        "maxlen": 10,
        "show_hash": "index",
        #'toggle':True,
        "title": "Array",
        "add_remove_controls": "append_only",
        "align_horizontal": True,
    }

    arr = Array(**di_arr)
    display(arr)

if __name__ == "__main__":
    arr.value = [{"None": False}, {"ads": True}]
