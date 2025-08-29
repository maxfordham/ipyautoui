
"""A generic iterable object.

Creates an array object where widgets can be added or removed. if the widgets have a "value" or "_value" trait the 
that trait is automatically watched / observed for changes.

This item is used for the AutoObject `array`. 
"""
# TODO: move iterable.py to root


# +
import ipywidgets as w
import traitlets as tr
import typing as ty
from IPython.display import display
from ipyautoui.basemodel import BaseModel
import uuid
from uuid import UUID
import functools
from ipyautoui.constants import (
    ADD_BUTTON_KWARGS,
    REMOVE_BUTTON_KWARGS,
    BUTTON_WIDTH_MIN,
    BUTTON_HEIGHT_MIN,
)
from ipyautoui._utils import frozenmap
import logging
from ipyautoui.custom.title_description import TitleDescription
import enum
import string
import random
from ipyautoui.automapschema import from_schema_method, get_widget
from jsonref import replace_refs
from ipyautoui.watch_validate import WatchValidate
from ipyautoui._utils import remove_non_present_kwargs, traits_in_kwargs

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


class ItemBox(w.Box):
    index = tr.Int()
    key = tr.Union([tr.Int(), tr.Unicode(), tr.Instance(klass=UUID)])
    add_remove_controls = tr.UseEnum(ItemControl, default_value=ItemControl.add_remove)
    widget = tr.Any(
        default_value=w.ToggleButton(description="placeholder")
    )  # TODO: rename widget

    @tr.default("key")
    def _default_key(self):
        return uuid.uuid4()

    @tr.observe("add_remove_controls")
    def _add_remove_controls(self, on_change):
        self.map_controls[self.add_remove_controls]()

    @tr.observe("widget")
    def _widget(self, on_change):
        if len(self.children) == 0:
            self.set_children()
        self.children[2].children = [self.widget]

    def _remove_only(self):
        self.bn_add.layout.display = "None"
        self.bn_remove.layout.display = ""

    def _append_only(self):
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
            w.Box([self.widget], layout=w.Layout(flex="100%")),  # item
        ]


# -


class Array(w.VBox, WatchValidate):
    # TODO: explicitly define widget type for each item. AutoArray guesses it, but it can be overridden...

    _value = tr.List()  # NOTE: value setter and getter in `WatchValidate`
    # _widgets = tr.List() # TODO: list of DOMWidgets ?
    fn_add = tr.Callable(
        default_value=lambda **kwargs: w.ToggleButton(
            description=(
                "add test "
                + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
            )
        ),
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

    def _get_widgets(self):
        return [bx.widget for bx in self.boxes]

    @property
    def widgets(self):
        return self._get_widgets()

    @widgets.setter
    def widgets(self, widgets):
        self._set_boxes(widgets)
        [self._init_row_controls(key=i.key) for i in self.boxes]
        self._update_boxes()
        self._align_horizontal("")
        self._add_remove_controls("")

    def _set_boxes(self, widgets):
        self.boxes = [
            ItemBox(index=n, widget=widget) for n, widget in enumerate(widgets)
        ]
        self.di_boxes = {box.key: box for box in self.boxes} # HACK: to match with AutoObject. TODO: update to di_boxes? to match AutoObject

    def _update_widgets_from_value(self):
        diff = len(self.value) - len(self.boxes)
        if diff < 0:
            self.boxes = self.boxes[0 : len(self.value)]
        elif diff > 0:
            for n in range(0, diff):
                self.add_row(update_value=False)
        for n, v in enumerate(self.value):
            try:
                self.boxes[n].widget.value = v
            except Exception as e:
                raise ValueError(
                    f"{e}, widget-type={str(type(self.boxes[n].widget))}, value={v}, also, ",
                    f"\n value (len={len(self.value)} and widgets (len={len(self.widgets)}) must be same length",
                )
        self._update_boxes()

    @tr.validate("type")
    def _type(self, proposal):
        if proposal["value"] != "array":
            raise ValueError("type must be array")
        else:
            return "array"

    @tr.observe("length")
    def _length(self, on_change):
        if self.length == 0:
            if self.add_remove_controls == ItemControl.append_only:
                self.display_bn_add_from_zero(True)
            elif self.add_remove_controls == ItemControl.add_remove:
                self.display_bn_add_from_zero(True)
            else:
                self.display_bn_add_from_zero(False)
        else:
            self.display_bn_add_from_zero(False)

    # @tr.validate("fn_remove")
    # def _valid_fn_remove(self, proposal):
    #     if not len(inspect.signature(proposal["value"]).parameters) == 1:
    #         raise ValueError(
    #             "fn_remove must have 1no arg == item box. the item box that is being deleted. i.e. `self.fn_remove(bx)"
    #         )
    #     return proposal["value"]

    @tr.observe("add_remove_controls")
    def _add_remove_controls(self, on_change):
        for bx in self.boxes:
            bx.add_remove_controls = self.add_remove_controls

        if self.add_remove_controls == ItemControl.append_only:
            self.display_bn_add_from_zero(True)
        else:
            self.display_bn_add_from_zero(False)

    @tr.observe("align_horizontal")
    def _align_horizontal(self, on_change):
        flip(self.bx_boxes, self.align_horizontal)

    @property
    def map_key_value(self):
        return {
            b.key: (
                lambda w: (
                    w.value if hasattr(w, "value") or hasattr(w, "_value") else None
                )
            )(b.widget.value)
            for b in self.boxes
        }

    def display_bn_add_from_zero(self, display: bool):
        if display:
            self.bn_add_from_zero.layout.display = ""
        else:
            self.bn_add_from_zero.layout.display = "None"

    def __init__(self, **kwargs):
        self.vbx_widget = w.VBox()
        self.vbx_error = w.VBox()

        self.bn_add_from_zero = w.Button(**ADD_BUTTON_KWARGS)
        self.bn_add_from_zero.layout.display = "None"
        self.bx_boxes = w.Box()
        self._init_form_controls()
        self.widgets = self._init_widgets(kwargs)
        self.bn_add_from_zero.layout.display = ""
        super().__init__(**traits_in_kwargs(type(self), kwargs))
        self.vbx_widget.children = [self.bn_add_from_zero, self.bx_boxes]

        self.layout.border = "1px solid #00a3e0"
        self._set_children()
        self._post_init(**kwargs)

    def _set_children(self):
        self.children = [self.vbx_widget]

    def _init_widgets(self, kwargs):
        if "widgets" in kwargs:
            return kwargs["widgets"]
        else:
            return []

    def _post_init(self, **kwargs):
        pass  # NOTE: this can be overwritten to provide customisation

    def _init_form_controls(self):
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
        widget = self._get_attribute(key, "widget")
        for watch in ["_value", "value"]:
            if widget.has_trait(watch):
                # widget.observe(self._update_value, names=watch)
                widget.observe(self._watch_validate_change, names=watch)
                break  # if `_value` is found don't look for `value`
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

    def _get_value(self):
        get = lambda w: w.value if hasattr(w, "value") else None
        return [get(bx.widget) for bx in self.boxes]

    # def _update_value(self, on_change):
    #     if not self._silent:
    #         self._value = [bx.widget.value for bx in self.boxes]

    def _update_boxes(self):
        self.bx_boxes.children = self.boxes

    def _append_row(self, onclick):
        key = None
        if len(self.boxes) > 0:
            key = self.boxes[-1].key
        self.add_row(key=key)

    def _add_row(self, onclick, key=None):
        print(f"add row with key = {key}")
        logger.info(f"add row with key = {key}")
        self.add_row(key=key)

    def add_row(
        self, key=None, new_key=None, add_kwargs=None, widget=None, update_value=True
    ):
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

        if widget is None:
            new_obj = self.fn_add(**add_kwargs)
        else:
            new_obj = widget

        bx = ItemBox(
            index=index,
            key=new_key,
            widget=new_obj,
            add_remove_controls=self.add_remove_controls,
        )
        self.boxes.insert(index + 1, bx)
        self._sort_boxes()  # update map
        self._init_row_controls(bx.key)  # init controls
        self._update_boxes()
        # self._update_value("")
        if update_value:
            self._watch_validate_update_value()

    def _remove_rows(self, onclick, key=None):
        self.remove_row(key=key)

    def remove_row(self, key=None, fn_onremove=None):
        if self.min_items is not None and len(self.boxes) <= self.min_items:
            logging.warning(
                f"ERROR: you can't have more that {self.max_items} items. len(self.boxes) <= self.min_items"
            )
            return None
        if len(self.boxes) <= 1:
            self.display_bn_add_from_zero(display=True)
        if key is None:
            print("key is None")
            key = self.iterable[-1].key
        n = self._get_attribute(key, "index")
        bx = self.boxes[n]
        self.fn_remove(bx)
        self.boxes.pop(n)
        self._sort_boxes()
        self._update_boxes()
        # self._update_value("")
        self._watch_validate_update_value()


class Dictionary(Array):
    _value = tr.Dict()  # NOTE: value setter and getter in `WatchValidate`

    @tr.default("sort_on_index")
    def _sort_on_index(self):
        return False

    def _get_value(self):
        get = lambda w: w.value if hasattr(w, "value") else None
        return {bx.key: get(bx.widget) for bx in self.boxes}

    def _get_widgets(self):
        return {bx.key: bx.widget for bx in self.boxes}

    def _set_boxes(self, widgets):
        self.boxes = [
            ItemBox(index=n, key=k, widget=widget)
            for n, (k, widget) in enumerate(widgets.items())
        ]

    def _init_widgets(self, kwargs):
        if "widgets" in kwargs:
            return kwargs["widgets"]
        else:
            return {}


class AutoArray(Array):
    allOf = tr.List(allow_none=True, default_value=None)
    items = tr.Dict(allow_none=True, default_value=None)
    prefix_items = tr.Dict(allow_none=True, default_value=None)
    # ^ TODO: add functionality: https://json-schema.org/understanding-json-schema/reference/array.html#id7
    #       : adds tuple functionality
    #       : maybe this should be a different widget all together?

    @tr.observe("allOf")
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


class AutoArrayForm(AutoArray, TitleDescription):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "value" in kwargs.keys():
            self.value = kwargs["value"]
        self._update_title_description()

    def _set_children(self):
        self.children = [self.hbx_title_description, self.vbx_widget]


if __name__ == "__main__":

    class CustomItem(w.HBox):
        _value = tr.Unicode()

        @tr.observe("_value")
        def _obs_value(self, on_change):
            self.html_out.value = self._value

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            with self.hold_trait_notifications():
                self.a.value, self.b.value, self.c.value = value.split("-")

        def __init__(self, value=None, **kwargs):
            self.a = w.Text(layout=w.Layout(width="50px"))
            self.b = w.Text(layout=w.Layout(width="50px"))
            self.c = w.Text(layout=w.Layout(width="50px"))
            self.html_out = w.HTML(layout=w.Layout(width="140px"))
            super().__init__()
            self.children = [self.a, self.b, self.c, self.html_out]
            self._init_controls()
            if value is not None:
                self.value = value
            else:
                self._update("")

        def _init_controls(self):
            self.a.observe(self._update, names="value")
            self.b.observe(self._update, names="value")
            self.c.observe(self._update, names="value")

        def _update(self, change):
            self._value = "-".join([self.a.value, self.b.value, self.c.value])

    class CustomArray(Array):
        def fn_add(self, value=None):
            return CustomItem(value=value)

        def _post_init(self, **kwargs):
            self.title = "custom array"
            self._init_CustomArray_controls()

        def _init_CustomArray_controls(self):
            self.observe(self.update_colors, "_value")

        def update_colors(self, on_change):
            print("asdf")

    arr_cu = CustomArray()
    display(arr_cu)

if __name__ == "__main__":
    from pydantic import RootModel, Field, BaseModel
    from ipyautoui.demo_schemas import ArrayWithUnionType, RootArray, RootArrayEnum

    class MyString(RootModel):
        root: str = Field(description="form with custom item...")

    class MyObject(BaseModel):
        stringy: str = Field("stringy", description="asdfsadf")
        inty: int = 1
        floaty: ty.Union[float, str] = 1.5
        custom_item: str = Field(
            "a-b-c",
            description="custom_item",
            json_schema_extra={"autoui": "CustomItem"},
        )

    class ArrayWithUnionType(RootModel):
        """hl;askdfhas;dlkf"""

        root: list[MyObject]

    s = replace_refs(ArrayWithUnionType.model_json_schema(), merge_props=True)
    v = MyObject(floaty=0.2).model_dump()
    s["value"] = [v]
    ui = AutoArrayForm.from_schema(s)
    display(ui)

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

    s = replace_refs(ArrayWithUnionType.model_json_schema(), merge_props=True)
    v = MyObject(floaty=0.2).model_dump()
    s["value"] = [v]
    ui = AutoArrayForm.from_schema(s)
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

    s = replace_refs(MyArray.model_json_schema(), merge_props=True)
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
        "fn_add": fn_add,
        "max_items": 10,
        "title": "Array",
        "description": "asdf",
        "add_remove_controls": "append_only",
        "align_horizontal": False,
    }

    arr = Array(**di_arr)
    display(arr)

if __name__ == "__main__":
    di_arr = {
        "fn_add": fn_add,
        "max_items": 10,
        "title": "Array",
        "description": "asdf",
        "add_remove_controls": "append_only",
        "align_horizontal": False,
    }

    di = Dictionary(**di_arr)
    display(arr)

if __name__ == "__main__":
    from ipyautoui.demo_schemas import RootArray

    schema = RootArray.model_json_schema()
    ui = AutoArray.from_schema(schema)
    display(ui)

# +
if __name__ == "__main__":
    di_arr = {
        "items": None,
        "fn_add": fn_add,
        "max_items": 10,
        "title": "Array",
        "add_remove_controls": "append_only",
        "align_horizontal": False,
    }

    arr = Array(**di_arr)
    display(arr)

# TODO: add `Dictionary` that uses key not index as item ref
# -
if __name__ == "__main__":
    di_arr = {
        "value": [{"None": False}],
        "fn_add": fn_add,
        "max_items": 10,
        "title": "Array",
        "add_remove_controls": "append_only",
        "align_horizontal": True,
    }

    arr = Array(**di_arr)
    display(arr)

if __name__ == "__main__":
    arr.value = [{"None": False}, {"ads": True}]
