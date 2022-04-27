# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# %run __init__.py
# %load_ext lab_black

"""
extends standard ipywidgets to facilitate initialisation from jsonschema
"""

from ipyautoui.constants import DI_JSONSCHEMA_WIDGET_MAP, BUTTON_WIDTH_MIN
import ipywidgets as widgets
from copy import deepcopy
from ipyautoui._utils import obj_from_importstr

#  -- CHANGE JSON-SCHEMA KEYS TO IPYWIDGET KEYS -------------
def update_key(key, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    if key in di_map.keys():
        return di_map[key]
    else:
        return key

def update_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    return {update_key(k, di_map): v for k, v in di.items()}

def _init_autoui(schema):
    schema = deepcopy(schema)
    caller = update_keys(schema)
    caller = {k: v for k, v in caller.items() if k != "description"}
    caller = {k: v for k, v in caller.items() if k != "title"}
    return schema, caller

    
class IntText(widgets.IntText):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)

class IntSlider(widgets.IntSlider):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
class FloatText(widgets.FloatText):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
class FloatSlider(widgets.FloatSlider):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
class IntRangeSlider(widgets.IntRangeSlider):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        self.caller["min"] = self.schema["items"][0]["minimum"]
        self.caller["max"] = self.schema["items"][0]["maximum"]
        super().__init__(**self.caller)
        
class FloatRangeSlider(widgets.FloatRangeSlider):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        self.caller["min"] = self.schema["items"][0]["minimum"]
        self.caller["max"] = self.schema["items"][0]["maximum"]
        super().__init__(**self.caller)
        
class Text(widgets.Text):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
class Textarea(widgets.Textarea):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
class Combobox(widgets.Combobox):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
class Dropdown(widgets.Dropdown):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
class SelectMultiple(widgets.SelectMultiple):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
class Checkbox(widgets.Checkbox):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
class DatePicker(widgets.DatePicker):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)
        
# class DatetimePicker(widgets.DatetimePicker):
#     def __init__(self, schema):
#         self.schema, self.caller = _init_autoui(schema)
#         super().__init__(**self.caller)
        
# class FileChooser(widgets.FileChooser):
#     def __init__(self, schema):
#         self.schema, self.caller = _init_autoui(schema)
#         super().__init__(**self.caller)
        
# class Grid(widgets.Grid):
#     def __init__(self, schema):
#         self.schema, self.caller = _init_autoui(schema)
#         super().__init__(**self.caller)
        
class ColorPicker(widgets.ColorPicker):
    def __init__(self, schema):
        self.schema, self.caller = _init_autoui(schema)
        super().__init__(**self.caller)

def autooveride(schema):
    aui = schema["autoui"]
    if type(aui) == str:
        cl = obj_from_importstr(aui)
    else:
        cl = aui
    return cl(schema)
