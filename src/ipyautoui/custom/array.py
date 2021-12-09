# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python [conda env:mf_base1] *
#     language: python
#     name: conda-env-mf_base1-xpython
# ---

# +
"""generic array object"""
# %run __init__.py
# %load_ext lab_black
import ipywidgets as widgets
import traitlets
import typing
import immutables
from dataclasses import dataclass
import uuid
import functools
import math
from ipyautoui.constants import ADD_BUTTON_KWARGS, REMOVE_BUTTON_KWARGS, BLANK_BUTTON_KWARGS, BUTTON_WIDTH_MIN, BUTTON_HEIGHT_MIN

frozenmap = (
    immutables.Map
)  # https://www.python.org/dev/peps/pep-0603/, https://github.com/MagicStack/immutables
BOX = frozenmap({True:widgets.HBox, False:widgets.VBox })
# -

TOGGLE_BUTTON_KWARGS = frozenmap(
    icon="",
    # style={"button_color":"white"},
    layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN},
    # disabled=True
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
    box.children = [box_buttons,box_label,box_item]
    
    box_item.children = [item]
    box_label.children = [widgets.HTML(f'<b>{label}</b>')]
    
    if show_add_remove:
        box_buttons.children = [add, remove]
        
    if append_only:
        [setattr(add, k, v) for k,v in BLANK_BUTTON_KWARGS.items()];
        
    return box



# +
@dataclass
class ArrayItem:
    index: int
    add: typing.Any
    remove: typing.Any
    guid: uuid.uuid4
    item: typing.Any  # this must be valid to be a child of a HBox or VBox and must have a "value" that can be watched
        


class Array(traitlets.HasTraits):
    """generic array. pass a list of items """
    value = traitlets.List()
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
        description=""
    ):
        
        self.array = [
            ArrayItem(
                index=n,
                add=widgets.Button(**ADD_BUTTON_KWARGS),
                remove=widgets.Button(**REMOVE_BUTTON_KWARGS),
                guid=uuid.uuid4(),
                item=i,
            )
            for n, i in enumerate(items)
        ]
        self.orient_rows = orient_rows
        self.toggle = toggle
        self.add_item = add_item
        self.watch_value = watch_value
        self.minlen = minlen #TODO: validation. must be > 1
        self.maxlen = maxlen
        self.append_only = append_only 
        self.show_add_remove=show_add_remove
        self.show_index = show_index
        self.title = title
        self.description = description
        
        self._init_form()
        self._init_controls()
        self.watch_value = watch_value
        self.zfill = 1
        if self.watch_value:
            self._update_value('change')
        
    @property
    def items(self):
        return [a.item for a in self.array]
    
    def row_from_array_item(self, array_item):
        if self.show_index:
            self.zfill = math.floor(math.log10(len(self.array)))
            label = str(array_item.index).zfill(self.zfill) + '. '
        else:
            label =""
        return make_row(array_item.item, array_item.add, array_item.remove, self.orient_rows, self.append_only, self.show_add_remove)
    
    def _update_index_labels(self):
        if self.show_index:
            self.zfill = math.floor(math.log10(len(self.array)))
            labels = [str(a.index).zfill(self.zfill) + '. ' for a in self.array]
            for r, l in zip(self.rows_box.children, labels):
                r.children[1].children[0].value = f'<b>{l}</b>'
            #[a.item]

    def _init_form(self):
        rows = [self.row_from_array_item(a) for a in self.array] 
        
        header = [widgets.HTML(f'<b>{self.title}</b>'), widgets.HTML(f'<i>{self.description}</i>')]
        if self.toggle:
            self.toggle_button = widgets.ToggleButton(icon = 'plus',layout={"width": BUTTON_WIDTH_MIN, "height": BUTTON_HEIGHT_MIN})
            header.insert(0,self.toggle_button)
        self.title_box = BOX[self.orient_rows](header)   
        self.rows_box = BOX[not self.orient_rows](rows)
        self.form_box = BOX[not self.orient_rows]([self.title_box])
        
        self._update_index_labels()
        
        if self.append_only: # disable remove bottom row and enable add button on bottom row to be used for append
            [setattr(self.rows_box.children[0].children[0].children[1], k, v) for k,v in BLANK_BUTTON_KWARGS.items()];
            [setattr(self.rows_box.children[0].children[0].children[0], k, v) for k,v in ADD_BUTTON_KWARGS.items()];

            
    def _init_controls(self):
        if self.toggle:
            self.toggle_button.observe(self._toggle_button, 'value')
        [self._init_row_controls(guid=r.guid) for r in self.array]
        
    def _toggle_button(self, change):
        if self.toggle_button.value:
            self.toggle_button.icon = 'minus'
            self.form_box.children = [self.title_box, self.rows_box]
        else:
            self.toggle_button.icon = 'plus'
            self.form_box.children = [self.title_box]

    def _init_row_controls(self, guid=None):
        if self.append_only:
            self.rows_box.children[0].children[0].children[0].on_click(self.append_row)
        else:
            self._get_add_widget(guid).on_click(
                functools.partial(self._add_rows, guid=guid)
            )
        self._get_remove_widget(guid).on_click(
            functools.partial(self._remove_rows, guid=guid)
        )
        if self.watch_value:
            self._get_item(guid).observe(self._update_value, names='value')
            
    def _update_value(self, onchange):
        self.value = [a.item.value for a in self.array]
        
    # -----------------------------------------------------    
    def _get_add_widget(self, guid):
        return [r.add for r in self.array if r.guid == guid][0]

    def _get_remove_widget(self, guid):
        return [r.remove for r in self.array if r.guid == guid][0]

    def _get_guid(self, index):
        return [r.guid for r in self.array if r.index == index][0]

    def _get_index(self, guid):
        return [r.index for r in self.array if r.guid == guid][0]
    
    def _get_item(self, guid):
         return [r.item for r in self.array if r.guid == guid][0]
    # TODO: combine these functions ^^^ -------------------
    
    def _sort_map(self):
        sort = sorted(self.array, key=lambda k: k.index)
        for n, s in enumerate(sort):
            s.index = n
        return sort

    def _remove_rows(self, onclick, guid=None):

        if len(self.array) <= 1:
            pass
        else:
            n = self._get_index(guid)
            # add item
            children = list(self.rows_box.children[0:n]) + list(
                self.rows_box.children[n + 1 :]
            ) 
            self.rows_box.children = children
            # update map
            self.array.pop(n)
            self.array = self._sort_map()
            if self.watch_value:
                self._update_value('change')
            if self.show_index:
                self._update_index_labels()

    def remove_row(self, guid=None):
        self._remove_rows("click", guid=guid)

    def remove_row_index(self, index):
        if index is None:
            raise ValueError(
                "index must be an integer less than the number of items in the array"
            )
        guid = self._get_guid(index) # +1
        self.remove_row(guid=guid)

    def _add_rows(self, onclick, guid=None):
        if len(self.array)>= self.maxlen:
            return None
        n = self._get_index(guid)
        # add item
        new_item = self.add_item()
        item = ArrayItem(
            index=n,
            add=widgets.Button(**ADD_BUTTON_KWARGS),
            remove=widgets.Button(**REMOVE_BUTTON_KWARGS),
            guid=uuid.uuid4(),
            item=new_item,
        )
        self.array.append(item)
        row = self.row_from_array_item(item)
        children = (
            list(self.rows_box.children[0 : n + 1])
            + [row]
            + list(self.rows_box.children[n + 1 :])
        )
        self.rows_box.children = children
        self.array = self._sort_map()  # update map
        self._init_row_controls(item.guid)  # init controls
        if self.watch_value:
            self._update_value('change')
        if self.show_index:
            self._update_index_labels()

    def add_row(self, guid=None):
        self._add_rows("click", guid=guid)

    def add_row_after_index(self, index=None):
        if index is None:
            raise ValueError(
                "index must be an integer less than the number of items in the array"
            )
        guid = self._get_guid(index)
        self.add_row(guid=guid)
        
    def append_row(self, action):
        self._add_rows('click', self.array[-1].guid)

    def display(self):
        display(self.form_box)

    def _ipython_display_(self):
        self.display()
        
class AutoArray:
    pass # TODO: create AutoArray class that works with the AutoUi class for arrays


# -

if __name__ == "__main__":
    import random
    from IPython.display import Markdown
    def get_di():
        words = ['a', 'AAA', 'AAAS', 'aardvark', 'Aarhus', 'Aaron', 'ABA', 'Ababa',
         'aback', 'abacus', 'abalone', 'abandon', 'abase']
        n = random.randint(0, len(words)-1)
        m =  random.randint(0, 1)
        _bool = {0:False,1:True}
        return {words[n]:_bool[m]}

    def add_item():
        return TestItem(di=get_di())

    class TestItem(widgets.HBox, traitlets.HasTraits):
        value= traitlets.Dict()
        def __init__(self, di: typing.Dict=get_di()):
            self.value = di
            self._init_form()
            self._init_controls()

        def _init_form(self):
            self._label = widgets.HTML(f"{list(self.value.keys())[0]}")
            self._bool = widgets.ToggleButton(list(self.value.values())[0])
            super().__init__(
                children=[self._bool, self._label],
            )

        def _init_controls(self):
            self._bool.observe(self._set_value, names='value')

        def _set_value(self, change):
            self.value = {self._label.value: self._bool.value}
            
    def test_make_row(item=add_item(), 
                      add=widgets.Button(**ADD_BUTTON_KWARGS), 
                      remove=widgets.Button(**REMOVE_BUTTON_KWARGS), 
                      orient_rows=True, 
                      append_only=False, 
                      show_add_remove=True, 
                      label="shituafs"):
        return make_row(item, add, remove, orient_rows, append_only, show_add_remove, label=label)
    
    display(Markdown("---")) 
    display(test_make_row())
    display(Markdown("---")) 
    
    array = Array(
        items=[add_item()],
        add_item=add_item,
        #orient_rows=False,
        #show_add_remove=False,
        maxlen=10, 
        append_only=True,
        show_index=True,
        #toggle=False,
        title='asdfasd',
        description='asfasdf'
    )
    display(array)
    display(Markdown("---")) 


