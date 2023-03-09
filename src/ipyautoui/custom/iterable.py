# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# TODO: support arrary / dictionary of length = 0
"""A generic iterable object.

Creates an array object where widgets can be added or removed. if the widgets have a "value" or "_value" trait the 
that trait is automatically watched / observed for 

Example:
    see below of simple example usage::
    
        import traitlets as tr
        import typing as ty

        import ipywidgets as w
        from IPython.display import Markdown

        from ipyautoui.custom.iterable import IterableItem, Array, Dictionary


        class TestItem(w.HBox, tr.HasTraits):
            value = tr.Dict()

            def __init__(self, di: ty.Dict):
                self.value = di
                self._init_form()
                self._init_controls()

            def _init_form(self):
                self._label = w.HTML(f"{list(self.value.keys())[0]}")
                self._bool = w.ToggleButton(list(self.value.values())[0])
                super().__init__(children=[self._bool, self._label])  # self._acc,

            def _init_controls(self):
                self._bool.observe(self._set_value, names="value")

            def _set_value(self, change):
                self.value = {self._label.value: self._bool.value}


        def fn_add():
            return TestItem(di={"Example": 1})


            "items": [fn_add()],
            "fn_add": fn_add,
            "maxlen": 10,
            "show_hash": "index",
            "toggle": True,
            "title": "Array",
            "add_remove_controls": "append_only",
            "orient_rows": False,
        }

        arr = Array(**di_arr)
        display(arr)

"""
# TODO: move iterable.py to root
# TODO: review: https://github.com/widgetti/react-ipywidgets - it could simplify the code required below.
# %run _dev_sys_path_append.py
# %run __init__.py
#
# %load_ext lab_black
import ipywidgets as w
import traitlets as tr
from traitlets import validate
import typing as ty
from IPython.display import display
from ipyautoui.basemodel import BaseModel
from pydantic import validator
import uuid
from uuid import UUID
import functools
from markdown import markdown
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

logger = logging.getLogger(__name__)
BOX = frozenmap({True: w.HBox, False: w.VBox})
TOGGLE_BUTTON_KWARGS = frozenmap(
    icon="",
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
)
# -

# +
class IterableItem(BaseModel):
    index: int
    key: ty.Union[UUID, str, int, float, bool] = None
    item: ty.Any = None
    add: ty.Any = None
    remove: ty.Any = None
    label: ty.Any = None
    orient_rows: bool = True
    row: ty.Any = None

    @validator("key", always=True)
    def _key(cls, v, values):
        """if no key given return uuid.uuid4()"""
        if v is None:
            return uuid.uuid4()
        else:
            return v

    @validator("add", always=True)
    def _add(cls, v, values):
        if v is None:
            return w.Button(layout=dict(BUTTON_MIN_SIZE))
        else:
            return v

    @validator("remove", always=True)
    def _remove(cls, v, values):
        if v is None:
            return w.Button(layout=dict(BUTTON_MIN_SIZE))
        else:
            return v

    @validator("label", always=True)
    def _label(cls, v, values):
        if v is None:
            return w.HTML("placeholder label")
        else:
            return v

    @validator("item", always=True)
    def _item(cls, v, values):
        if v is None:
            return w.ToggleButton(description="placeholder item")
        else:
            return v

    @validator("row", always=True)
    def _row(cls, v, values):
        ItemBox = BOX[values["orient_rows"]]
        if v is None:
            v = ItemBox(
                children=[
                    ItemBox(layout=w.Layout(flex="1 0 auto")),  # buttons
                    ItemBox(layout=w.Layout(flex="1 0 auto")),  # label
                    ItemBox(layout=w.Layout(flex="100%")),  # item
                ]
            )
            v.children[2].children = [values["item"]]
            return v
        else:
            return v


# # +
class Array(w.VBox):
    """generic iterable. pass a list of items"""

    # -----------------------------------------------------------------------------------
    _value = tr.List()
    _show_hash = tr.Unicode(allow_none=True)
    _add_remove_controls = tr.Unicode(allow_none=True)
    _sort_on = tr.Unicode(allow_none=True)

    @validate("show_hash")
    def _validate_show_hash(self, proposal):
        if proposal.value not in ["index", "key", None]:
            raise ValueError(
                f'{proposal} given. allowed values of show_hash are "index", "key" and None only'
            )
        return proposal

    @validate("_add_remove_controls")
    def _validate_add_remove_controls(self, proposal):
        # TODO: validator not getting called when this is changed once the class has been instantiated
        if proposal.value not in [
            "add_remove",
            "append_only",
            "remove_only",
            None,
        ]:  # TODO: put this in an enum...
            raise ValueError(
                f'{proposal} given. allowed values of _add_remove_controls are "add_remove", "append_only", "remove_only", None only'
            )
        return proposal

    @validate("_sort_on")
    def _validate_add_remove_controls(self, proposal):
        if proposal.value not in ["index", "key", None]:
            raise ValueError(
                f'{proposal} given. allowed values of sort_on are "index", "key" and None only'
            )
        return proposal

    def _update_value(self, onchange):
        self._value = [a.item.value for a in self.iterable]

    # -----------------------------------------------------------------------------------
    def __init__(
        self,
        value: ty.List = None,
        items: ty.List = None,
        toggle=False,
        title=None,
        fn_add: ty.Callable = lambda: display("add item"),
        fn_add_dialogue: ty.Callable = None,
        fn_remove: ty.Callable = lambda: display("remove item"),
        # fn_remove_dialogue: ty.Callable = lambda: display(f"are you sure you want to remove {item}"), #TODO
        watch_value: bool = True,
        minlen: int = 0,
        maxlen: int = 100,
        add_remove_controls: str = "add_remove",
        show_hash: str = "index",
        sort_on="index",
        orient_rows=True,
    ):
        if value is not None and items is not None:
            raise ValueError(
                '"value" (data only) and "items" (widget objects) cannot both be specified at input. you must specify one or the other.'
            )
        self.orient_rows = orient_rows
        self.minlen = minlen  # TODO: validation. must be > 1
        self.maxlen = maxlen
        self.fn_add = fn_add
        self.fn_add_dialogue = fn_add_dialogue
        self.fn_remove = fn_remove
        self.watch_value = watch_value
        self.zfill = 2
        value, items = self._init_value(value, items)
        self.iterable = self._init_iterable(items)
        self._init_form()
        self._toggle = toggle
        self.title = title
        self.add_remove_controls = add_remove_controls
        self.show_hash = show_hash
        self.sort_on = sort_on
        self._update_value("change")

    def _init_value(self, value, items):
        if value is None and items is None:
            items = self._init_items(items)
        elif value is None and items is not None:
            pass
        elif value is not None and items is None:
            items = [self.fn_add(v) for v in value]
        elif value is not None and items is not None:
            raise ValueError('either "items" or "value" must be None')
        else:
            raise ValueError("error with _init_value")
        return value, items

    def _init_iterable(self, items):
        return [
            IterableItem(
                index=n,
                key=uuid.uuid4(),
                item=i,
            )
            for n, i in enumerate(items)
        ]

    def _init_items(self, items):
        if items is None:
            return []
        else:
            return items

    @property
    def length(self):
        return len(self.iterable)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: ty.List):
        self.items = [self.fn_add() for v in value]
        for n, v in enumerate(value):
            self.items[n].value = v
        self._update_value("onchange")

    @property
    def items(self):
        return [i.item for i in self.iterable]

    @items.setter
    def items(self, value: ty.List):
        self.iterable = self._init_iterable(value)
        self._update_rows_box()
        self._update_rows()
        self._init_controls()

    @property
    def iterable_keys(self):
        return [i.key for i in self.iterable]

    @property
    def map_key_value(self):
        return {l.key: l.item.value for l in self.iterable}

    def _add_from_zero_display(self):
        if (
            self.length == 0
            and self.add_remove_controls != "remove_only"
            and self.add_remove_controls is not None
        ):
            self.rows_box.children = [self.add_from_zero]
        elif self.length == 0 and self.add_remove_controls == "remove_only":
            self.rows_box.children = []
        else:
            pass

    def _add_from_zero(self, on_click):
        self.add_row()

    def _init_form(self):
        # init containers
        super().__init__(
            layout=w.Layout(
                width="100%",
                display="flex",
                flex="flex-grow",
                # border="solid LightCyan 2px",
            )
        )  # main container
        self.rows_box = BOX[not self.orient_rows](
            layout=w.Layout(width="100%", display="flex", flex="flex-grow")
        )
        self.title_box = w.HBox(layout=w.Layout(display="flex", flex="flex-grow"))
        self.toggle_button = w.ToggleButton(icon="minus", layout=dict(BUTTON_MIN_SIZE))
        self.add_from_zero = w.Button(**ADD_BUTTON_KWARGS)
        # self._add_from_zero_display()
        self.toggle_button.value = True
        self._refresh_children()
        self._update_rows_box()

    def _refresh_children(self):
        self.children = [self.title_box, self.rows_box]

    # buttons ---------------
    def _style_zeroth_buttonbar(self):
        if self.add_remove_controls is None:
            pass
        elif self.add_remove_controls == "add_remove":
            [setattr(self.iterable[0].add, k, v) for k, v in ADD_BUTTON_KWARGS.items()]
            [
                setattr(self.iterable[0].remove, k, v)
                for k, v in REMOVE_BUTTON_KWARGS.items()
            ]
        elif self.add_remove_controls == "append_only":
            [setattr(self.iterable[0].add, k, v) for k, v in ADD_BUTTON_KWARGS.items()]
            [
                setattr(self.iterable[0].remove, k, v)
                for k, v in BLANK_BUTTON_KWARGS.items()
            ]
        elif self.add_remove_controls == "remove_only":
            [
                setattr(self.iterable[0].add, k, v)
                for k, v in BLANK_BUTTON_KWARGS.items()
            ]
            [
                setattr(self.iterable[0].remove, k, v)
                for k, v in REMOVE_BUTTON_KWARGS.items()
            ]
        else:
            pass

    def _style_nth_buttonbar(self, index):
        if self.add_remove_controls is None:
            pass
        elif self.add_remove_controls == "add_remove":
            [
                setattr(self.iterable[index].add, k, v)
                for k, v in ADD_BUTTON_KWARGS.items()
            ]
            [
                setattr(self.iterable[index].remove, k, v)
                for k, v in REMOVE_BUTTON_KWARGS.items()
            ]
        elif self.add_remove_controls == "append_only":
            [
                setattr(self.iterable[index].add, k, v)
                for k, v in BLANK_BUTTON_KWARGS.items()
            ]
            [
                setattr(self.iterable[index].remove, k, v)
                for k, v in REMOVE_BUTTON_KWARGS.items()
            ]
        elif self.add_remove_controls == "remove_only":
            [
                setattr(self.iterable[index].add, k, v)
                for k, v in BLANK_BUTTON_KWARGS.items()
            ]
            [
                setattr(self.iterable[index].remove, k, v)
                for k, v in REMOVE_BUTTON_KWARGS.items()
            ]
        else:
            pass

    def _style_buttonbar(self, index):
        if index == 0:
            self._style_zeroth_buttonbar()
        else:
            self._style_nth_buttonbar(index)

    def _update_buttonbar_box(self, index):
        if self.add_remove_controls is None:
            buttons_box = []
        else:
            self.iterable[index].add = w.Button(layout=dict(BUTTON_MIN_SIZE))
            self.iterable[index].remove = w.Button(layout=dict(BUTTON_MIN_SIZE))
            buttons_box = [self.iterable[index].add, self.iterable[index].remove]
        self.iterable[index].row.children[0].children = buttons_box

    def _update_buttonbar(self, index):
        self._update_buttonbar_box(index)
        self._style_buttonbar(index)

    def _update_buttonbars(self):
        [self._update_buttonbar(index) for index, item in enumerate(self.iterable)]

    def _update_label(self, index):
        if self.show_hash is None:
            labels_box = []
            self.iterable[index].row.children[1].children = labels_box
            return
        if self.show_hash == "index":
            label = str(self.iterable[index].index).zfill(self.zfill) + ". "
        elif self.show_hash == "key":
            label = str(self.iterable[index].key)
        else:
            label = ""
        self.iterable[index].label.value = f"<b>{label}</b>"
        labels_box = [self.iterable[index].label]
        self.iterable[index].row.children[1].children = labels_box

    def _update_labels(self):
        [self._update_label(index) for index, item in enumerate(self.iterable)]

    def _update_row(self, index):
        self._update_buttonbar(index)
        self._update_labels()

    def _update_rows(self):
        [self._update_row(index) for index, item in enumerate(self.iterable)]

    def _update_rows_box(self):
        self.rows_box.children = [i.row for i in self.iterable]
        self._add_from_zero_display()

    @property
    def add_remove_controls(self):
        if self._add_remove_controls is None:
            return None
        else:
            return self._add_remove_controls  # .value

    @add_remove_controls.setter
    def add_remove_controls(self, value: str):
        self._add_remove_controls = value
        self._update_buttonbars()
        self._init_controls()
        self._add_from_zero_display()

    @property
    def show_hash(self):
        return self._show_hash

    @show_hash.setter
    def show_hash(self, value: str):
        self._show_hash = value
        self._update_labels()

    @property
    def toggle(self):
        return self._toggle

    @toggle.setter
    def toggle(self, value: bool):
        self._toggle = value
        self.toggle_button.value = True
        self._update_header()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: ty.Union[str, None]):
        self._title = value
        if self.title is None:
            self.html_title = w.HTML(self.title)
        else:
            self.html_title = w.HTML(markdown(self.title))
        self._update_header()

    def _update_header(self):
        header = []
        if self.toggle:
            header.append(self.toggle_button)
        if self.title is not None:
            header.append(self.html_title)
        self.title_box.children = header

    def _toggle_button(self, change):
        if self.toggle_button.value:
            self.toggle_button.icon = "minus"
            self.children = [self.title_box, self.rows_box]
        else:
            self.toggle_button.icon = "plus"
            self.children = [self.title_box]

    def _init_row_controls(self, key=None):
        if self.add_remove_controls == "append_only":
            # self.iterable[0].add = w.Button(layout=dict(BUTTON_MIN_SIZE))
            self.iterable[0].add.on_click(self._add_row)
            # self._style_zeroth_buttonbar()
        else:
            self._get_attribute(key, "add").on_click(
                functools.partial(self._add_row, key=key)
            )
        self._get_attribute(key, "remove").on_click(
            functools.partial(self._remove_rows, key=key)
        )
        if self.watch_value:
            obj = self._get_attribute(key, "item")
            if "value" in obj.traits():
                obj.observe(self._update_value, names="value")
            elif "_value" in obj.traits():
                obj.observe(self._update_value, names="_value")
            else:
                logging.warning(
                    'array item must have either "value" or "_value" trait to be observed'
                )

    def _init_controls(self):
        self.add_from_zero.on_click(self._add_from_zero)
        self.toggle_button.observe(self._toggle_button, "value")
        [self._init_row_controls(key=i.key) for i in self.iterable]

    def _sort_iterable(self):
        if self.sort_on == "index":
            sort = sorted(self.iterable, key=lambda k: k.index)
        elif self.sort_on == "key":
            sort = sorted(self.iterable, key=lambda k: str(k.key))
        else:
            sort = self.iterable
        for n, s in enumerate(sort):
            s.index = n
        return sort

    def _get_attribute(self, key, get):
        return [getattr(r, get) for r in self.iterable if r.key == key][0]

    def _add_row(self, onclick, key=None):
        if self.fn_add_dialogue is None:
            self.add_row(key=key)
        else:
            out = w.Output()
            self.children = [self.title_box, out, self.rows_box]
            with out:
                display(self.fn_add_dialogue(cls=self))

    def add_row(self, key=None, new_key=None, add_kwargs=None, item=None):
        """add row to array after key. if key=None then append to end"""
        if self.maxlen is not None and len(self.iterable) >= self.maxlen:
            print("len(self.iterable) >= self.maxlen")
            return None

        if key is None:
            if len(self.iterable) == 0:
                index = 0
            else:
                key = self.iterable[-1].key
                index = self._get_attribute(key, "index")  # append
        else:
            index = self._get_attribute(key, "index")

        if new_key is not None:
            if new_key in [i.key for i in self.iterable]:
                print(f"{new_key} already exists in keys")
                return None

        if add_kwargs is None:
            add_kwargs = {}

        if item is None:
            new_item = self.fn_add(**add_kwargs)
        else:
            new_item = item

        item = IterableItem(
            index=index,
            key=new_key,
            item=new_item,
        )
        self.iterable.insert(index + 1, item)
        self.iterable = self._sort_iterable()  # update map
        index = self._get_attribute(item.key, "index")
        self._update_row(index)
        self._update_rows_box()
        self._init_row_controls(item.key)  # init controls
        if self.watch_value:
            self._update_value("change")
        self._add_from_zero_display()

    def _remove_rows(self, onclick, key=None):
        self.remove_row(key=key)

    def remove_row(self, key=None, remove_kwargs=None, fn_onremove=None):
        if len(self.iterable) <= 1:
            pass
        if key is None:
            print("key is None")
            key = self.iterable[-1].key
        if remove_kwargs is None:
            remove_kwargs = {}
        try:
            self.fn_remove(key=key, **remove_kwargs)
        except:
            self.fn_remove(**remove_kwargs)
        n = self._get_attribute(key, "index")
        if self.add_remove_controls == "append_only" and n == 0:
            pass
        else:
            n = self._get_attribute(key, "index")
            # print(f'n={str(n)}')
            self.iterable.pop(n)
            self.iterable = self._sort_iterable()
            if self.watch_value:
                self._update_value("change")
            self._update_rows_box()
            self._update_labels()

        self._add_from_zero_display()


class Dictionary(Array):
    value = tr.Dict()

    def _update_value(self, onchange):
        self.value = {a.key: a.item.value for a in self.iterable}

    # -----------------------------------------------------------------------------------
    def __init__(
        self,
        value: ty.Dict = None,
        items: ty.Dict = None,
        toggle=False,
        title=None,
        fn_add: ty.Callable = lambda: display("add item"),
        fn_add_dialogue: ty.Callable = None,
        fn_remove: ty.Callable = lambda: display("remove item"),
        watch_value: bool = True,
        minlen: int = 0,
        maxlen: int = None,
        add_remove_controls: str = "add_remove",
        show_hash: str = "index",
        sort_on="index",
        orient_rows=True,
    ):
        super().__init__(
            value,
            items,
            toggle=toggle,
            title=title,
            fn_add=fn_add,
            fn_add_dialogue=fn_add_dialogue,
            fn_remove=fn_remove,
            watch_value=watch_value,
            minlen=minlen,
            maxlen=maxlen,
            add_remove_controls=add_remove_controls,
            show_hash=show_hash,
            sort_on=sort_on,
            orient_rows=orient_rows,
        )

    def _init_items(self, items):
        if items is None:
            return {}
        else:
            return items

    @property
    def items(self):
        return {i.key: i.item for i in self.iterable}

    @items.setter
    def items(self, value: ty.List):
        self.iterable = self._init_iterable(value)
        self._update_rows_box()
        self._update_rows()
        self._init_controls()

    def _init_iterable(self, items):
        return [
            IterableItem(
                index=n,
                key=k,
                add=w.Button(**ADD_BUTTON_KWARGS),
                remove=w.Button(**REMOVE_BUTTON_KWARGS),
                item=v,
            )
            for n, (k, v) in enumerate(items.items())
        ]


def validate_items(sch_arr):
    if "items" not in sch_arr.keys():
        raise ValueError("items must be in schema keys")
    if any(_ in sch_arr["items"].keys() for _ in ["allOf", "anyOf", "oneOf", "not"]):
        raise ValueError(
            'items with: "allOf, anyOf, oneOf, not" keys currently not supported'
        )
    return sch_arr


class AutoArray(Array):
    _schema = tr.Dict()

    @validate("_schema")
    def _validate_schema(self, proposal):
        if "type" and "items" not in list(proposal.value.keys()):
            raise ValueError(f"not valid array schema")
        if proposal.value["type"] != "array":
            raise ValueError(f"not valid array schema")
        item = list(proposal.value["items"].keys())[0]
        if item in ["oneOf", "anyOf", "allOf", "not"]:
            raise ValueError(f"'{item}' not currently supported for array items")
        return proposal

    def __init__(
        self,
        schema: ty.Dict,
        value=None,
        toggle=False,
        fn_remove: ty.Callable = lambda: None,
        watch_value: bool = True,
        add_remove_controls: str = "add_remove",
        show_hash: str = "index",
        sort_on="index",
        orient_rows=True,
        fn_add_dialogue: ty.Callable = None,
    ):

        self.fn_add_dialogue = fn_add_dialogue
        self.fn_remove = fn_remove
        self._toggle = toggle
        self.schema = schema
        self.orient_rows = orient_rows
        self.watch_value = watch_value
        self.zfill = 2
        if value is not None:
            items = [self.fn_add() for v in value]
        elif "default" in self.schema.keys():
            items = [self.fn_add() for v in self.schema["default"]]
            # [display(i) for i in items]
        else:
            items = None
        items = self._init_items(items)
        self.iterable = self._init_iterable(items)
        self._init_form()

        self.add_remove_controls = add_remove_controls
        self.show_hash = show_hash
        self.sort_on = sort_on
        self._update_value("change")

    @property
    def schema(self):
        return self._schema["value"]

    @schema.setter
    def schema(self, value):

        self._schema = value
        self.caller = create_widget_caller(value)
        if "title" in self.schema.keys():
            self._title = self.schema["title"]
        else:
            self._title = None
        if "minItems" in self.schema.keys():
            self.minlen = self.schema["minItems"]
        else:
            self.minlen = 0
        if "maxItems" in self.schema.keys():
            self.maxlen = self.schema["maxItems"]
        else:
            self.maxlen = 100
        from ipyautoui import automapschema as aumap

        caller = aumap.map_widget(self.caller["items"])
        self.fn_add = functools.partial(aumap.widgetcaller, caller)


# -

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
        "add_remove_controls": "append_only",
        "orient_rows": False,
    }

    arr = Array(**di_arr)
    display(arr)

if __name__ == "__main__":
    from ipyautoui.test_schema import TestArrays
    from ipyautoui.autowidgets import create_widget_caller
    from ipyautoui.autoipywidget import AutoObject

    schema = TestArrays.schema()["properties"]["array_strings"]
    ui = AutoArray(schema)
    display(ui)

if __name__ == "__main__":
    from ipyautoui.test_schema import TestArrays
    from ipyautoui.autoipywidget import AutoObject
    from ipyautoui import AutoUi

    # TestArrays.schema()["properties"]  # ["array_strings"]

    schema = TestArrays.schema()
    ui = AutoUi(schema=TestArrays)
    display(ui)

if __name__ == "__main__":
    from ipyautoui.test_schema import TestArrays

    schema = TestArrays.schema()
    schema = schema["properties"]["array_strings1"]
    ui = AutoArray(schema)
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

if __name__ == "__main__":
    di_di = {
        "items": {"key": fn_add()},
        "fn_add": fn_add,
        "maxlen": 10,
        "show_hash": None,
        "toggle": True,
        "title": "Array",
        "add_remove_controls": "append_only",
        "orient_rows": True,
    }

    di = Dictionary(**di_di)
    display(di)

if __name__ == "__main__":
    di.add_remove_controls = "add_remove"
    di.show_hash = "index"

if __name__ == "__main__":
    di_di = {
        "items": None,
        "fn_add": fn_add,
        "maxlen": 10,
        "show_hash": None,
        "toggle": True,
        "title": "Array",
        "add_remove_controls": "append_only",
        "orient_rows": True,
    }

    di = Dictionary(**di_di)
    display(di)

if __name__ == "__main__":
    di.items = {"key1": fn_add(), "key2": fn_add()}
# -
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


if __name__ == "__main__":
    di_arr = {
        "value": [{"None": False}],
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

if __name__ == "__main__":
    arr.value = [{"None": False}, {"ads": True}, {"asdf": False}]
