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
    display_python_string,
)
from ipyautoui.custom import Grid, FileChooser, SaveButtonBar
from ipyautoui.constants import DI_JSONSCHEMA_WIDGET_MAP, BUTTON_WIDTH_MIN
from ipyautoui.constants import load_test_constants
from ipyautoui.test_schema import TestAutoLogic
import immutables

frozenmap = immutables.Map


# -

def display_template_ui_model():
    from ipyautoui import test_schema
    display(PreviewPy(test_schema, docstring_priority=False))


# +
from ipyautoui.custom.iterable import AutoArray
from ipyautoui.automapschema import automapschema, widgetcaller, MAP_WIDGETS


def get_title_description_from_schema(schema):
    if schema["type"] == "array":
        return "", ""
    elif schema["type"] == "object":
        return "", ""
    else:
        if "title" in schema.keys():
            t = schema["title"]
        else:
            t = ""
        if "description" in schema.keys():
            d = schema["description"]
        else:
            d = ""
        return t, d


def _init_widgets_and_rows(pr: typing.Dict) -> tuple((widgets.VBox, typing.Dict)):
    """initiates widget for from dict built from schema

    Args:
        pr (typing.Dict): schema properties - sanitised for ipywidgets

    Returns:
        (widgets.VBox, typing.Dict): box with widgets, di of widgets
    """

    def _init_widget(v):
        return widgetcaller(v)

    di_widgets = {k: _init_widget(v) for k, v in pr.items()}
    # return di_widgets
    labels = {}
    for k, v in pr.items():
        try:
            t, d = get_title_description_from_schema(v.schema_)
            l = widgets.HTML(f"<b>{t}</b>, <i>{d}</i>")
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


# -

class Auto:
    _value = traitlets.Any()
    ui = traitlets.Any()

    def __init__(self, schema):
        self.schema = schema

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = schema
        if hasattr(self, "di_widgets"):
            self._update_widgets_from_value()


class TitleAndToggle(HasTraits):
    show_raw = traitlets.Bool(default=True)


# + tags=[]
def _get_value_trait(widget):
    """looks for a value or _value trait on widget (allowing setters and getters to be used on value)"""
    if "_value" in widget.traits().keys():
        return widget.traits()["_value"]
    elif "value" in widget.traits().keys():
        return widget.traits()["value"]
    else:
        raise ValueError("no value (or _value) trait found")


class AutoIpywidget(widgets.VBox):  # , traitlets.HasTraits
    _value = traitlets.Dict()

    @traitlets.validate("_value")
    def _valid_value(self, proposal):
        return proposal["value"]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """this is for setting the value via the API"""
        self._value = value
        if hasattr(self, "di_widgets"):
            self._update_widgets_from_value()

    def __init__(
        self, schema, value=None, show_raw=False, widgets_mapper=None,
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
            self._widgets_mapper = MAP_WIDGETS  # TODO: maybe this should be a dict

    def _init_ui(self, schema):
        self._init_schema(schema)
        self._init_form()
        self._init_titlebox()
        self._init_controls()

    def _init_schema(self, schema):
        self.sch = schema  # attach_schema_refs(schema, schema_base=schema)
        self.pr = automapschema(self.sch, widget_map=self.widgets_mapper)

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
        self.ui_header.children = [self.ui_titlebox]

        self.ui_box, self.di_widgets = _init_widgets_and_rows(self.pr)
        self._value = self.di_widgets_value
        self.ui_main.children = [self.ui_box]
        self.children = [self.ui_header, self.ui_main]
        self._update_widgets_from_value()

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
        tmp = self._value.copy()
        tmp[key] = getattr(self.di_widgets[key], watch)
        self._value = tmp
        #  note. it is required to .copy the _value and then set it again
        #        otherwise traitlets doesn't register the change.

    def _showraw(self, onchange):
        if self.showraw.value:
            self.showraw.tooltip = "show user interface"
            self.showraw.icon = "user-edit"
            out = widgets.Output()
            with out:
                display(display_python_string(json.dumps(self.value, indent=4)))
            self.ui_main.children = [out]
        else:
            self.showraw.tooltip = "show raw data"
            self.showraw.icon = "code"
            self.ui_main.children = [self.ui_box]


# -
if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.constants import load_test_constants

    test_constants = load_test_constants()
    test = TestAutoLogic()
    sch = test.schema()
    ui = AutoIpywidget(sch, show_raw=True)
    display(ui)

if __name__ == "__main__":
    from ipyautoui.test_schema import TestArrays
    from ipyautoui.constants import load_test_constants

    test_constants = load_test_constants()
    test = TestArrays()
    sch = test.schema()
    ui = AutoIpywidget(sch, show_raw=True)
    display(ui)


