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


#  ----------------------------------------------------------
#  -- HELPER FUNCTIONS --------------------------------------
def get_type(pr, typ="string"):
    return {k: v for k, v in pr.items() if v["type"] == typ}


def get_format(pr, typ="date"):
    pr = {k: v for k, v in pr.items() if "format" in v}
    return {k: v for k, v in pr.items() if v["format"] == typ}


def get_range(pr, is_type="integer"):
    """finds numeric range within schema properties. a range in json must satisfy these criteria:
    - check1: array length == 2
    - check2: minimum and maximum values must be given
    - check3: check numeric typ given (i.e. integer or number or numeric)
    """
    array = get_type(pr, typ="array")

    #  check1: array length == 2
    array = {k: v for k, v in array.items() if len(v["items"]) == 2}
    if len(array) == 0:
        return {}
    #  ^ if len(v["items"]) != 2 returns empty dict

    #  check2: minimum and maximum values must be given
    tmp = {}
    for k, v in array.items():
        tmp[k] = v
        for i in v["items"]:
            if "minimum" not in i and "maximum" not in i:
                tmp = {}
    if len(tmp) == 0:
        return {}
    #  ^ if "minimum" and "maximum" not given returns empty dict

    #  check3: check numeric typ given (i.e. integer or number or numeric)
    if is_type == "numeric":
        rng = {
            k: v
            for k, v in tmp.items()
            if v["items"][0]["type"] == "integer" or v["items"][0]["type"] == "number"
        }
    else:
        rng = {k: v for k, v in tmp.items() if v["items"][0]["type"] == is_type}
    if len(rng) == 0:
        return {}
    #  ^ if wrong numeric type given returns empty dict

    for k, v in rng.items():
        rng[k]["minimum"] = v["items"][0]["minimum"]
        rng[k]["maximum"] = v["items"][0]["maximum"]
    return rng


def drop_enums(pr):
    return {k: v for k, v in pr.items() if "enum" not in v}


def find_enums(pr):
    return {k: v for k, v in pr.items() if "enum" in v}


def check_for_autoui(v):
    try:
        return "autoui" not in v
    except:
        return True


def drop_explicit_autoui(pr):
    return {k: v for k, v in pr.items() if check_for_autoui(v)}


def find_explicit_autoui(pr):
    return {k: v for k, v in pr.items() if "autoui" in v}

#  ----------------------------------------------------------

#  -- FILTER FUNCTIONS --------------------------------------
#  -- find relevant inputs from json-schema properties ------
def get_IntText(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    ints = get_type(pr, typ="integer")
    simple_ints = {
        k: v for k, v in ints.items() if "minimum" not in v and "maximum" not in v
    }
    return simple_ints


def get_IntSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    ints = get_type(pr, typ="integer")
    simple_ints = {k: v for k, v in ints.items() if "minimum" in v and "maximum" in v}
    return simple_ints


def get_FloatText(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    floats = get_type(pr, typ="number")
    simple_floats = {
        k: v for k, v in floats.items() if "minimum" not in v and "maximum" not in v
    }
    return simple_floats


def get_FloatSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    floats = get_type(pr, typ="number")
    simple_floats = {
        k: v for k, v in floats.items() if "minimum" in v and "maximum" in v
    }
    return simple_floats


def get_Text(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    strings = get_type(pr)
    short_strings = drop_enums(strings)
    return short_strings


def get_Textarea(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    strings = get_type(pr)
    simple_strings = drop_enums(strings)
    long_strings = {
        k: v for k, v in strings.items() if "maxLength" in v and v["maxLength"] >= 200
    }
    return long_strings


def get_Dropdown(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    drops = find_enums(pr)
    drops = {k: v for k, v in drops.items() if v["type"] != "array"}
    return drops


def get_SelectMultiple(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    mult = find_enums(pr)
    mult = {k: v for k, v in mult.items() if v["type"] == "array"}
    return mult


def get_Checkbox(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    return get_type(pr, typ="boolean")


def get_DatePicker(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    date = get_type(pr, "string")
    date = get_format(date)
    for k, v in date.items():
        if type(v["default"]) == str:
            v["default"] = datetime.strptime(v["default"], "%Y-%m-%d").date()
    return date


def get_DatetimePicker(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    date = get_type(pr, "string")
    date = get_format(date, typ="date-time")
    for k, v in date.items():
        if "default" in v.keys():
            if type(v["default"]) == str:
                v["default"] = datetime.strptime(
                    v["default"], "%Y-%m-%dT%H:%M:%S.%f"
                ).date()
    return date


def get_FileChooser(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    file = get_type(pr, "string")
    file = get_format(file, typ="path")
    return file


def get_DataGrid(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    grid = get_type(pr, "string")
    grid = get_format(grid, typ="DataFrame")
    return grid


def get_ColorPicker(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    color = get_type(pr, "string")
    color = get_format(color, typ="color")
    return color


def get_IntRangeSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    pr = get_range(pr, is_type="integer")
    return pr


def get_FloatRangeSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    pr = get_range(pr, is_type="number")
    return pr


def get_Object(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    object_ = get_type(pr, "object")
    if len(object_) > 0:  # what is this for?
        pr_ = list(object_.values())[0]
    else:
        pr_ = []

    return object_


def get_Array(pr, rename_keys=True):
    """
    get arrays. filters out numeric ranges which are handled by:
    - get_IntRangeSlider
    - get_FloatRangeSlider
    """
    pr = drop_explicit_autoui(pr)
    rng = get_range(pr, is_type="numeric")
    arr = get_type(pr, "array")

    return {k: v for k, v in arr.items() if k not in rng.keys()}


def get_AutoOveride(pr, rename_keys=True):
    pr = find_explicit_autoui(pr)
    return pr
#  ----------------------------------------------------------

#  -- WIDGET MAPPING ----------------------------------------
#  -- uses filter functions to map schema objects to widgets
def auto_overide(str_widget_type):
    if type(str_widget_type) == str:
        return obj_from_importstr(str_widget_type)
    else:
        return str_widget_type


class AutoIpywidgetPlaceholder(widgets.Textarea):
    def __init__(self, schema):
        txt = f"""
placeholder widget for object type: 

schema: 
{str(schema)}
"""
        super().__init__(value=txt)


class AutoArrayPlaceholder(widgets.Textarea):
    def __init__(self, schema):
        txt = f"""
placeholder widget for array type: 

schema: 
{str(schema)}
"""
        super().__init__(value=txt)


class WidgetMapper(BaseModel):
    """defines a filter function and associated widget. the "fn_filt" is used to search the
    json schema to find appropriate objects, the objects are then passed to the "widget" for the ui
    """
    fn_filt: typing.Callable
    widget: typing.Callable


class WidgetCaller(BaseModel):
    schema_: typing.Dict
    autoui: typing.Callable  # TODO: change name autoui --> widget
    #mvalue: typing.Any = None  # TODO: add functionality to add value. (don't think this is required...)


def widgetcaller(caller: WidgetCaller):
    """
    returns widget from widget caller object
    Args:
        caller: WidgetCaller
    Returns:
        widget of some kind
    """
    # if type(caller.autoui) == str:  # object_from_string ?

    try:
        # args = inspect.getfullargspec(cl).args
        # kw = {k_: v_ for k_, v_ in v.items() if k_ in args}
        # ^ do this if required (get allowed args from class)

        w = caller.autoui(caller.schema_)

    except:
        txt = f"""
error building widget: {str(caller.autoui)}
from schema: 
{str(caller.schema_)}
"""
        # TODO: add logging
        w = widgets.Textarea(txt)
    return w


DI_WIDGETS_MAPPER = frozenmap(
    **{
        "IntText": WidgetMapper(fn_filt=get_IntText, widget=auiwidgets.IntText),
        "IntSlider": WidgetMapper(fn_filt=get_IntSlider, widget=auiwidgets.IntSlider),
        "FloatText": WidgetMapper(fn_filt=get_FloatText, widget=auiwidgets.FloatText),
        "FloatSlider": WidgetMapper(
            fn_filt=get_FloatSlider, widget=auiwidgets.FloatSlider
        ),
        "IntRangeSlider": WidgetMapper(
            fn_filt=get_IntRangeSlider, widget=auiwidgets.IntRangeSlider
        ),
        "FloatRangeSlider": WidgetMapper(
            fn_filt=get_FloatRangeSlider, widget=auiwidgets.FloatRangeSlider
        ),
        "Text": WidgetMapper(fn_filt=get_Text, widget=auiwidgets.Text),
        "Textarea": WidgetMapper(fn_filt=get_Textarea, widget=auiwidgets.Textarea),
        "Dropdown": WidgetMapper(fn_filt=get_Dropdown, widget=auiwidgets.Dropdown),
        "SelectMultiple": WidgetMapper(
            fn_filt=get_SelectMultiple, widget=auiwidgets.SelectMultiple
        ),
        "Checkbox": WidgetMapper(fn_filt=get_Checkbox, widget=auiwidgets.Checkbox),
        "DatePicker": WidgetMapper(
            fn_filt=get_DatePicker, widget=auiwidgets.DatePicker
        ),
        "DatetimePicker": WidgetMapper(
            fn_filt=get_DatetimePicker, widget=auiwidgets.DatePicker
        ),  # TODO: udpate to DatetimePicker with ipywidgets==8
        "FileChooser": WidgetMapper(fn_filt=get_FileChooser, widget=FileChooser),
        "Grid": WidgetMapper(fn_filt=get_DataGrid, widget=Grid),
        "ColorPicker": WidgetMapper(
            fn_filt=get_ColorPicker, widget=auiwidgets.ColorPicker
        ),
        "AutoOveride": WidgetMapper(
            fn_filt=get_AutoOveride, widget=auto_overide
        ),  # TODO: this should be first...
        "object": WidgetMapper(
            fn_filt=get_Object, widget=AutoIpywidgetPlaceholder
        ),  # AutoIpywidget. gets overridden by AutoIpywidget.
        "array": WidgetMapper(fn_filt=get_Array, widget=AutoArrayPlaceholder),
    }
)


def automapschema(
    schema: typing.Dict, di_widgets_mapper: typing.Dict = None
) -> typing.Dict:
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
    schema = attach_schema_refs(schema, schema_base=schema)

    # checks
    if "type" not in schema.keys():
        raise ValueError('"type" is a required key in schema')
    if schema["type"] != "object":
        raise ValueError(
            'the top level "type" of the schema must be an object (note. this might be a pydantic only requirement...)'
        )

    pr = schema["properties"]
    li_pr = pr.keys()
    di_ = {}
    for k, v in di_widgets_mapper.items():
        di = v.fn_filt(pr)
        for k_, v_ in di.items():
            # print(v_, type(k_))
            tmp = {}
            tmp["schema_"] = v_
            if "autoui" not in v_:
                tmp["autoui"] = v.widget
            else:
                # pass
                tmp["autoui"] = v.widget(v_["autoui"])  # apply autooverride...

            di_[k_] = WidgetCaller(**tmp)
    not_matched = set(di_.keys()) ^ set(li_pr)
    if len(not_matched) > 0:
        print(
            "the following UI items from schema not matched to a widget:"
        )  # TODO: add logging!
        print(not_matched)
    li_ordered = [l for l in li_pr if l not in not_matched]
    di_ordered = {l: di_[l] for l in li_ordered}
    return di_ordered


if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic, TestAutoLogicSimple, TestArrays
    from ipyautoui.autoipywidget import AutoIpywidget

    # sch = deepcopy(TestArrays().schema())
    # sch = deepcopy(TestAutoLogic().schema())
    # sch = deepcopy(TestAutoLogicSimple().schema())
    # sch = deepcopy(TestObjects().schema())
    sch = deepcopy(TestAutoLogic().schema())
    pr = automapschema(sch)
# -

if __name__ == "__main__":
    display(widgets.VBox([widgetcaller(v) for k, v in pr.items()]))


