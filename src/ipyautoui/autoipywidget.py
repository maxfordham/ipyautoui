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
# TODO: add ipyvuetify-jsonschema to this repo
"""autoui is used to automatically create ipywidget user input (UI) form from a pydantic schema.

This module maps the pydantic fields to appropriate widgets based on type to display the data in the UI.
It also supports extension, but mapping custom datatypes onto custom widget classes.
This information can also be stored to file.

Example:
    see example for a pydantic schema that can be automatically converted into a 
    ipywidgets UI. Currently nesting is not supported::
    
        from ipyautoui.constants import DISPLAY_AUTOUI_SCHEMA_EXAMPLE
        DISPLAY_AUTOUI_SCHEMA_EXAMPLE()
"""
# %run __init__.py
# %load_ext lab_black
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

from ipyautoui._utils import (
    obj_from_string,
    display_pydantic_json,
    file,
    obj_from_importstr,
)
from ipyautoui.custom import Grid, FileChooser, SaveButtonBar
from ipyautoui.constants import DI_JSONSCHEMA_WIDGET_MAP, BUTTON_WIDTH_MIN
from ipyautoui.constants import load_test_constants
from ipyautoui.test_schema import TestAutoLogic
import immutables

frozenmap = immutables.Map
# -

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.constants import load_test_constants

    test_constants = load_test_constants()
    test = TestAutoLogic()
    sch = test.schema()


# +
# sch
# -

def display_template_ui_model():
    from ipyautoui import test_schema

    display(PreviewPy(test_schema, docstring_priority=False))


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

#  -- CHANGE JSON-SCHEMA KEYS TO IPYWIDGET KEYS -------------
def update_key(key, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    if key in di_map.keys():
        return di_map[key]
    else:
        return key


def update_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP, ignore_description=False):
    if ignore_description:
        return {
            update_key(k, di_map): v for k, v in di.items() if k != "description"
        }  # TODO: make this work!
    else:
        return {update_key(k, di_map): v for k, v in di.items()}


def add_description_field(di):
    for k, v in di.items():
        if "description" not in v:
            v["description"] = ""
        # t=v['title']
        # d=v['description']
        # v['description'] = f"<b>{t}</b>, <i>{d}</i>"

    return di


def rename_schema_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    di = add_description_field(di)
    rename = {}
    for k, v in di.items():
        if v["type"] == "object":
            rename[k] = update_keys(v, di_map, ignore_description=True)
        else:
            rename[k] = update_keys(v, di_map)

    rename = {k: update_keys(v, di_map) for k, v in di.items()}
    return rename


def call_rename_schema_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP, rename_keys=True):
    if rename_keys:
        return rename_schema_keys(di, di_map=di_map)
    else:
        return di


#  ----------------------------------------------------------

#  -- HELPER FUNCTIONS --------------------------------------
def get_type(pr, typ="string"):
    return {k: v for k, v in pr.items() if v["type"] == typ}


def get_format(pr, typ="date"):
    pr = {k: v for k, v in pr.items() if "format" in v}
    return {k: v for k, v in pr.items() if v["format"] == typ}


def get_range(pr, typ="integer"):
    """finds numeric range within schema properties. a range in json must satisfy these criteria:
    - check1: array length == 2
    - check2: minimum and maximum values must be given
    - check3: check numeric typ given (i.e. integer or number)
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

    #  check3: check numeric typ given (i.e. integer or number)
    rng = {k: v for k, v in tmp.items() if v["items"][0]["type"] == typ}
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
    return call_rename_schema_keys(simple_ints, rename_keys=rename_keys)


def get_IntSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    ints = get_type(pr, typ="integer")
    simple_ints = {k: v for k, v in ints.items() if "minimum" in v and "maximum" in v}
    return call_rename_schema_keys(simple_ints, rename_keys=rename_keys)


def get_FloatText(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    floats = get_type(pr, typ="number")
    simple_floats = {
        k: v for k, v in floats.items() if "minimum" not in v and "maximum" not in v
    }
    return call_rename_schema_keys(simple_floats, rename_keys=rename_keys)


def get_FloatSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    floats = get_type(pr, typ="number")
    simple_floats = {
        k: v for k, v in floats.items() if "minimum" in v and "maximum" in v
    }
    return call_rename_schema_keys(simple_floats, rename_keys=rename_keys)


def get_Text(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    strings = get_type(pr)
    short_strings = drop_enums(strings)
    # short_strings = {k:v for k,v in strings.items() if 'maxLength' in v and v['maxLength']<200}
    return call_rename_schema_keys(short_strings, rename_keys=rename_keys)


def get_Textarea(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    strings = get_type(pr)
    simple_strings = drop_enums(strings)
    long_strings = {
        k: v for k, v in strings.items() if "maxLength" in v and v["maxLength"] >= 200
    }
    return call_rename_schema_keys(long_strings, rename_keys=rename_keys)


def get_Dropdown(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    drops = find_enums(pr)
    drops = {k: v for k, v in drops.items() if v["type"] != "array"}
    return call_rename_schema_keys(drops, rename_keys=rename_keys)


def get_SelectMultiple(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    mult = find_enums(pr)
    mult = {k: v for k, v in mult.items() if v["type"] == "array"}
    return call_rename_schema_keys(mult, rename_keys=rename_keys)


def get_Checkbox(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    return call_rename_schema_keys(get_type(pr, typ="boolean"), rename_keys=rename_keys)


def get_DatePicker(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    date = get_type(pr, "string")
    date = get_format(date)
    for k, v in date.items():
        if type(v["default"]) == str:
            v["default"] = datetime.strptime(v["default"], "%Y-%m-%d").date()
    return call_rename_schema_keys(date, rename_keys=rename_keys)


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
    return call_rename_schema_keys(date, rename_keys=rename_keys)


def get_FileChooser(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    file = get_type(pr, "string")
    file = get_format(file, typ="path")
    return call_rename_schema_keys(file, rename_keys=rename_keys)


def get_DataGrid(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    grid = get_type(pr, "string")
    grid = get_format(grid, typ="DataFrame")
    return call_rename_schema_keys(grid, rename_keys=rename_keys)


def get_ColorPicker(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    color = get_type(pr, "string")
    color = get_format(color, typ="color")
    return call_rename_schema_keys(color, rename_keys=rename_keys)


def get_IntRangeSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    pr = get_range(pr, typ="integer")
    return call_rename_schema_keys(pr, rename_keys=rename_keys)


def get_FloatRangeSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    pr = get_range(pr, typ="number")
    return call_rename_schema_keys(pr, rename_keys=rename_keys)


def get_Object(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    object_ = get_type(pr, "object")
    if len(object_) > 0:  # what is this for?
        pr_ = list(object_.values())[0]
    else:
        pr_ = []

    return object_


def get_Array(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    arr = get_type(pr, "array")
    return arr


def get_AutoOveride(pr, rename_keys=True):
    pr = find_explicit_autoui(pr)
    return call_rename_schema_keys(pr, rename_keys=rename_keys)


#  ----------------------------------------------------------

#  -- WIDGET MAPPING ----------------------------------------
#  -- uses filter functions to map schema objects to widgets
def auto_overide(str_widget_type):
    if type(str_widget_type) == str:
        return obj_from_importstr(str_widget_type)
    else:
        return str_widget_type


class AutoIpywidgetPlaceholder:
    pass


class AutoArrayPlaceholder:
    pass


class WidgetMapper(BaseModel):
    """defines a filter function and associated widget. the "fn_filt" is used to search the
    json schema to find appropriate objects, the objects are then passed to the "widget" for the ui
    """

    fn_filt: typing.Callable
    widget: typing.Callable


DI_WIDGETS_MAPPER = frozenmap(
    **{
        "IntText": WidgetMapper(fn_filt=get_IntText, widget=widgets.IntText),
        "IntSlider": WidgetMapper(fn_filt=get_IntSlider, widget=widgets.IntSlider),
        "FloatText": WidgetMapper(fn_filt=get_FloatText, widget=widgets.FloatText),
        "FloatSlider": WidgetMapper(
            fn_filt=get_FloatSlider, widget=widgets.FloatSlider
        ),
        "Text": WidgetMapper(fn_filt=get_Text, widget=widgets.Text),
        "Textarea": WidgetMapper(fn_filt=get_Textarea, widget=widgets.Textarea),
        "Dropdown": WidgetMapper(fn_filt=get_Dropdown, widget=widgets.Dropdown),
        "SelectMultiple": WidgetMapper(
            fn_filt=get_SelectMultiple, widget=widgets.SelectMultiple
        ),
        "Checkbox": WidgetMapper(fn_filt=get_Checkbox, widget=widgets.Checkbox),
        "DatePicker": WidgetMapper(fn_filt=get_DatePicker, widget=widgets.DatePicker),
        "DatetimePicker": WidgetMapper(
            fn_filt=get_DatetimePicker, widget=widgets.DatePicker
        ),  # TODO: udpate to DatetimePicker with ipywidgets==8
        "FileChooser": WidgetMapper(fn_filt=get_FileChooser, widget=FileChooser),
        "Grid": WidgetMapper(fn_filt=get_DataGrid, widget=Grid),
        "ColorPicker": WidgetMapper(
            fn_filt=get_ColorPicker, widget=widgets.ColorPicker
        ),
        "AutoOveride": WidgetMapper(
            fn_filt=get_AutoOveride, widget=auto_overide
        ),  # TODO: this should be first...
        "object": WidgetMapper(
            fn_filt=get_Object, widget=AutoIpywidgetPlaceholder
        ),  # AutoIpywidget. gets overridden by AutoIpywidget.
        "array": WidgetMapper(fn_filt=get_Array, widget=AutoArrayPlaceholder),
        "IntRangeSlider": WidgetMapper(
            fn_filt=get_IntRangeSlider, widget=widgets.IntRangeSlider
        ),
        "FloatRangeSlider": WidgetMapper(
            fn_filt=get_FloatRangeSlider, widget=widgets.FloatRangeSlider
        ),
    }
)


def map_to_widget(
    sch: typing.Dict, di_widgets_mapper: typing.Dict = None
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
    sch = attach_schema_refs(sch, schema_base=sch)
    if "properties" in sch.keys():
        pr = sch["properties"]
    else:
        # often true when items of array
        pr = sch
    li_pr = pr.keys()
    di_ = {}
    for k, v in di_widgets_mapper.items():
        di = v.fn_filt(pr)
        # if "type" in di.keys():
        #     v.widget
        for k_, v_ in di.items():
            di_[k_] = v_
            if "autoui" not in v_:
                di_[k_]["autoui"] = v.widget
            else:
                # pass
                di_[k_]["autoui"] = v.widget(v_["autoui"])  # apply autooverride...
    not_matched = set(di_.keys()) ^ set(li_pr)
    if len(not_matched) > 0:
        print(
            "the following UI items from schema not matched to a widget:"
        )  # TODO: add logging!
        print(not_matched)
    li_ordered = [l for l in li_pr if l not in not_matched]
    di_ordered = {l: di_[l] for l in li_ordered}
    return di_ordered


# -
from ipyautoui.test_schema import TestObjects

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic, TestObjects, TestArrays
    from ipyautoui.constants import load_test_constants
    from copy import copy

    test_constants = load_test_constants()
    test = TestArrays()
    sch = copy(test.schema())

    def widgets_mapper(value=None):
        if value is None:
            _widgets_mapper = dict(DI_WIDGETS_MAPPER)
        autonested = functools.partial(AutoIpywidget, show_raw=False)
        autoarray = functools.partial(AutoArray)
        _widgets_mapper["object"].widget = autonested
        _widgets_mapper["array"].widget = autoarray
        return _widgets_mapper

    di_widgets_mapper = widgets_mapper()

    sch = attach_schema_refs(sch, schema_base=sch)
    pr = map_to_widget(sch, di_widgets_mapper=di_widgets_mapper)
    box, di_widgets = _init_widgets_and_rows(pr)
    [display(v) for k, v in di_widgets.items()]

if __name__ == "__main__":
    arr = di_widgets["array_strings"]
    AutoArray(arr.schema).items
    arr.schema
    arr.fn_add()

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.constants import load_test_constants

    test_constants = load_test_constants()
    test = TestAutoLogic()
    sch = test.schema()

    # key = "$ref"
    # sch = update_property_definitions(sch, key)
    # pr = map_to_widget(sch)


def _init_widgets_and_rows(pr: typing.Dict) -> tuple((widgets.VBox, typing.Dict)):
    """initiates widget for from dict built from schema

    Args:
        pr (typing.Dict): schema properties - sanitised for ipywidgets

    Returns:
        (widgets.VBox, typing.Dict): box with widgets, di of widgets
    """

    def _init_widget(v):
        if v["type"] == "object":
            return v["autoui"](v)
        elif v["type"] == "array":
            return v["autoui"](v)
        else:
            try:
                kw = v
                return v["autoui"](**kw)
            except:
                cl = v["autoui"]
                args = inspect.getfullargspec(cl).args
                kw = {k_: v_ for k_, v_ in v.items() if k_ in args}
                # print(kw)
                return cl(**kw)

    di_widgets = {k: _init_widget(v) for k, v in pr.items()}
    # return di_widgets
    labels = {}
    for k, v in pr.items():
        try:
            l = widgets.HTML(f"<b>{v['title']}</b>, <i>{v['autoui_description']}</i>")
        except:
            l = widgets.HTML("")
        labels[k] = l
    ui_box = widgets.VBox()
    rows = []
    for (k, v), (k2, v2) in zip(di_widgets.items(), labels.items()):
        rows.append(widgets.HBox([v, v2]))
    ui_box.children = rows
    # ui_box.layout = {'border': 'solid yellow'}
    return ui_box, di_widgets


# +
# handler - decides what to do given set of inputs UiFromSchema - generates ui from jsonschema
# -

from ipyautoui.custom.iterable_1 import AutoArray


# + tags=[]
def _get_value_trait(widget):
    """looks for a value or _value trait on widget (allowing setters and getters to be used on value)"""
    if "_value" in widget.traits().keys():
        return widget.traits()["_value"]
    elif "value" in widget.traits().keys():
        return widget.traits()["value"]
    else:
        raise ValueError("no value (or _value) trait found")


class AutoIpywidget(widgets.VBox): #, traitlets.HasTraits
    _value = traitlets.Dict()

    @traitlets.validate("_value")
    def _valid_value(self, proposal):
        return proposal["value"]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if hasattr(self, "di_widgets"):
            self._update_widgets_from_value()

    def __init__(
        self,
        schema,
        value=None,
        show_raw=True,  # TODO: remove this
        widgets_mapper=None,
    ):
        self.widgets_mapper = widgets_mapper
        self.show_raw = show_raw
        self._init_ui(schema)
        if value is not None:
            self.value = value

    @property
    def widgets_mapper(self):
        return self._widgets_mapper

    @widgets_mapper.setter
    def widgets_mapper(self, value):
        if value is None:
            self._widgets_mapper = dict(DI_WIDGETS_MAPPER)
        autonested = functools.partial(AutoIpywidget, show_raw=False)
        autoarray = AutoArray
        self._widgets_mapper["object"].widget = autonested
        self._widgets_mapper["array"].widget = autoarray

    def _init_ui(self, schema):
        self._init_schema(schema)
        self._init_form()
        self._init_titlebox()
        self._init_controls()

    def _init_schema(self, schema):
        self.sch = attach_schema_refs(schema, schema_base=schema)
        self.pr = map_to_widget(self.sch, di_widgets_mapper=self.widgets_mapper)

    def _update_widgets_from_value(self):
        for k, v in self.value.items():
            if k in self.di_widgets.keys():
                if v is None:
                    v = _get_value_trait(self.di_widgets[k]).default()
                self.di_widgets[k].value = v
            else:
                print(
                    f"no widget created for {k}. fix this in the schema! TODO: fix the schema reader and UI to support nesting. or use ipyvuetify"
                )

    def _init_form(self):
        super().__init__(
            layout=widgets.Layout(
                width="100%",
                display="flex",
                flex="flex-grow",
                border="solid LemonChiffon 2px",
            )
        )  # main container
        self.ui_header = widgets.VBox()
        self.ui_main = widgets.VBox()

        self.ui_titlebox = widgets.VBox()
        self.ui_buttonbar = widgets.HBox()
        self.ui_header.children = [self.ui_buttonbar, self.ui_titlebox]

        self.ui_box, self.di_widgets = _init_widgets_and_rows(self.pr)
        self._value = self.di_widgets_value
        self.ui_main.children = [self.ui_box]
        self.children = [self.ui_header, self.ui_main]
        self._update_widgets_from_value()
        # display(self.ui_main)

    @property
    def di_widgets_value(self):
        return {k: v.value for k, v in self.di_widgets.items()}

    def _init_titlebox(self):
        children = []
        titlebox_children = []
        self.titlebox = widgets.HBox()
        children.append(self.titlebox)

        if self.show_raw:
            self.showraw = widgets.ToggleButton(
                icon="code",
                layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
                tooltip="show raw data",
                style={"font_weight": "bold", "button_color": None},
            )
            titlebox_children.append(self.showraw)
        self.title = widgets.HTML(f"<big><b>{self.sch['title']}</b></big>")
        titlebox_children.append(self.title)
        if "description" in self.sch.keys():
            children.append(widgets.HTML(markdown(f"{self.sch['description']}")))
        self.titlebox.children = titlebox_children
        self.ui_titlebox.children = children

    def disable_edits(self):
        for k, v in self.di_widgets.items():
            try:
                v.disabled = True
            except:
                pass

    def _init_controls(self):
        for k, v in self.di_widgets.items():
            if v.has_trait("value"):
                v.observe(
                    functools.partial(self._watch_change, key=k, watch="value"), "value"
                )
            elif v.has_trait("_value"):
                v.observe(
                    functools.partial(self._watch_change, key=k, watch="_value"),
                    "_value",
                )
            else:
                pass
        if self.show_raw:
            self.showraw.observe(self._showraw, "value")

    def _watch_change(self, change, key=None, watch="value"):
        self._value[key] = getattr(self.di_widgets[key], watch)

    def _showraw(self, onchange):
        if self.showraw.value:
            self.showraw.tooltip = "show user interface"
            self.showraw.icon = "user-edit"
            out = widgets.Output()
            with out:
                display(
                    Markdown(
                        "\n```Python\n"
                        + "#  raw json data of the user input form"
                        + "\n```"
                    )
                )
                display(self.value)
            self.ui_main.children = [out]
        else:
            self.showraw.tooltip = "show raw data"
            self.showraw.icon = "code"
            self.ui_main.children = [self.ui_box]


if __name__ == "__main__":
    ui = AutoIpywidget(sch)
    display(ui)
# -
if __name__ == "__main__":
    sch = attach_schema_refs(
        ui.sch["properties"]["recursive_nest"]["properties"]["nested"],
        schema_base=ui.sch["properties"]["recursive_nest"]["properties"]["nested"],
    )
    pr = map_to_widget(sch)

    sch

    sch

    AutoIpywidget(schema=ui.sch["properties"]["recursive_nest"]["properties"]["nested"])

    schema = {
        "title": "NestedObject",
        "description": "description in docstring",
        "type": "object",
        "properties": {
            "string1": {
                "title": "String1",
                "description": "a description about my string",
                "default": "adsf",
                "type": "string",
            },
            "int_slider1": {
                "title": "Int Slider1",
                "default": 2,
                "minimum": 0,
                "maximum": 3,
                "type": "integer",
                "description": "",
            },
            "int_text1": {
                "title": "Int Text1",
                "default": 1,
                "type": "integer",
                "description": "",
            },
        },
    }

    AutoIpywidget(schema, show_raw=False)


