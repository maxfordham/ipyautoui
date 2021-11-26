# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
import sys

from numpy import disp, dsplit
sys.path.append('/mnt/c/engDev/git_extrnl/pydantic')
# %run __init__.py
import pathlib
import functools
import pandas as pd
import ipywidgets as widgets
from IPython.display import display
from datetime import datetime, date
from dataclasses import dataclass

from pydantic import BaseModel, Field, conint, constr
from pydantic.color import Color
import traitlets
import typing
from enum import Enum

import ipyautoui
from ipyautoui._utils import obj_from_string

DI_JSONSCHEMA_WIDGET_MAP = {
    'minimum': 'min',
    'maximum': 'max',
    'enum': 'options',
    'default': 'value',
    'description': 'autoui_label'
}
#  ^ this is how the json-schema names map to ipywidgets.

# +
class Gender(str, Enum):
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'
    
class NestedObject(BaseModel):
    string1: str = Field(default='adsf', description='a description about my string')
    int_slider1: conint(ge=0,le=3) =2
    int_text1: int = 1

class TestAutoLogic(BaseModel):
    """<br>this is a test UI form to demonstrate how pydantic class can be used to generate an ipywidget input form"""
    string: str = Field(default='adsf', description='a description about my string')
    int_slider: conint(ge=0,le=3) =2
    int_text: int = 1
    int_range_slider: typing.Tuple[int,int] = Field(default=(0,3),ge=0,le=4)   # check
    float_slider: float = Field(default=2.2, ge=0,le=3) 
    float_text: float =2.2
    float_range_slider: typing.Tuple[float,float] = Field(default=(0,2.2), ge=0,le=3.5)
    checkbox: bool = True
    dropdown: Gender = None
    dropdown_simple: str = Field(default ='asd', enum=['asd','asdf'])
    combobox: str = Field(default ='asd', enum=['asd','asdf'], autoui="<class 'ipywidgets.widgets.widget_string.Combobox'>")
    # selection_range_slider
    select_multiple: typing.List[Gender] = Field(default =['male','female']) # TODO: make this work. requires handling the "anyOf" JSON link
    select_multiple_simple: typing.List[str] = Field(default =['male','female'], enum=['male','female', 'other', 'not_given'])
    text: constr(min_length=0, max_length=20) = 'short text'
    text_area: constr(min_length=0, max_length=200)  = 'long text ' * 50
    date_picker: date = date.today()
    color_picker: Color = 'red'
    file_chooser: pathlib.Path = pathlib.Path('.')
    array: typing.typing.List[str] = Field(default=[], max_items=5)
    # file_upload # TODO: how best to implement this? could auto-save to another location...
    # model_run_name # TODO: try and implement this as a test for custom widgets...
    datagrid: str = Field(default=pd.DataFrame.from_dict({'test':[0,1],'df':[1,2]}).to_json(), format="DataFrame")
    nested: NestedObject = Field(default=None)
    
#  -- ATTACH DEFINITIONS TO PROPERTIES ----------------------
def recursive_search(sch:typing.Dict, li: typing.List) ->typing.Dict:
    """searches down schema tree to retrieve definitions

    Args:
        sch (typing.Dict): json schema made from pydantic   
        li (typing.List): list of keys to search down tree

    Returns:
        typing.Dict: definition retrieved from schema
    """
    if len(li) > 1:
        f = li[0]
        li_tmp = li[1:]
        sch_tmp = sch[f]
        return recursive_search(sch_tmp, li_tmp)
    else:
        return sch[li[0]]

def update_property_from_definition(sch: typing.Dict, item: typing.Dict, key:typing.Any) -> typing.Dict:
    """attaches definition back to properties in schema

    Args:
        sch (typing.Dict): json schema
        item (typing.Dict): definition item
        key (typing.Any): what to search for (#ref)

    Returns:
        typing.Dict: sch
    """ 
    k = list(item.keys())[0]
    v = list(item.values())[0]
    
    li_filt = v[key].split('/')[1:]
    definition = recursive_search(sch, li_filt)

    di_new = {}
    for k_, v_ in item.items():
        di_new[k_] = definition
    
    sch['properties'][k] = di_new[k]
    return sch

def update_property_definitions(sch: typing.Dict, key: str):
    """attaches all definitions back to properties. 
    TODO - currently only looks at the first level!

    Args:
        sch (typing.Dict): [description]
        key (str): [description]

    Returns:
        [type]: [description]
    """
    li_definitions = [{k:v} for k,v in sch['properties'].items() if key in v]
    for l in li_definitions:
         sch = update_property_from_definition(sch, l, key)
    return sch
#  ----------------------------------------------------------

#  -- CHANGE JSON-SCHEMA KEYS TO IPYWIDGET KEYS -------------

def update_key(key, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    if key in di_map.keys():
        return di_map[key]
    else:
        return key
    
def update_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    return {update_key(k, di_map): v for k, v in di.items()}

def add_description_field(di):
    for k,v in di.items():
        if 'description' not in v:
            v['description'] =''
        t=v['title']
        d=v['description']
        v['description'] = f"<b>{t}</b>, <i>{d}</i>"
    return di

def rename_schema_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    di = add_description_field(di)
    rename = {k:update_keys(v, di_map) for k, v in di.items()}
    return rename

def call_rename_schema_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP, rename_keys=True):
    if rename_keys:
        return rename_schema_keys(di, di_map=di_map)
    else:
        return di
#  ----------------------------------------------------------

#  -- HELPER FUNCTIONS --------------------------------------
def get_type(pr, typ='string'):
    return {k:v for k,v in pr.items() if v['type'] ==typ}

def get_format(pr, typ='date'):
    pr = {k:v for k,v in pr.items() if 'format' in v}
    return {k:v for k,v in pr.items() if v['format'] ==typ}

def get_range(pr, typ='integer'):
    array = get_type(pr, typ='array')
    array = {k:v for k,v in array.items() if len(v['items']) ==2}
    tmp = {}
    for k,v in array.items():
        tmp[k] = v
        for i in v['items']:
            if 'minimum' not in i and 'maximum' not in i:
                tmp = {}
    if len(tmp)==0:
        return tmp
    else:
        rng = {k:v for k, v in tmp.items() if v['items'][0]['type'] == typ}
        for k, v in rng.items():
            rng[k]['minimum'] = v['items'][0]['minimum']
            rng[k]['maximum'] = v['items'][0]['maximum']
    return rng

def drop_enums(pr):
    return {k:v for k,v in pr.items() if 'enum' not in v}

def find_enums(pr):
    return {k:v for k,v in pr.items() if 'enum' in v}

def drop_explicit_autoui(pr):
    return {k:v for k,v in pr.items() if 'autoui' not in v}

def find_explicit_autoui(pr):
    return {k:v for k,v in pr.items() if 'autoui' in v}
#  ----------------------------------------------------------

#  -- FILTER FUNCTIONS --------------------------------------
#  -- find relevant inputs from json-schema properties ------
def get_IntText(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    ints = get_type(pr, typ='integer')
    simple_ints = {k:v for k,v in ints.items() if 'minimum' not in v and 'maximum' not in v}
    return call_rename_schema_keys(simple_ints, rename_keys=rename_keys)

def get_IntSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    ints = get_type(pr, typ='integer')
    simple_ints = {k:v for k,v in ints.items() if 'minimum' in v and 'maximum' in v}
    return call_rename_schema_keys(simple_ints, rename_keys=rename_keys)

def get_FloatText(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    floats = get_type(pr, typ='number')
    simple_floats = {k:v for k,v in floats.items() if 'minimum' not in v and 'maximum' not in v}
    return call_rename_schema_keys(simple_floats, rename_keys=rename_keys)

def get_FloatSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    floats = get_type(pr, typ='number')
    simple_floats = {k:v for k,v in floats.items() if 'minimum' in v and 'maximum' in v}
    return call_rename_schema_keys(simple_floats, rename_keys=rename_keys)

def get_Text(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    strings = get_type(pr)
    short_strings = drop_enums(strings)
    #short_strings = {k:v for k,v in strings.items() if 'maxLength' in v and v['maxLength']<200}
    return call_rename_schema_keys(short_strings, rename_keys=rename_keys)

def get_Textarea(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    strings = get_type(pr)
    simple_strings = drop_enums(strings)
    long_strings = {k:v for k,v in strings.items() if 'maxLength' in v and v['maxLength']>=200}
    return call_rename_schema_keys(long_strings, rename_keys=rename_keys)

def get_Dropdown(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    drops = find_enums(pr)
    drops = {k:v for k,v in drops.items() if v['type'] != 'array'}
    return call_rename_schema_keys(drops, rename_keys=rename_keys)

def get_SelectMultiple(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    mult = find_enums(pr)
    mult = {k:v for k,v in mult.items() if v['type'] == 'array'}
    return call_rename_schema_keys(mult, rename_keys=rename_keys)

def get_Checkbox(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    return call_rename_schema_keys(get_type(pr, typ='boolean'), rename_keys=rename_keys)

def get_DatePicker(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    date = get_type(pr, 'string')
    date = get_format(date)
    for k,v in date.items():
        v['default'] = datetime.strptime(v['default'], "%Y-%m-%d").date()
    return call_rename_schema_keys(date, rename_keys=rename_keys)

def get_FileChooser(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    file = get_type(pr, 'string')
    file = get_format(file, typ='path')
    return call_rename_schema_keys(file, rename_keys=rename_keys)

def get_DataGrid(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    grid = get_type(pr, 'string')
    grid = get_format(grid, typ='DataFrame')
    return call_rename_schema_keys(grid, rename_keys=rename_keys)

def get_ColorPicker(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    color = get_type(pr, 'string')
    color = get_format(color, typ='color')
    return call_rename_schema_keys(color, rename_keys=rename_keys) 

def get_IntRangeSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    return call_rename_schema_keys(get_range(pr, typ='integer'), rename_keys=rename_keys)  

def get_FloatRangeSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    return call_rename_schema_keys(get_range(pr, typ='number'), rename_keys=rename_keys)  

def get_AutoOveride(pr, rename_keys=True):
    pr = find_explicit_autoui(pr)
    return call_rename_schema_keys(pr, rename_keys=rename_keys)  
#  ----------------------------------------------------------

#  -- WIDGET MAPPING ----------------------------------------
#  -- uses filter functions to map schema objects to widgets 
def AutoOveride(str_widget_type):
    return obj_from_string(str_widget_type)

@dataclass
class WidgetMapper:
    """defines a filter function and associated widget. the "fn_filt" is used to search the 
    json schema to find appropriate objects, the objects are then passed to the "widget" for the ui
    """
    fn_filt: typing.Callable
    widget: typing.Callable

DI_WIDGETS_MAPPER = {
    'IntText': WidgetMapper(fn_filt=get_IntText, widget=widgets.IntText),
    'IntSlider': WidgetMapper(fn_filt=get_IntSlider, widget=widgets.IntSlider),
    'FloatText': WidgetMapper(fn_filt=get_FloatText, widget=widgets.FloatText),
    'FloatSlider': WidgetMapper(fn_filt=get_FloatSlider, widget=widgets.FloatSlider),
    'Text': WidgetMapper(fn_filt=get_Text, widget=widgets.Text),
    'Textarea': WidgetMapper(fn_filt=get_Textarea, widget=widgets.Textarea),
    'Dropdown':WidgetMapper(fn_filt=get_Dropdown, widget=widgets.Dropdown),
    'SelectMultiple':WidgetMapper(fn_filt=get_SelectMultiple, widget=widgets.SelectMultiple),
    'Checkbox': WidgetMapper(fn_filt=get_Checkbox, widget=widgets.Checkbox),
    'DatePicker': WidgetMapper(fn_filt=get_DatePicker, widget=widgets.DatePicker),
    'AutoUiFileChooser': WidgetMapper(fn_filt=get_FileChooser, widget=ipyautoui._custom_widgets.AutoUiFileChooser),
    'AutoUiDataGrid': WidgetMapper(fn_filt=get_DataGrid, widget=ipyautoui._custom_widgets.AutoUiDataGrid),
    'ColorPicker': WidgetMapper(fn_filt=get_ColorPicker, widget=widgets.ColorPicker),
    'IntRangeSlider': WidgetMapper(fn_filt=get_IntRangeSlider, widget=widgets.IntRangeSlider),
    'FloatRangeSlider': WidgetMapper(fn_filt=get_FloatRangeSlider, widget=widgets.FloatRangeSlider),
    'AutoOveride': WidgetMapper(fn_filt=get_AutoOveride, widget=AutoOveride),
}

def map_to_widget(sch: typing.Dict, di_widgets_mapper: typing.Dict=None) -> typing.Dict:
    """maps the widgets to the appropriate data using the di_widgets_mapper. 
    also renames json schema keys to names that ipywidgets can understand.

    Args:
        sch (typing.Dict): [description]
        di_widgets_mapper (typing.Dict, optional): [description]. Defaults to DI_WIDGETS_MAPPER.
            if new mappings given they extend DI_WIDGETS_MAPPER. it is expected that renaming 
            schema keys (call_rename_schema_keys) is done in the filter function

    Returns:
        typing.Dict: a dict (same order as original) with widget type
    """
    if di_widgets_mapper is None:
        di_widgets_mapper = DI_WIDGETS_MAPPER
    else:
        di_widgets_mapper = {**DI_WIDGETS_MAPPER, **di_widgets_mapper}
    pr = sch['properties']
    li_pr = pr.keys()
    di_ = {}
    for k, v in di_widgets_mapper.items():
        di = v.fn_filt(pr)
        for k_, v_ in di.items():
            di_[k_] = v_
            if 'autoui' not in v_:
                di_[k_]['autoui'] = v.widget
            else:
                di_[k_]['autoui'] = v.widget(v_['autoui'])          
    not_matched = set(di_.keys()) ^ set(li_pr) 
    if len(not_matched)>0:
        print('the following UI items from schema not matched to a widget:')
        print(not_matched)
    li_ordered = [l for l in li_pr if l not in not_matched]
    di_ordered = {l:di_[l] for l in li_ordered}        
    return di_ordered


def _init_widgets_and_rows(pr: typing.Dict)-> typing.Tuple(widgets.VBox, typing.Dict):
    """initiates widget for from dict built from schema

    Args:
        pr (typing.Dict): schema properties - sanitised for ipywidgets

    Returns:
        (widgets.VBox, typing.Dict): box with widgets, di of widgets
    """
    di_widgets = {k:v['autoui'](**v) for k,v in pr.items()}
    labels = {k:widgets.HTML(v['autoui_label']) for k,v in pr.items()}
    ui_box = widgets.VBox()
    rows = []
    for (k,v), (k2,v2) in zip(di_widgets.items(), labels.items()):
        rows.append(widgets.HBox([v,v2]))              
    ui_box.children = rows
    return ui_box, di_widgets

class AutoUi(traitlets.HasTraits):
    """AutoUi widget. generates UI form from pydantic schema. keeps the "value" field
    up-to-date on_change 

    Args:
        traitlets ([type]): traitlets.HasTraits makes it possible to observe the value
            of this widget.
    """
    value = traitlets.Dict()
    def __init__(self, pydantic_obj: typing.Type[BaseModel], di_widgets_mapper: typing.Dict=None):
        """init AutoUi

        Args:
            pydantic_obj (typing.Type[BaseModel]): initiated pydantic data object
            di_widgets_mapper (typing.Dict, optional): [description]. Defaults to DI_WIDGETS_MAPPER.
                if new mappings given they extend DI_WIDGETS_MAPPER. it is expected that renaming 
                schema keys (call_rename_schema_keys) is done in the filter function
        """
        self.out = widgets.Output()
        self._set_di_widgets_mapper(di_widgets_mapper)
        self.pydantic_obj = pydantic_obj
        self._init_schema()
        self._init_form()
        self._init_controls()
        
    # TODO
    def parse_file(self,path: pathlib.Path):
        pass

    # TODO
    def file(self,path: pathlib.Path):
        pass

    def _set_di_widgets_mapper(self, di_widgets_mapper):
        if di_widgets_mapper is None:
            self.di_widgets_mapper = DI_WIDGETS_MAPPER
        else:
            self.di_widgets_mapper = {**DI_WIDGETS_MAPPER, **di_widgets_mapper}
            
    def _init_schema(self):
        sch = self.pydantic_obj.schema().copy()
        key = '$ref'
        self.sch = update_property_definitions(sch, key)
        self.pr = map_to_widget(self.sch, di_widgets_mapper=self.di_widgets_mapper)
    
    def _init_form(self):
        self.ui_form = widgets.VBox()
        title = widgets.HTML(f"<big><b>{self.sch['title']}</b></big> - {self.sch['description']}")
        self.ui_box, self.di_widgets = _init_widgets_and_rows(self.pr)
        self.ui_form.children = [title, self.ui_box]
        
    def _init_controls(self):
        [v.observe(functools.partial(self._watch_change, key=k), 'value') for k, v in self.di_widgets.items()];
        
    def _watch_change(self, change, key=None):
        setattr(self.pydantic_obj, key, self.di_widgets[key].value)
        self.value = self.pydantic_obj.dict()
                    
    def display(self):
        with self.out:
            display(self.ui_form)
        display(self.out)
        
    def _ipython_display_(self):
        self.display()


# -

if __name__ == "__main__":
    test = TestAutoLogic() 
    aui = AutoUi(test)
    display(aui)
