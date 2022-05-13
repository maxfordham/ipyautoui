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

import functools
import ipywidgets as widgets
from IPython.display import display
import traitlets
import typing
from ipyautoui.constants import load_test_constants
#  from ipyautoui.custom.iterable import AutoArray
from ipyautoui.automapschema import automapschema, widgetcaller, MAP_WIDGETS
import immutables

frozenmap = immutables.Map

# +


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
    """creates an ipywidgets form from a json-schema or pydantic model"""

    _value = traitlets.Dict(allow_none=True)

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
        self, schema, value=None, widgets_mapper=None,
    ):
        self.widgets_mapper = widgets_mapper
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
        # self._init_titlebox()
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
        #         self.ui_header = widgets.VBox()
        #         self.ui_main = widgets.VBox()

        #         self.ui_titlebox = widgets.VBox()
        #         self.ui_header.children = [self.ui_titlebox]

        #         self.ui_box, self.di_widgets = _init_widgets_and_rows(self.pr)
        #         self._value = self.di_widgets_value
        #         self.ui_main.children = [self.ui_box]
        #         self.children = [self.ui_header, self.ui_main]
        #         self._update_widgets_from_value()
        self.ui_main = widgets.VBox()
        self.ui_widgets, self.di_widgets = _init_widgets_and_rows(self.pr)
        self.ui_main.children = [
            self.ui_widgets
        ]  # note. box in box to allow for ui_main to be swapped to raw
        self._value = self.di_widgets_value
        self.children = [self.ui_main]
        self._update_widgets_from_value()

    @property
    def di_widgets_value(self):
        return {k: v.value for k, v in self.di_widgets.items()}

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

    def _watch_change(self, change, key=None, watch="value"):
        # tmp = self._value.copy()
        # tmp[key] = getattr(self.di_widgets[key], watch)
        # self._value = tmp

        self._value = self.di_widgets_value
        #  note. it is required to .copy the _value and then set it again
        #        otherwise traitlets doesn't register the change.


# -
if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.constants import load_test_constants

    test_constants = load_test_constants()
    test = TestAutoLogic()
    sch = test.schema()
    ui = AutoIpywidget(sch)
    display(ui)

if __name__ == "__main__":
    from ipyautoui.test_schema import TestArrays
    from ipyautoui.constants import load_test_constants

    test_constants = load_test_constants()
    test = TestArrays()
    sch = test.schema()
    ui = AutoIpywidget(sch)
    display(ui)
