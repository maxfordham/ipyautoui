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
# from pydantic.dataclasses import dataclass
from pydantic import validator, BaseModel
import uuid
from uuid import UUID
import functools
import math
from ipyautoui.constants import (
    ADD_BUTTON_KWARGS,
    REMOVE_BUTTON_KWARGS,
    BLANK_BUTTON_KWARGS,
    BUTTON_WIDTH_MIN,
    BUTTON_HEIGHT_MIN,
    BUTTON_MIN_SIZE
)
from markdown import markdown

frozenmap = (
    immutables.Map
)  # https://www.python.org/dev/peps/pep-0603/, https://github.com/MagicStack/immutables
BOX = frozenmap({True: widgets.HBox, False: widgets.VBox})
TOGGLE_BUTTON_KWARGS = frozenmap(
    icon="", layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
)


# +


class IterableItem(BaseModel):
    index: int
    key: typing.Union[UUID, str, int, float, bool]
    item: typing.Any  # this must be valid to be a child of a HBox or VBox and must have a "value" that can be watched
    add: typing.Any = None
    remove: typing.Any = None
    label: typing.Any = None
    
    @validator("add", always=True)
    def _add(cls, v, values):
        if v is None:
            return widgets.Button(layout=dict(BUTTON_MIN_SIZE))
        else:
            return v
    
    @validator("remove", always=True)
    def _remove(cls, v, values):
        if v is None:
            return widgets.Button(layout=dict(BUTTON_MIN_SIZE))
        else:
            return v
    
    @validator("label", always=True)
    def _label(cls, v, values):
        if v is None:
            return widgets.HTML()
        else:
            return v
    
def make_row(item, add, remove, orient_rows): #, orient_rows, append_only, show_add_remove, label=""
    """creates a generic row item. code below defined the structure
    
    Code:
        box_buttons = BOX[orient_rows]()
        box_label = BOX[orient_rows]()
        box_item = BOX[orient_rows]()
        box = BOX[orient_rows]()
        box.children = [box_buttons,box_label,box_item]
    """
    box_buttons = BOX[orient_rows]()
    box_label = BOX[orient_rows](layout=widgets.Layout(flex='1 0 auto' ))
    box_item = BOX[orient_rows](layout=widgets.Layout(width='100%'))
    box = BOX[orient_rows](layout=widgets.Layout(width='100%' ))
    
    box.children = [box_buttons, box_label, box_item]
    box_item.children = [item]
    
#     box_label.children = [widgets.HTML(f"<b>{label}</b>")]

#     if show_add_remove:
#         box_buttons.children = [add, remove]

#     if append_only:
#         [setattr(add, k, v) for k, v in BLANK_BUTTON_KWARGS.items()]

    return box



class Iterable(widgets.Box, traitlets.HasTraits):
    """generic iterable. pass a list of items"""
    # -----------------------------------------------------------------------------------
    value = traitlets.List()
    _show_hash = traitlets.Unicode()
    _show_add_remove  = traitlets.Unicode(allow_none=True)
    
    @validate("show_hash")
    def _validate_show_hash(self, proposal):
        if proposal.value not in ["index", "key", "False"]:
            raise ValueError(
                f'{proposal} given. allowed values of show_hash are "index", "key" and "False" only'
            )
        return proposal
    
    @validate("_show_add_remove")
    def _validate_show_add_remove(self, proposal):
        if proposal.value not in ["add_remove", "append_only", "remove_only", None]:
            raise ValueError(
                f'{proposal} given. allowed values of _show_add_remove are "add_remove", "append_only", "remove_only", None only'
            )
        return proposal
    
    def _update_value(self, onchange):
        self.value = [a.item.value for a in self.iterable]
        
    # -----------------------------------------------------------------------------------
    def __init__(
        self,
        items: typing.List,
        toggle=True,
        add_item: typing.Callable = lambda: display("add item"),
        watch_value: bool = True,
        minlen=1,
        maxlen=None,
        #append_only=False,
        show_add_remove='add_remove',
        show_hash="False",
        sort_on_index=True,
        title="",
        orient_rows = False
    ):
        self.orient_rows = orient_rows
        self.minlen = minlen  # TODO: validation. must be > 1
        self.maxlen = maxlen
        self.add_item = add_item
        self.watch_value = watch_value
        self.zfill = 2
        
        self.iterable = self._init_iterable(items)
        self._init_form()
        self._toggle = toggle
        self.title = title
        
        self.show_add_remove = show_add_remove
        self.show_hash = show_hash

        self._init_controls()
        self.sort_on_index = sort_on_index

    def _init_iterable(self, items):
        return [
            IterableItem(
                index=n,
                key=uuid.uuid4(),
                item=i,
            )
            for n, i in enumerate(items)
        ]
    
    def _init_form(self):
        # init containers
        super().__init__(layout=widgets.Layout(width='100%', display="flex", flex="flex-grow")) # main container
        self.rows_box = BOX[not self.orient_rows](layout=widgets.Layout(width='100%', display="flex", flex="flex-grow"))
        self.title_box = BOX[self.orient_rows](layout=widgets.Layout(display="flex", flex="flex-grow"))
        self.toggle_button = widgets.ToggleButton(icon="minus",layout=dict(BUTTON_MIN_SIZE))
        self.toggle_button.value = True
        rows = [self.row_from_iterable_item(a) for a in self.iterable]
        self.rows_box.children = rows
        self.children = [self.title_box, self.rows_box ]
        
        
    # buttons ---------------
    def style_zeroth_buttons(self):
        if self.show_add_remove is None:
            pass
        elif self.show_add_remove == "add_remove":
            [setattr(self.iterable[0].add, k, v)for k, v in ADD_BUTTON_KWARGS.items()]
            [setattr(self.iterable[0].remove, k, v)for k, v in BLANK_BUTTON_KWARGS.items()]
        elif self.show_add_remove == "append_only":
            [setattr(self.iterable[0].add, k, v)for k, v in ADD_BUTTON_KWARGS.items()]
            [setattr(self.iterable[0].remove, k, v)for k, v in BLANK_BUTTON_KWARGS.items()]
        elif self.show_add_remove == "remove_only":
            [setattr(self.iterable[0].add, k, v)for k, v in BLANK_BUTTON_KWARGS.items()]
            [setattr(self.iterable[0].remove, k, v)for k, v in BLANK_BUTTON_KWARGS.items()]
        else:
            pass
        
    def style_nth_buttons(self, index):
        if self.show_add_remove is None:
            pass
        elif self.show_add_remove == "add_remove":
            [setattr(self.iterable[index].add, k, v)for k, v in ADD_BUTTON_KWARGS.items()]
            [setattr(self.iterable[index].remove, k, v)for k, v in REMOVE_BUTTON_KWARGS.items()]
        elif self.show_add_remove == "append_only":
            [setattr(self.iterable[index].add, k, v)for k, v in BLANK_BUTTON_KWARGS.items()]
            [setattr(self.iterable[index].remove, k, v)for k, v in REMOVE_BUTTON_KWARGS.items()]
        elif self.show_add_remove == "remove_only":
            [setattr(self.iterable[index].add, k, v)for k, v in BLANK_BUTTON_KWARGS.items()]
            [setattr(self.iterable[index].remove, k, v)for k, v in REMOVE_BUTTON_KWARGS.items()]
        else:
            pass
        
    def update_buttons_box(self, n):
        if self.show_add_remove is None:
            buttons_box = []
        else:
            buttons_box = [self.iterable[n].add, self.iterable[n].remove]
        self.rows_box.children[n].children[0].children = buttons_box
        
    def style_iterable_item(self, iterable_item):
        index = self.iterable.index(iterable_item)
        if index == 0:
            self.style_zeroth_buttons()
        else:
            self.style_nth_buttons(index)
        self._update_label(iterable_item)
        self.update_buttons_box(index)
        
    def style_iterable_items(self):
        [self.style_iterable_item(i) for i in self.iterable];
            
    @property
    def show_add_remove(self):
        if self._show_add_remove is None:
            return None
        else:
            return self._show_add_remove.value
    
    @show_add_remove.setter
    def show_add_remove(self, value: str):
        self._show_add_remove = value
        self.style_iterable_items()
        [self.update_buttons_box(n) for n, item in enumerate(self.iterable)];
    # ---------------------        
    
        
    # labels ---------------
    def _update_label(self, iterable_item):
        index = self.iterable.index(iterable_item)
        if self.show_hash == "index":
            label = str(iterable_item.index).zfill(self.zfill) + ". "    
        elif self.show_hash == "key":
            label = str(iterable_item.key)
        else:
            label = ''
        self.iterable[index].label.value = f"<b>{label}</b>"
        if self.show_hash == "index" or self.show_hash == "key":
            self.rows_box.children[index].children[1].children = [self.iterable[index].label]
        else:
            self.rows_box.children[index].children[1].children = []

    def _update_labels(self):
        [self._update_label(i) for i in self.iterable]

    @property
    def show_hash(self):
        return self._show_hash
    
    @show_hash.setter
    def show_hash(self, value: str):
        self._show_hash = value
        self._update_labels()
    # ---------------------
    
    @property
    def items(self):
        return [a.item for a in self.iterable]

    def row_from_iterable_item(self, iterable_item):
        return make_row(
            iterable_item.item,
            iterable_item.add,
            iterable_item.remove,
            self.orient_rows
        )
    
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
    def title(self, value: typing.Union[str, None]):
        self._title = value
        if self.title is None:
            self.html_title = widgets.HTML(self.title)
        else:
            self.html_title = widgets.HTML(markdown(self.title))
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

    def _init_controls(self):
        self.toggle_button.observe(self._toggle_button, "value")
        [self._init_row_controls(key=r.key) for r in self.iterable]
        if self.watch_value:
            self._update_value("change")

    def _init_row_controls(self, key=None):
        if self.show_add_remove  == "append_only":
            self.iterable[0].add.on_click(self._add_row)
        else:
            self._get_attribute(key, 'add').on_click(
                functools.partial(self._add_row, key=key)
            )
        self._get_attribute(key, 'remove').on_click(
            functools.partial(self._remove_rows, key=key)
        )
        if self.watch_value:
            self._get_attribute(key, 'item').observe(self._update_value, names="value")

    def _get_attribute(self, key, get):
        return [getattr(r, get) for r in self.iterable if r.key == key][0]

    def _get_key(self, index):
        return [r.key for r in self.iterable if r.index == index][0]

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
            n = self._get_attribute(key, 'index')
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
            self.show_hash = self.show_hash 
            if n == 0:
                self.style_iterable_item(self.iterable[n])

    def remove_row(self, key=None):
        if key is None: 
            key = self.iterable[-1].key
        self._remove_rows("click", key=key)

    def remove_row_index(self, index):
        if index is None:
            raise ValueError(
                "index must be an integer less than the number of items in the iterable"
            )
        key = self._get_key(index)
        self.remove_row(key=key)

    def _add_row(self, onclick, key=None):
        self.add_row(key=key)

    def add_row(self, key=None, new_key=None, add_kwargs=None):
        """add row to array. if key=None then append to end"""
        if len(self.iterable) >= self.maxlen:
            print('len(self.iterable) >= self.maxlen')
            return None
        
        if add_kwargs is None:
            add_kwargs = {}
        
        if key is None: 
            key = self.iterable[-1].key
            #print(f'key == {key}')
            
        if new_key is None:
            new_key = uuid.uuid4()
            
        if new_key in [i.key for i in self.iterable]:
            print(f'{new_key} already exists in keys')
            return None
        
        # add item
        n = self._get_attribute(key, 'index')
        new_item = self.add_item(**add_kwargs)
        item = IterableItem(
            index=n,
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
        self.style_iterable_item(item)
        
    def add_row_after_index(self, index=None):
        if index is None:
            raise ValueError(
                "index must be an integer less than the number of items in the iterable"
            )
        key = self._get_key(index)
        self.add_row(key=key)

# +


class AutoIterable:
    pass  # TODO: create AutoIterable class that works with the AutoUi class for iterables


class VArray(Iterable):
    # ref: https://github.com/jupyter-widgets/ipywidgets/blob/master/python/ipywidgets/ipywidgets/widgets/widget_box.py
    _model_name = traitlets.Unicode('VBoxModel').tag(sync=True) 
    _view_name = traitlets.Unicode('VBoxView').tag(sync=True)
    def __init__(
        self,
        items: typing.List,
        toggle=True,
        #orient_rows: bool = True,
        add_item: typing.Callable = lambda: display("add item"),
        watch_value: bool = True,
        minlen=1,
        maxlen=None,
        #append_only=False,
        show_add_remove='append_only',
        show_index=False,
        title="",
    ):
        if show_index:
            s_hash = 'index'
        else:
            s_hash = 'False'
        super().__init__(items,
            toggle=toggle,
            orient_rows=True,
            add_item=add_item,
            watch_value=watch_value,
            minlen=minlen,
            maxlen=maxlen,
            #append_only=append_only,
            show_add_remove=show_add_remove,
            show_hash=s_hash,
            title=title,
    )
        
class HArray(Iterable):
    # ref: https://github.com/jupyter-widgets/ipywidgets/blob/master/python/ipywidgets/ipywidgets/widgets/widget_box.py
    _model_name = traitlets.Unicode('HBoxModel').tag(sync=True) 
    _view_name = traitlets.Unicode('HBoxView').tag(sync=True)
    def __init__(
        self,
        items: typing.List,
        toggle=True,
        #orient_rows: bool = True,
        add_item: typing.Callable = lambda: display("add item"),
        watch_value: bool = True,
        minlen=1,
        maxlen=None,
        #append_only=False,
        show_add_remove='append_only',
        show_index=False,
        title="",
    ):
        if show_index:
            s_hash = 'index'
        else:
            s_hash = 'False'
        super().__init__(items,
            toggle=toggle,
            orient_rows=False,
            add_item=add_item,
            watch_value=watch_value,
            minlen=minlen,
            maxlen=maxlen,
            #append_only=append_only,
            show_add_remove=show_add_remove,
            show_hash=s_hash,
            title=title,
    )
        
        
class VDictionary(Iterable):
    value = traitlets.Dict()
    # ref: https://github.com/jupyter-widgets/ipywidgets/blob/master/python/ipywidgets/ipywidgets/widgets/widget_box.py
    _model_name = traitlets.Unicode('VBoxModel').tag(sync=True) 
    _view_name = traitlets.Unicode('VBoxView').tag(sync=True)
    def __init__(
        self,
        items: typing.Dict,
        toggle=True,
        #orient_rows: bool = True,
        add_item: typing.Callable = lambda: display("add item"),
        watch_value: bool = True,
        minlen=1,
        maxlen=None,
        #append_only=False,
        show_add_remove='append_only',
        show_key=False,
        title="",
    ):
        if show_key:
            s_hash = 'key'
        else:
            s_hash = 'False'
        super().__init__(items,
            toggle=toggle,
            orient_rows=True,
            add_item=add_item,
            watch_value=watch_value,
            minlen=minlen,
            maxlen=maxlen,
            #append_only=append_only,
            show_add_remove=show_add_remove,
            show_hash=s_hash,
            title=title,
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
    
class HDictionary(Iterable):
    value = traitlets.Dict()
    # ref: https://github.com/jupyter-widgets/ipywidgets/blob/master/python/ipywidgets/ipywidgets/widgets/widget_box.py
    _model_name = traitlets.Unicode('HBoxModel').tag(sync=True) 
    _view_name = traitlets.Unicode('HBoxView').tag(sync=True)
    def __init__(
        self,
        items: typing.Dict,
        toggle=True,
        add_item: typing.Callable = lambda: display("add item"),
        watch_value: bool = True,
        minlen=1,
        maxlen=None,
        #append_only=False,
        show_add_remove='append_only',
        show_key=False,
        title="",
    ):
        if show_key:
            s_hash = 'key'
        else:
            s_hash = 'False'
        super().__init__(items,
            toggle=toggle,
            orient_rows=False,
            add_item=add_item,
            watch_value=watch_value,
            minlen=minlen,
            maxlen=maxlen,
            #append_only=append_only,
            show_add_remove=show_add_remove,
            show_hash=s_hash,
            title=title,
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
            #self._acc = widgets.Accordion([self._label,self._bool ])
            super().__init__(children=[self._bool, self._label])#self._acc, 

        def _init_controls(self):
            self._bool.observe(self._set_value, names="value")

        def _set_value(self, change):
            self.value = {self._label.value: self._bool.value}

    def test_make_row(
        item=add_item(),
        add=widgets.Button(**ADD_BUTTON_KWARGS),
        remove=widgets.Button(**REMOVE_BUTTON_KWARGS),
        orient_rows=True,
    ):
        return make_row(
            item, add, remove, orient_rows#, append_only, show_add_remove, label=label
        )

    display(Markdown("---"))
    display(test_make_row())
    display(Markdown("---"))
    
    di_h_arr = {
        'items':[add_item()],
        'add_item':add_item,
        'maxlen':10,
        'show_index':False,
        'toggle':False,
        'title':'Array',
    }
    di_v_arr = di_h_arr.copy()
    di_v_arr['show_index'] = True
    di_v_arr['toggle'] = True
    harr = HArray(**di_h_arr)
    varr = VArray(**di_v_arr)
    
    di_h_di = {
        'items':{'key':add_item()},
        'add_item':add_item,
        'maxlen':10,
        'show_key':False,
        'toggle':False,
        'title':None,
    }
    di_v_di = di_h_di.copy()
    di_v_di['show_key'] = True
    di_v_di['toggle'] = True
    hdi = HDictionary(**di_v_di)
    vdi = VDictionary(**di_v_di)
    
    display(Markdown("## Horizonantal Array"))
    display(harr)
    display(Markdown("---"))
    
    display(Markdown("## Vertical Array"))
    display(varr)
    display(Markdown("---"))
    
    display(Markdown("## Horizonantal Dictionary"))
    display(hdi)
    display(Markdown("---"))
    
    display(Markdown("## Vertical Dictionary"))
    display(vdi)
    display(Markdown("---"))

harr.toggle = False
harr.show_add_remove = None

w.value


