# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.3
#   kernelspec:
#     display_name: Python [conda env:ipyautoui]
#     language: python
#     name: conda-env-ipyautoui-xpython
# ---

"""generic iterable object."""
# %run __init__.py
# %load_ext lab_black

# +
import ipywidgets as widgets
import traitlets
from traitlets import validate
import typing
import immutables
from dataclasses import dataclass
import uuid
import functools
import math
from ipyautoui.constants import (
    ADD_BUTTON_KWARGS,
    REMOVE_BUTTON_KWARGS,
    BLANK_BUTTON_KWARGS,
    BUTTON_WIDTH_MIN,
    BUTTON_HEIGHT_MIN,
)

frozenmap = (
    immutables.Map
)  # https://www.python.org/dev/peps/pep-0603/, https://github.com/MagicStack/immutables
BOX = frozenmap({True: widgets.HBox, False: widgets.VBox})
TOGGLE_BUTTON_KWARGS = frozenmap(
    icon="", layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
)


def make_row(item, add, remove, orient_rows, append_only, show_add_remove, label=""):
    """creates a generic row item. code below defined the structure
    
    Code:
        box_buttons = BOX[orient_rows]()
        box_label = BOX[orient_rows]()
        box_item = BOX[orient_rows]()
        box = BOX[orient_rows]()
        box.children = [box_buttons,box_label,box_item]
    """
    box_buttons = BOX[orient_rows]()
    box_label = BOX[orient_rows]()
    box_item = BOX[orient_rows]()
    box = BOX[orient_rows]()
    box.children = [box_buttons, box_label, box_item]

    box_item.children = [item]
    box_label.children = [widgets.HTML(f"<b>{label}</b>")]

    if show_add_remove:
        box_buttons.children = [add, remove]

    if append_only:
        [setattr(add, k, v) for k, v in BLANK_BUTTON_KWARGS.items()]

    return box


@dataclass
class IterableItem:
    index: int
    key: typing.Union[uuid.uuid4, str, int, float, bool]
    add: typing.Any
    remove: typing.Any
    item: typing.Any  # this must be valid to be a child of a HBox or VBox and must have a "value" that can be watched


class Iterable(traitlets.HasTraits):
    """generic iterable. pass a list of items """

    value = traitlets.List()
    show_hash = traitlets.Unicode()

    @validate("show_hash")
    def _validate_show_hash(self, proposal):
        if proposal.value not in ["index", "key", "False"]:
            raise ValueError(
                f'{proposal} given. allowed values of show_hash are "index", "key" and "False" only'
            )
        return proposal
    
    def _update_value(self, onchange):
        self.value = [a.item.value for a in self.iterable]

    def __init__(
        self,
        items: typing.List,
        toggle=True,
        orient_rows: bool = True,
        add_item: typing.Callable = lambda: display("add item"),
        watch_value: bool = True,
        minlen=1,
        maxlen=None,
        append_only=False,
        show_add_remove=True,
        show_hash="False",
        sort_on_index=True,
        title="",
        description="",
    ):

        self.iterable = self._init_iterable(items)
        self.orient_rows = orient_rows
        self.toggle = toggle
        self.add_item = add_item
        self.watch_value = watch_value
        self.minlen = minlen  # TODO: validation. must be > 1
        self.maxlen = maxlen
        self.append_only = append_only
        self.show_add_remove = show_add_remove
        self.show_hash = show_hash
        self.title = title
        self.description = description

        self._init_form()
        self._init_controls()
        self.watch_value = watch_value
        self.sort_on_index = sort_on_index
        self.zfill = 1
        
    def _init_iterable(self, items):
        return [
            IterableItem(
                index=n,
                key=uuid.uuid4(),
                add=widgets.Button(**ADD_BUTTON_KWARGS),
                remove=widgets.Button(**REMOVE_BUTTON_KWARGS),
                item=i,
            )
            for n, i in enumerate(items)
        ]

    # labels ------
    def _hash_labels(self):
        if self.show_hash.value == "index":
            self._update_index_labels()
        elif self.show_hash.value == "key":
            self._update_key_labels()
        else:
            pass

    def _update_index_labels(self):
        self.zfill = math.floor(math.log10(len(self.iterable)))
        labels = [str(a.index).zfill(self.zfill) + ". " for a in self.iterable]
        for r, l in zip(list(self.rows_box.children), labels):
            r.children[1].children[0].value = f"<b>{l}</b>"

    def _update_key_labels(self):
        for r, i in zip(self.rows_box.children, self.iterable):
            r.children[1].children[0].value = f"<b>{i.key}</b>"
    # ------------
    
    
    @property
    def items(self):
        return [a.item for a in self.iterable]

    def row_from_iterable_item(self, iterable_item):
        self._hash_labels()
        return make_row(
            iterable_item.item,
            iterable_item.add,
            iterable_item.remove,
            self.orient_rows,
            self.append_only,
            self.show_add_remove,
        )

    def _init_form(self):
        self.form_box = BOX[not self.orient_rows]()  # main
        self.rows_box = BOX[not self.orient_rows]()
        self.title_box = BOX[self.orient_rows]()

        rows = [self.row_from_iterable_item(a) for a in self.iterable]
        header = [
            widgets.HTML(f"<b>{self.title}</b>"),
            widgets.HTML(f"<i>{self.description}</i>"),
        ]
        self.title_box.children = header
        self.rows_box.children = rows

        if self.toggle:
            self.toggle_button = widgets.ToggleButton(
                icon="plus",
                layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
            )
            header.insert(0, self.toggle_button)
            self.form_box.children = [self.title_box]
        else:
            self.form_box.children = [self.title_box, self.rows_box]
        self._hash_labels()

        # if self.append_only: 
        # disable remove bottom row and enable add button on bottom row to be used for append
        if self.show_add_remove and self.append_only: 
            [
                setattr(self.rows_box.children[0].children[0].children[1], k, v)
                for k, v in BLANK_BUTTON_KWARGS.items()
            ]
            [
                setattr(self.rows_box.children[0].children[0].children[0], k, v)
                for k, v in ADD_BUTTON_KWARGS.items()
            ]

    def _init_controls(self):
        if self.toggle:
            self.toggle_button.observe(self._toggle_button, "value")
        [self._init_row_controls(key=r.key) for r in self.iterable]
        if self.watch_value:
            self._update_value("change")

    def _toggle_button(self, change):
        if self.toggle_button.value:
            self.toggle_button.icon = "minus"
            self.form_box.children = [self.title_box, self.rows_box]
        else:
            self.toggle_button.icon = "plus"
            self.form_box.children = [self.title_box]

    def _init_row_controls(self, key=None):
        if self.show_add_remove and self.append_only:
            self.rows_box.children[0].children[0].children[0].on_click(self.add_row)
        else:
            self._get_attribute(key, 'add').on_click(
                functools.partial(self._add_rows, key=key)
            )
        self._get_remove_widget(key).on_click(
            functools.partial(self._remove_rows, key=key)
        )
        if self.watch_value:
            self._get_item(key).observe(self._update_value, names="value")

    # -----------------------------------------------------
    def _get_attribute(self, key, get):
        return [getattr(r, get) for r in self.iterable if r.key == key][0]
    
    def _get_add_widget(self, key):
        return [r.add for r in self.iterable if r.key == key][0]

    def _get_remove_widget(self, key):
        return [r.remove for r in self.iterable if r.key == key][0]

    def _get_key(self, index):
        return [r.key for r in self.iterable if r.index == index][0]

    def _get_index(self, key):
        return [r.index for r in self.iterable if r.key == key][0]

    def _get_item(self, key):
        return [r.item for r in self.iterable if r.key == key][0]

    # TODO: combine these functions ^^^ -------------------

    def _sort_map(self):
        if self.sort_on_index:
            sort = sorted(self.iterable, key=lambda k: k.index)
        else:
            sort = sorted(self.iterable, key=lambda k: k.key)
        for n, s in enumerate(sort):
            s.index = n
        return sort

    def _remove_rows(self, onclick, key=None):

        if len(self.iterable) <= 1:
            pass
        else:
            n = self._get_index(key)
            # add item
            children = list(self.rows_box.children[0:n]) + list(
                self.rows_box.children[n + 1 :]
            )
            self.rows_box.children = children
            # update map
            self.iterable.pop(n)
            self.iterable = self._sort_map()
            if self.watch_value:
                self._update_value("change")
            self._hash_labels()

    def remove_row(self, key=None):
        self._remove_rows("click", key=key)

    def remove_row_index(self, index):
        if index is None:
            raise ValueError(
                "index must be an integer less than the number of items in the iterable"
            )
        key = self._get_key(index)
        self.remove_row(key=key)

    def _add_rows(self, onclick, key=None):
        self.add_row(key=key)

    def add_row(self, key=None, new_key=None, add_kwargs=None):
        """add row to array. if key=None then append to end"""
        if len(self.iterable) >= self.maxlen:
            return None
        
        if add_kwargs is None:
            add_kwargs = {}
        
        if key is None: 
            key = self.iterable[-1].key
            
        if new_key is None:
            new_key = uuid.uuid4()
            
        if new_key in [i.key for i in self.iterable]:
            print(f'{new_key} already exists in keys')
            return None
        # add item
        n = self._get_index(key)
        new_item = self.add_item(**add_kwargs)
        item = IterableItem(
            index=n,
            add=widgets.Button(**ADD_BUTTON_KWARGS),
            remove=widgets.Button(**REMOVE_BUTTON_KWARGS),
            key=new_key,
            item=new_item,
        )
        self.iterable.append(item)
        row = self.row_from_iterable_item(item)
        children = (
            list(self.rows_box.children[0 : n + 1])
            + [row]
            + list(self.rows_box.children[n + 1 :])
        )
        self.rows_box.children = children
        self.iterable = self._sort_map()  # update map
        self._init_row_controls(item.key)  # init controls
        if self.watch_value:
            self._update_value("change")
        self._hash_labels()
        

    def add_row_after_index(self, index=None):
        if index is None:
            raise ValueError(
                "index must be an integer less than the number of items in the iterable"
            )
        key = self._get_key(index)
        self.add_row(key=key)

    def display(self):
        display(self.form_box)

    def _ipython_display_(self):
        self.display()


class AutoIterable:
    pass  # TODO: create AutoIterable class that works with the AutoUi class for iterables


class Array(Iterable):
    def __init__(
        self,
        items: typing.List,
        toggle=True,
        orient_rows: bool = True,
        add_item: typing.Callable = lambda: display("add item"),
        watch_value: bool = True,
        minlen=1,
        maxlen=None,
        append_only=False,
        show_add_remove=True,
        show_index=False,
        title="",
        description="",
    ):
        if show_index:
            show_hash = 'index'
        else:
            show_hash = 'False'
        super().__init__(items,
            toggle=toggle,
            orient_rows=orient_rows,
            add_item=add_item,
            watch_value=watch_value,
            minlen=minlen,
            maxlen=maxlen,
            append_only=append_only,
            show_add_remove=show_add_remove,
            show_hash=show_hash,
            title=title,
            description=description,
    )
        
        
class Dictionary(Iterable):
    value = traitlets.Dict()
    def __init__(
        self,
        items: typing.Dict,
        toggle=True,
        orient_rows: bool = True,
        add_item: typing.Callable = lambda: display("add item"),
        watch_value: bool = True,
        minlen=1,
        maxlen=None,
        append_only=False,
        show_add_remove=True,
        show_key=False,
        title="",
        description="",
    ):
        if show_key:
            show_hash = 'key'
        else:
            show_hash = 'False'
        super().__init__(items,
            toggle=toggle,
            orient_rows=orient_rows,
            add_item=add_item,
            watch_value=watch_value,
            minlen=minlen,
            maxlen=maxlen,
            append_only=append_only,
            show_add_remove=show_add_remove,
            show_hash=show_hash,
            title=title,
            description=description,
    )
        
    def _update_value(self, onchange):
        self.value = {a.key: a.item.value for a in self.iterable}
        
    @property
    def items(self):
        return {a.key: a.item for a in self.iterable}
    
    def _init_iterable(self, items):
        return [
            IterableItem(
                index=n,
                key=k,
                add=widgets.Button(**ADD_BUTTON_KWARGS),
                remove=widgets.Button(**REMOVE_BUTTON_KWARGS),
                item=v,
            )
            for n, (k, v) in enumerate(items.items())
        ]


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

    def add_item():
        return TestItem(di=get_di())

    class TestItem(widgets.HBox, traitlets.HasTraits):
        value = traitlets.Dict()

        def __init__(self, di: typing.Dict = get_di()):
            self.value = di
            self._init_form()
            self._init_controls()

        def _init_form(self):
            self._label = widgets.HTML(f"{list(self.value.keys())[0]}")
            self._bool = widgets.ToggleButton(list(self.value.values())[0])
            super().__init__(children=[self._bool, self._label],)

        def _init_controls(self):
            self._bool.observe(self._set_value, names="value")

        def _set_value(self, change):
            self.value = {self._label.value: self._bool.value}

    def test_make_row(
        item=add_item(),
        add=widgets.Button(**ADD_BUTTON_KWARGS),
        remove=widgets.Button(**REMOVE_BUTTON_KWARGS),
        orient_rows=True,
        append_only=False,
        show_add_remove=True,
        label="shituafs",
    ):
        return make_row(
            item, add, remove, orient_rows, append_only, show_add_remove, label=label
        )

    display(Markdown("---"))
    display(test_make_row())
    display(Markdown("---"))

    arr = Array(
        items=[add_item()],
        add_item=add_item,
        # orient_rows=False,
        #show_add_remove=False,
        maxlen=10,
        #append_only=True,
        show_index=True,
        toggle=False,
        title="asdfasd",
        description="asfasdf",
    )
    display(arr)
    display(Markdown("---"))
    
    di = Dictionary(
        items={'key':add_item()},#[add_item()],#{'key':add_item()},
        add_item=add_item,
        # orient_rows=False,
        #show_add_remove=False,
        maxlen=10,
        #append_only=True,
        show_key=False,
        toggle=False,
        title="asdfasd",
        description="asfasdf",
    )
    display(di)
    display(Markdown("---"))


