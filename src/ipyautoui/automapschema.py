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

from ipyautoui.test_schema import TestAutoLogic, TestObjects, TestArrays
from ipyautoui.constants import load_test_constants
import typing
from ipyautoui.constants import DI_JSONSCHEMA_WIDGET_MAP, BUTTON_WIDTH_MIN
from copy import deepcopy
from pydantic import BaseModel
from ipywidgets import widgets

test_constants = load_test_constants()
test = TestAutoLogic()

# +
import pathlib
import functools
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, Markdown
from datetime import datetime, date
from dataclasses import dataclass
from pydantic import BaseModel
from markdown import markdown
import immutables
import json
import traitlets
import typing
from enum import Enum
import inspect

from ipyautoui.displayfile import PreviewPy
from ipyautoui.test_schema import TestAutoLogic
import ipyautoui.autowidgets as auiwidgets

from ipyautoui._utils import (
    obj_from_string,
    display_pydantic_json,
    file,
    obj_from_importstr,
)
from ipyautoui.custom import Grid, FileChooser, SaveButtonBar
from ipyautoui.constants import DI_JSONSCHEMA_WIDGET_MAP, BUTTON_WIDTH_MIN
from ipyautoui.constants import load_test_constants
import numbers

frozenmap = immutables.Map
# +
#  -- ATTACH DEFINITIONS TO PROPERTIES ----------------------
def recursive_search_schema(sch: typing.Dict, li: typing.List) -> typing.Dict:
    """searches down schema tree to retrieve definitions

    Args:
        sch (typing.Dict): json schema made from pydantic
        li (typing.List): list of keys to search down tree

    Returns:
        typing.Dict: definition retrieved from schema
    """
    f = li[0]
    if len(li) > 1:
        li_tmp = li[1:]
        sch_tmp = sch[f]
        return recursive_search_schema(sch_tmp, li_tmp)
    else:
        return sch[f]


def attach_schema_refs(schema, schema_base=None):
    """
    attachs #definitions to $refs within the main schema
    recursive function. schema_base is constant as is used for retrieving definitions. 
    schema is recursively edited. 
    
    Args:
        schema (dict): json schema
        schema_base (dict): same as above but isn't recursively searched. leave blank 
            and it defaults to schema
    
    Returns:
        schema (dict): with $refs removed and replaced with #defintions
    
    """
    if schema_base is None:
        schema_base = schema
    if type(schema) == list:
        for n, s in enumerate(schema):
            schema[n] = attach_schema_refs(s, schema_base=schema_base)
    elif type(schema) == dict:
        for k, v in schema.items():
            if type(v) == dict:
                if "$ref" in v:
                    li_filt = v["$ref"].split("/")[1:]
                    schema[k] = recursive_search_schema(schema_base, li_filt)
                else:
                    schema[k] = attach_schema_refs(v, schema_base=schema_base)
            elif type(v) == list:
                schema[k] = attach_schema_refs(v, schema_base=schema_base)
            else:
                pass
    else:
        pass
    return schema


#  ----------------------------------------------------------

# +
# IntText
# IntSlider
# FloatText
# FloatSlider
# Text
# Textarea
# Dropdown
# SelectMultiple
# Checkbox
# autooveride


def is_IntText(di):
    if "autoui" in di.keys():
        return False
    if not di["type"] == "integer":
        return False
    if "minimum" and "maximum" in di.keys():
        return False
    return True


def is_IntSlider(di):
    if "autoui" in di.keys():
        return False
    if not di["type"] == "integer":
        return False
    if "minimum" and "maximum" not in di.keys():
        return False
    return True


def is_FloatText(di):
    if "autoui" in di.keys():
        return False
    if not di["type"] == "number":
        return False
    if "minimum" and "maximum" in di.keys():
        return False
    return True


def is_FloatSlider(di):
    if "autoui" in di.keys():
        return False
    if not di["type"] == "number":
        return False
    if "minimum" and "maximum" not in di.keys():
        return False
    return True


def is_range(di, is_type="integer"):
    """finds numeric range within schema properties. a range in json must satisfy these criteria:
    - check1: array length == 2
    - check2: minimum and maximum values must be given
    - check3: check numeric typ given (i.e. integer or number or numeric)
    """

    def get_type(di):
        t = di["items"][0]["type"]
        t1 = di["items"][0]["type"]
        if t != t1:
            raise ValueError("items are different types")
        else:
            return t

    if di["type"] != "array":
        return False
    if not "items" in di.keys() and len(di["items"]) != 2:
        return False
    for i in di["items"]:
        if "minimum" not in i and "maximum" not in i:
            return False

    #  check3: check numeric typ given (i.e. integer or number or numeric)
    if is_type == "numeric":
        if not get_type(di) == "integer" or get_type(di) == "number":
            return False
    elif is_type == "number":
        if not get_type(di) == "number":
            return False
    elif is_type == "integer":
        if not get_type(di) == "integer":
            return False
    else:
        raise ValueError('is_type must be one of: "integer", "number", "numeric"')
    return True


def is_IntRangeSlider(di):
    if "autoui" in di.keys():
        return False
    if not is_range(di, is_type="integer"):
        return False
    return True


def is_FloatRangeSlider(di):
    if "autoui" in di.keys():
        return False
    if not is_range(di, is_type="number"):
        return False
    return True


def is_Text(di):
    if "autoui" in di.keys():
        return False
    if not di["type"] == "string":
        return False
    if "enum" in di.keys():
        return False
    if "maxLength" in di.keys() and di["maxLength"] >= 200:
        return False
    return True


def is_Textarea(di):
    if "autoui" in di.keys():
        return False
    if not di["type"] == "string":
        return False
    if "enum" in di.keys():
        return False
    if "maxLength" in di.keys() and di["maxLength"] <= 200:  # i.e. == long text
        return False
    return True


def is_Dropdown(di):
    if "autoui" in di.keys():
        return False
    if "enum" not in di.keys():
        return False
    if di["type"] == "array":
        return False
    return True


def is_SelectMultiple(di):
    if "autoui" in di.keys():
        return False
    if "enum" not in di.keys():
        return False
    if di["type"] != "array":
        return False
    return True


def is_Checkbox(di):
    if "autoui" in di.keys():
        return False
    if di["type"] != "boolean":
        return False
    return True


def is_AutoOveride(di):
    if "autoui" not in di.keys():
        return False
    return True


def is_AutoIpywidget(di):
    if "autoui" in di.keys():
        return False
    if not di["type"] == "object":
        return False
    return True


class WidgetMapper(BaseModel):
    """defines a filter function and associated widget. the "fn_filt" is used to search the
    json schema to find appropriate objects, the objects are then passed to the "widget" for the ui
    """

    fn_filt: typing.Callable
    widget: typing.Callable


class WidgetCaller(BaseModel):
    schema_: typing.Dict
    autoui: typing.Callable  # TODO: change name autoui --> widget
    # mvalue: typing.Any = None  # TODO: add functionality to add value. (don't think this is required...)


def widgetcaller(caller: WidgetCaller, show_errors=True):
    """
    returns widget from widget caller object
    Args:
        caller: WidgetCaller
    Returns:
        widget of some kind
    """
    try:
        # args = inspect.getfullargspec(cl).args
        # kw = {k_: v_ for k_, v_ in v.items() if k_ in args}
        # ^ do this if required (get allowed args from class)

        w = caller.autoui(caller.schema_)

    except:
        if show_errors:
            txt = f"""
ERROR: widgetcaller
-----
widget:
{str(caller.autoui)}

schema: 
{str(caller.schema_)}
"""
            # TODO: add logging
            w = widgets.Textarea(txt)
        else:
            return  # TODO: check this works
    return w


MAP_WIDGETS = frozenmap(
    **{
        "AutoOveride": WidgetMapper(
            fn_filt=is_AutoOveride, widget=auiwidgets.autooveride
        ),
        "IntText": WidgetMapper(fn_filt=is_IntText, widget=auiwidgets.IntText),
        "IntSlider": WidgetMapper(fn_filt=is_IntSlider, widget=auiwidgets.IntSlider),
        "FloatText": WidgetMapper(fn_filt=is_FloatText, widget=auiwidgets.IntText),
        "FloatSlider": WidgetMapper(
            fn_filt=is_FloatSlider, widget=auiwidgets.IntSlider
        ),
        "IntRangeSlider": WidgetMapper(
            fn_filt=is_IntRangeSlider, widget=auiwidgets.IntRangeSlider
        ),
        "FloatRangeSlider": WidgetMapper(
            fn_filt=is_FloatRangeSlider, widget=auiwidgets.FloatRangeSlider
        ),
        "Text": WidgetMapper(fn_filt=is_Text, widget=auiwidgets.Text),
        "Textarea": WidgetMapper(fn_filt=is_Textarea, widget=auiwidgets.Textarea),
        "Dropdown": WidgetMapper(fn_filt=is_Dropdown, widget=auiwidgets.Dropdown),
        "SelectMultiple": WidgetMapper(
            fn_filt=is_SelectMultiple, widget=auiwidgets.SelectMultiple
        ),
        "Checkbox": WidgetMapper(fn_filt=is_Checkbox, widget=auiwidgets.Checkbox),
        "object": WidgetMapper(
            fn_filt=is_AutoIpywidget, widget=auiwidgets.AutoPlaceholder
        ),
        "array": WidgetMapper(
            fn_filt=is_AutoIpywidget, widget=auiwidgets.AutoPlaceholder
        ),
    }
)


def map_widget(di, widget_map=MAP_WIDGETS, fail_on_error=False):
    mapped = []

    # loop through widget_map to find a correct mapping...
    for k, v in widget_map.items():
        if v.fn_filt(di):
            mapped.append(k)
    if len(mapped) == 0:
        if fail_on_error:
            # TODO: pass error or not..
            raise ValueError(f"widget map not found for: {di}")
        else:
            return WidgetCaller(schema_=di, autoui=auiwidgets.AutoPlaceholder)
    elif len(mapped) == 1:
        k = mapped[0]
        return WidgetCaller(schema_=di, autoui=widget_map[k].widget)
    else:
        # TODO: add logging. take last map
        k = mapped[-1]
        return WidgetCaller(schema_=di, autoui=widget_map[k].widget)


def automapschema(schema, widget_map=MAP_WIDGETS):
    schema = attach_schema_refs(schema)
    if "type" not in schema.keys():
        raise ValueError('"type" is a required key in schema')
    if schema["type"] == "object":
        # loop through keys
        pr = schema["properties"]
        return {k: map_widget(v, widget_map=widget_map) for k, v in pr.items()}
    # elif schema["type"] == "array":
    #     return map_widget(schema, widget_map=widget_map)
    else:
        return map_widget(schema, widget_map=widget_map)


if __name__ == "__main__":
    m = automapschema(
        {
            "title": "Int Slider",
            "default": 2,
            "minimum": 0,
            "maximum": 3,
            "type": "integer",
        }
    )

    display(m)
# -

if __name__ == "__main__":
    s = TestAutoLogic.schema()
    # display(s)
    m = automapschema(s)
    display(m)

if __name__ == "__main__":
    display(widgets.VBox([widgetcaller(v) for k, v in m.items()]))


