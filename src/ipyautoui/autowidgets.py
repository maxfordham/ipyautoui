# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# %run _dev_sys_path_append.py
# %run __init__.py
#
# %load_ext lab_black

"""
extends standard ipywidgets to facilitate initialisation from jsonschema
"""

from ipyautoui.constants import MAP_JSONSCHEMA_TO_IPYWIDGET
import ipywidgets as w
import traitlets as tr
from copy import deepcopy
from ipyautoui.custom import (
    modelrun,
    markdown_widget,
    filechooser,
)  # , fileupload #<- `fileupload` causes circular import
from ipyautoui._utils import remove_non_present_kwargs
from datetime import datetime
import functools
import pandas as pd
import numpy as np
import math

SHOW_NONE_KWARGS = dict(value="None", disabled=True, layout={"display": "None"})


def _get_value_trait(obj_with_traits):
    """gets the trait type for a given object (looks for "_value" and
    "value" allowing use of setters and getters)
    Args:
        obj_with_traits (traitlets.Type): obj with traits
    Raises:
        ValueError: if "value" trait not exist
    Returns:
        typing.Type: trait type of traitlet
    """
    try:
        return obj_with_traits.traits()["value"]
    except:
        raise ValueError(f"{str(type(obj_with_traits))}: has no 'value' trait")


def is_null(value):
    """

    Example:
        >>> [is_null(value) for value in [math.nan, np.nan, None, pd.NA, 3.3, "adsf"]]
        [True, True, True, True, False, False]
    """
    fn = lambda value, check: True if value is check else False
    li_check = [fn(value, obj) for obj in [pd.NA, math.nan, np.nan, None]]
    if True in li_check:
        return True
    else:
        return False


class Nullable(w.HBox):
    """class to allow widgets to be nullable. The widget that is extended is accessed
    using `self.widget`"""

    disabled = tr.Bool(default_value=False)
    
    @tr.observe("disabled")
    def observe_disabled(self, on_change):
        """If disabled, ensure that the widget is disabled and the button is also."""
        if self.disabled:
            if self.widget.value is not None:
                self.bn.value = False
            else:
                self.bn.value = True
            self.bn.disabled = True
            self.widget.disabled = True
        else:
            self.bn.disabled = False
            self.widget.disabled = False
    
    def __init__(self, widget_type, schema, *args, **kwargs):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        # ^ TODO: should this be in a higher-level func?
        #         ui = nullable(w.IntSlider)(value=30) # this doesn't work bu maybe should...
        self.nullable = tr.Bool(default_value=True)
        self.bn = w.ToggleButton(icon="toggle-on", layout={"width": "40px"})
        self.show_none = w.Text(**SHOW_NONE_KWARGS)
        if "nullable" in kwargs.keys():
            self.nullable = kwargs["nullable"]
            kwargs.pop("nullable")
        if "value" in kwargs.keys():
            value = kwargs["value"]
        elif len(args) > 0:
            value = args[0]
        else:
            value = None
        self.widget = widget_type(*args, {**kwargs, **self.caller})
        self._init_trait()
        super().__init__([self.bn, self.widget, self.show_none])
        self._init_controls()
        self.value = value
        self._set_disabled()

    def _init_trait(self):
        # NOTE: see test for add_traits that demos usage  -@jovyan at 7/18/2022, 12:11:39 PM
        # https://github.com/ipython/ipython/commit/5105f02df27456cc54867dfbe4cef60d91021f92
        trait_type = type(_get_value_trait(self.widget))
        self.add_traits(**{"_value": trait_type(allow_none=True)})

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if pd.isnull(value):
            self.bn.value = True
            self._value = None
        else:
            self.bn.value = False
            self.widget.value = value
            # note. as the self.widget.value still exists in the background,
            #       this may not trigger a change event...
            #       so we'll manually do it too (below)
            self._update("")

    def _init_controls(self):
        self.bn.observe(self._toggle_none, "value")
        self.widget.observe(self._update, "value")
        self.observe(self._observe_nullable, "nullable")

    def _observe_nullable(self, onchange):
        if self.nullable:
            self.bn.layout.display = ""
        else:
            self.bn.layout.display = "None"

    def _update(self, onchange):
        self._value = self.widget.value

    def _toggle_none(self, onchange):
        if self.bn.value:
            self.bn.icon = "toggle-off"
            self.widget.layout.display = "None"
            self.show_none.layout.display = ""
            self.value = None
        else:
            self.bn.icon = "toggle-on"
            self.widget.layout.display = ""
            self.show_none.layout.display = "None"
            self.value = self.widget.value

    def _set_disabled(self):
        """If disabled in schema, set to value defined."""
        if "disabled" in self.schema:
            self.disabled = self.schema["disabled"]


def nullable(fn, **kwargs):
    """extend a simple widget to allow None

    Args:
        fn (widget_type): e.g. w.IntText

    Returns:
        Nullable: a HBox that contains a the widget `widget`.
    """
    nm = fn.__name__
    partial_func = functools.partial(Nullable, fn, **kwargs)
    functools.update_wrapper(partial_func, Nullable)
    partial_func.__name__ = Nullable.__name__ + nm
    return partial_func


#  -- CHANGE JSON-SCHEMA KEYS TO IPYWIDGET KEYS -------------


def update_keys(di, di_map=MAP_JSONSCHEMA_TO_IPYWIDGET):
    update_key = lambda key, di_map: di_map[key] if key in di_map.keys() else key
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


# TODO: add doctests here


class IntText(w.IntText):  # TODO: add value to these as arg?
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class IntSlider(w.IntSlider):
    """extends `ipywidgets.IntSlider`. Example:
    >>> from ipyautoui.test_schema import TestAutoLogic
    >>> import ipywidgets as w
    >>> sch = TestAutoLogic.schema()["properties"]['int_slider']
    >>> IntSlider(sch)
    IntSlider(value=2, max=3, min=1)
    >>> sch['type']
    'integer'
    """

    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


# TODO: add `schema` as a `tr.Dict()` with a validator and observe
#       on_change re-initialize the widget...


class FloatText(w.FloatText):
    """Example:
    >>> from ipyautoui.test_schema import TestAutoLogic
    >>> import ipywidgets as w
    >>> sch = TestAutoLogic.schema()["properties"]['float_text']
    >>> FloatText(sch)
    FloatText(value=2.2)
    >>> sch['type']
    'number'
    """

    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class FloatSlider(w.FloatSlider):
    """Example:
    >>> from ipyautoui.test_schema import TestAutoLogic
    >>> import ipywidgets as w
    >>> sch = TestAutoLogic.schema()["properties"]['float_slider']
    >>> FloatSlider(sch)
    FloatSlider(value=2.2, max=3.0, min=1.0)
    >>> sch['type']
    'number'
    """

    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class IntRangeSlider(w.IntRangeSlider):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        self.caller["min"] = self.schema["items"][0]["minimum"]
        self.caller["max"] = self.schema["items"][0]["maximum"]
        super().__init__(**self.caller)


class FloatRangeSlider(w.FloatRangeSlider):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        self.caller["min"] = self.schema["items"][0]["minimum"]
        self.caller["max"] = self.schema["items"][0]["maximum"]
        super().__init__(**self.caller)


class Text(w.Text):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class Textarea(w.Textarea):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class Combobox(w.Combobox):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class Dropdown(w.Dropdown):
    """extends `ipywidgets.Dropdown`. Example:
    >>> from ipyautoui.demo_schemas import CoreIpywidgets
    >>> import ipywidgets as w
    >>> sch = CoreIpywidgets.schema()["properties"]['dropdown']
    >>> Dropdown(sch).value

    # >>> sch = CoreIpywidgets.schema()["properties"]['dropdown_edge_case']
    # >>> Dropdown(sch).value
    # "apple"
    """

    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class SelectMultiple(w.SelectMultiple):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class Checkbox(w.Checkbox):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class DatePickerString(w.HBox, tr.HasTraits):
    _value = tr.Unicode(allow_none=True, default_value=None)

    def __init__(self, schema):
        """thin wrapper around ipywidgets.DatePicker that stores "value" as
        json serializable Unicode"""
        self.picker = w.DatePicker()
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
    def strftime_format(self, value):
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


class FileChooser(filechooser.FileChooser):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


# class Grid(w.Grid):
#     def __init__(self, schema):
#         self.schema = schema
#         self.caller = create_widget_caller(schema)
#         super().__init__(**self.caller)


class ColorPicker(w.ColorPicker):
    def __init__(self, schema):
        self.schema = schema
        self.caller = create_widget_caller(schema)
        super().__init__(**self.caller)


class AutoPlaceholder(w.Textarea):
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


# class AutoUploadPaths(fileupload.FilesUploadToDir):
#     def __init__(self, schema):
#         from ipyautoui.custom import modelrun, markdown_widget, filechooser, fileupload
#         self.schema = schema
#         self.caller = create_widget_caller(
#             schema, calling=markdown_widget.MarkdownWidget
#         )
#         super().__init__(**self.caller)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
# -


