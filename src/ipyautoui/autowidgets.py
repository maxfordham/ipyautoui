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

from ipyautoui.constants import DI_JSONSCHEMA_WIDGET_MAP
import ipywidgets as widgets
import traitlets
from copy import deepcopy
from ipyautoui._utils import obj_from_importstr
from ipyautoui.custom import modelrun, markdown_widget
from ipyautoui._utils import remove_non_present_kwargs
from datetime import datetime

#  -- CHANGE JSON-SCHEMA KEYS TO IPYWIDGET KEYS -------------
def update_key(key, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    if key in di_map.keys():
        return di_map[key]
    else:
        return key


def update_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    return {update_key(k, di_map): v for k, v in di.items()}


def create_widget_caller(schema, calling=None):
    """
    creates a "caller" object from the schema. 
    this renames schema keys as follows to match ipywidgets: 
        ```
        {
            'minimum': 'min',
            'maximum': 'max',
            'enum': 'options',
            'default': 'value',
            'description': 'autoui_description'
        }
        ```

    
    Args: 
        schema: dict, json schema
        calling, default=None: the class that will be called by the 
            returned "caller" object. if not None, args not present in the class
            are removed from "caller"
    
    Returns: 
        caller: dict, object that is passed the "calling" widget 
            initialised like ```calling(**caller)```
            
    """
    caller = deepcopy(schema)
    caller = update_keys(schema)
    caller = {k: v for k, v in caller.items() if k != "description"}
    caller = {k: v for k, v in caller.items() if k != "title"}
    if calling is not None:
        caller = remove_non_present_kwargs(calling, caller)
    return caller


class IntText(widgets.IntText):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class IntSlider(widgets.IntSlider):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class FloatText(widgets.FloatText):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class FloatSlider(widgets.FloatSlider):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class IntRangeSlider(widgets.IntRangeSlider):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        self.caller["min"] = self.schema["items"][0]["minimum"]
        self.caller["max"] = self.schema["items"][0]["maximum"]
        super().__init__(**self.caller)


class FloatRangeSlider(widgets.FloatRangeSlider):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        self.caller["min"] = self.schema["items"][0]["minimum"]
        self.caller["max"] = self.schema["items"][0]["maximum"]
        super().__init__(**self.caller)


class Text(widgets.Text):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class Textarea(widgets.Textarea):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class Combobox(widgets.Combobox):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class Dropdown(widgets.Dropdown):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class SelectMultiple(widgets.SelectMultiple):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class Checkbox(widgets.Checkbox):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class ColorPicker(widgets.ColorPicker):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class DatePickerString(widgets.HBox, traitlets.HasTraits):
    _value = traitlets.Unicode(allow_none=True, default_value=None)

    def __init__(self, schema):
        """thin wrapper around ipywidgets.DatePicker that stores "value" as 
        json serializable Unicode"""
        self.picker = widgets.DatePicker()
        self.schema = schema
        self._init_controls()
        super().__init__()
        self.children = [self.picker]

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        if "strftime_format" not in value.keys():
            self._strftime_format = "%Y-%m-%d"
        else:
            self._strftime_format = value["strftime_format"]
        if "disabled" not in value.keys():
            self.disabled = False
        else:
            self.disabled = value["disabled"]
        if "default" in value.keys():
            self.value = value["default"]
        self._schema = value

    @property
    def disabled(self):
        return self.picker.disabled

    @disabled.setter
    def disabled(self, value):
        self.picker.disabled = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if type(value) == str:
            self.picker.value = datetime.strptime(value, self.strftime_format)
        else:
            self.picker.value = value

    @property
    def strftime_format(self):
        return self._strftime_format

    @strftime_format.setter
    def strftime_format(self):
        self._strftime = value
        self._update_change("change")

    def _init_controls(self):
        self.picker.observe(self._update_change, "value")

    def _get_value(self):
        try:
            return self.picker.value.strftime(self.strftime_format)
        except:
            return None

    def _update_change(self, on_change):
        self._value = self._get_value()


# class DatetimePicker(widgets.DatetimePicker):
#     def __init__(self, schema):
#         self.schema = schema
#         self.caller = create_widget_caller(schema)
#         super().__init__(**self.caller)

# class FileChooser(widgets.FileChooser):
#     def __init__(self, schema):
#         self.schema = schema
#         self.caller = create_widget_caller(schema)
#         super().__init__(**self.caller)

# class Grid(widgets.Grid):
#     def __init__(self, schema):
#         self.schema = schema
#         self.caller = create_widget_caller(schema)
#         super().__init__(**self.caller)


class ColorPicker(widgets.ColorPicker):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


def autooveride(schema):
    aui = schema["autoui"]
    if type(aui) == str:
        cl = obj_from_importstr(aui)
    else:
        cl = aui
    return cl(schema)


class AutoPlaceholder(widgets.Textarea):
    def __init__(self, schema):
        txt = f"""
PLACEHOLDER WIDGET 
schema: 
{str(schema)}
"""
        super().__init__(value=txt)


class RunName(modelrun.RunName):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema, calling=modelrun.RunName)
        super().__init__(**self.caller)


class AutoMarkdown(markdown_widget.MarkdownWidget):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(
            schema, calling=markdown_widget.MarkdownWidget
        )
        super().__init__(**self.caller)


# class AutoOveride:
#     def __init__(self, schema):
#         self.schema = schema self.caller = create_widget_caller(schema)
#         super().__init__(**self.caller)

