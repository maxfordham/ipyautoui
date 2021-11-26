# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.12.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
import sys
sys.path.append('/mnt/c/engDev/git_extrnl/pydantic')
# %run __init__.py

import pathlib
from pydantic import BaseModel, ValidationError, validator
import ipywidgets as widgets
from typing import Optional, List, Dict, Type, Any, Union
from markdown import markdown
import ipydatagrid as ipg
import pandas as pd

from ipyautoui.constants import DF_MAP
from ipyautoui._utils import obj_from_string, _markdown
from ipyautoui._auto_logic import get_widget_class_strings, ALLOWED_VALUE_TYPES
from ipyautoui._custom_widgets import AutoUiFileChooser, AutoUiFileUpload, AutoUiDataGrid, AutoModelRunName


# +
# data-definitions only. they define the fields that are required to create a ui object. 

class AutoWidget(BaseModel):
    """data container for a AutoWidget. 
    this is a data container for all auto-widgets.
    it inherits pydantic.BaseModel and uses pydantic validation tools to 
    initiate the "widget" and the "autoui_type" based on the value type and kwargs. 
    using the pydantic ".dict()" and ".json()" commands data can be serialised. the "widget"
    parameter is excluded from the "dict()" and "json()" commands; this means that the 
    output contains strings only and can be written to file.
    """
    value: Any # ALLOWED_VALUE_TYPES
    kwargs: Dict = {}
    autoui_type: str = None
    widget: Any = None
    
    @validator('autoui_type', pre=True, always=True)
    def get_autoui_type(cls, v, values):
        if v is not None:
            # user indicated ui widget type
            if v in DF_MAP.widget.tolist():
                # user provided short-hand mapping to widget type
                cls_str = DF_MAP.set_index('widget')['widget_class_string'].to_dict()[v]
            else:
                # user input class string to be used explicitly
                cls_str = v
        else:
            # run auto ui mapper
            value = values['value']
            cls_str = get_widget_class_strings(values['value'], values['kwargs'], df_map=DF_MAP)
        if cls_str[0:6] != "<class":
            raise ValueError('autoui_type must be a class string')
        return cls_str 
    
    @validator('widget', always=True)
    def get_widget(cls, v, values):
        value = values['value']
        kwargs = values['kwargs']
        if value is not None:
            kwargs = {'value':value} | kwargs
        else:
            kwargs = kwargs
        return obj_from_string(values['autoui_type'])(**kwargs)
        
    class Config:
        arbitrary_types_allowed = True
        
class RowBase(BaseModel):
    name: str = 'name'
    label: str = 'label'

class WidgetRowBase(RowBase,AutoWidget):
    class Config:
        arbitrary_types_allowed = True

class AutoUiBase(BaseModel):
    """
    AutoUi data container. a defined data structure that can be written 
    to dict or JSON or used to initiate a AutoUi object.
    """
    rows: List[WidgetRowBase] = []
    path: pathlib.PurePath = None
        
    class Config:
        arbitrary_types_allowed = True
        fields = {
            'path': {
                'exclude': ...,
            }
        }


# +
# classes that inherit the data objects, and are initialised by them. 
# these classes add the "observe" ability

class WidgetRow(WidgetRowBase):
    """
    class that observes the WidgetRowBase and copies the value from the 
    awc.widget.value to the awc.value on change, this ensures that when the object 
    is written to file (and awc.widget is ignored when written to dict or json),
    thus the value of the widget state is saved
    """
    row: widgets.HBox = None  
    widget: Any = None
        
    def __init__(self, aw: WidgetRowBase):
        """
        Args:
            awc: AutoWidgetBase, data object for AutoWidget
        """
        super().__init__(**aw.dict())
        self._init_row()
        self._init_controls()
        
    def _init_row(self):
        self.row = self._get_row()
    
    def _init_controls(self):
        self.widget.observe(self._copy_value, 'value')
        
    def _copy_value(self, onchange):
        self.value = self.widget.value
        
    def _get_row(self):
        name = self.name
        label = self.label
        return widgets.HBox([self.widget, _markdown(value=f'__{name}__, '), _markdown(value=f'_{label}_')], layout={'width':'100%'}) 
        
    def display(self):
        display(self.row)

    def _ipython_display_(self):
        self.display()
        
    class Config:
        arbitrary_types_allowed = True
        fields = {
            'widget': {
                'exclude': ...,
            },
            'row': {
                'exclude': ...,
            }
        }
        
class AutoUi(AutoUiBase):
    """class that observes the AutoUiBase data structure and copies the value from the 
    self.widget.value to the self.value param on change, this ensures that when the object 
    is written to file (note. self.widget, self.ui are ignored when written to dict or json),
    that the value of the widget state is saved. this relies on the widgets that are being
    observed using traitlets and having an observable "value" field.
    
    TODO:
        make it so it only copies the data that has changed from the widgets 
        to the value field on change insted of the data from all widgets.
    """
    ui: widgets.VBox = None
        
    def __init__(self, aui: AutoUiBase):
        super().__init__(**aui.dict())
        self._init_widgets()
        
    def _init_widgets(self):
        self.rows = [WidgetRow(row) for row in self.rows]
        self.ui = widgets.VBox()
        self.ui.children = [w.row for w in self.rows]
    
    def display(self):
        display(self.ui)

    def _ipython_display_(self):
        self.display()
        
    class Config:
        arbitrary_types_allowed = True
        fields = {
            'ui': {
                'exclude': ...,
            }
        }



# -

if __name__ == "__main__":
    from IPython.display import Markdown
    display(Markdown('## Widgets'))
    from ipyautoui.test_autoui_data import di_test_autologic 
    from ipyautoui.tests import test_display_WidgetRow_widget, test_display_AutoUi
    test_display_WidgetRow_widget(di_test_autologic)
    ui=test_display_AutoUi(di_test_autologic)
    display(ui)
    #ui
