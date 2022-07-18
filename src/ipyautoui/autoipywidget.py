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
import logging
import functools
import ipywidgets as widgets
from IPython.display import display
import traitlets
import traitlets_paths

# TODO: Tasks pending completion -@jovyan at 7/18/2022, 2:07:55 PM
# use traitlets_paths or not... pull request to main traitlets?
import typing
from ipyautoui.constants import load_test_constants

#  from ipyautoui.custom.iterable import AutoArray
import ipyautoui.automapschema as aumap
import immutables
import inspect

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


def _init_widgets_and_rows(
    pr: typing.Dict,
) -> tuple((typing.List[widgets.HBox], typing.Dict)):
    """initiates widget for from dict built from schema

    Args:
        pr (typing.Dict): schema properties - sanitised for ipywidgets

    Returns:
        (widgets.VBox, typing.Dict): box with widgets, di of widgets
    """

    def _init_widget(v):
        return aumap.widgetcaller(v)

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
    rows = []
    for (k, v), (k2, v2) in zip(di_widgets.items(), labels.items()):
        rows.append(widgets.HBox([v, v2]))
    return rows, di_widgets


# + tags=[]
def _get_value_trait(obj_with_traits):
    """gets the trait type for a given object (looks for "_value" and 
    "value" allowing use of setters and getters)

    Args:
        obj_with_traits (traitlets.Type): obj with traits

    Raises:
        ValueError: if "_value" or "value" traits don't exist

    Returns:
        typing.Type: trait type of traitlet
    """
    if "_value" in obj_with_traits.traits().keys():
        return obj_with_traits.traits()["_value"]
    elif "value" in obj_with_traits.traits().keys():
        return obj_with_traits.traits()["value"]
    else:
        raise ValueError(
            f"{str(type(obj_with_traits))}: has no '_value' or 'value' trait"
        )


def _init_model_schema(schema):
    if type(schema) == dict:
        model = None  # jsonschema_to_pydantic(schema)  # TODO: do this!
    else:
        model = schema  # the "model" passed is a pydantic model
        schema = model.schema(by_alias=False)
    return model, schema


def add_fdir_to_widgetcaller(caller, fdir: str):  #: aumap.WidgetCaller
    """_summary_

    Args:
        caller (_type_): _description_
        fdir (str): _description_

    Raises:
        ValueError: _description_

    Example:
        >>> import ipyautoui.automapschema as aumap
        >>> from ipyautoui.autowidgets import Text
        >>> caller = aumap.WidgetCaller(schema_={'title': 'Test', 'type': 'object', 'properties': {'string': {'title': 'String','default': 'asdf','type': 'string'}}}, autoui=Text)
        >>> add_fdir_to_widgetcaller(caller, '.').kwargs
        {}
    """
    if isinstance(caller, aumap.WidgetCaller):
        if "fdir" in inspect.getfullargspec(caller.autoui).args:
            caller.kwargs = {"fdir": fdir}
            return caller
        else:
            return caller
    else:
        raise ValueError(f"ERROR add_fdir_to_widgetcallers self.fdir = {fdir}")


class AutoObject(widgets.VBox):
    """creates an ipywidgets form from a json-schema or pydantic model"""

    _value = traitlets.Dict(allow_none=True)
    fdir = traitlets.Unicode(allow_none=True)

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

    def __init__(self, schema, value=None, update_map_widgets=None, fdir=None):
        """creates a widget input form from schema

        Args:
            schema (dict): json schema defining widget to generate
            value (dict, optional): value of json. Defaults to None.
            update_map_widgets (frozenmap, optional): frozen dict of widgets to map to schema items. Defaults to None.
            fdir (path, optional): fdir to work from. useful for widgets that link to files. Defaults to None.

        Returns: 
            AutoIpywidget(widgets.VBox)
        """

        self.update_map_widgets = update_map_widgets
        self.fdir = fdir
        self._init_ui(schema)
        if value is not None:
            self.value = value

    def _init_ui(self, schema):
        self._init_schema(schema)
        self._init_form()
        self._init_controls()

    def _init_schema(self, schema):
        self.model, schema = _init_model_schema(schema)
        self.schema = aumap.attach_schema_refs(schema)
        if "type" not in self.schema.keys() and self.schema["type"] != "object":
            raise ValueError(
                '"type" must be in schema keys and "type" must == "object"'
            )
        pr = schema["properties"]
        self.pr = {
            k: aumap.map_widget(v, widgets_map=self.widgets_map) for k, v in pr.items()
        }
        if self.fdir is not None:
            for v in self.pr.values():
                v = add_fdir_to_widgetcaller(v, self.fdir)

    def _init_form(self):
        super().__init__(
            layout=widgets.Layout(
                width="100%",
                display="flex",
                flex="flex-grow",
                border="solid LemonChiffon 2px",
            )
        )
        self.children, self.di_widgets = _init_widgets_and_rows(self.pr)
        self._value = self.di_widgets_value
        self._update_widgets_from_value()

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
        self._value = self.di_widgets_value
        # NOTE: it is required to set the whole "_value" otherwise
        # traitlets doesn't register the change. -@jovyan at 7/18/2022, 12:45:48 PM

    def _update_widgets_from_value(self):
        for k, v in self.value.items():
            if k in self.di_widgets.keys():
                if v is None:
                    v = _get_value_trait(self.di_widgets[k]).default()
                self.di_widgets[k].value = v
            else:
                logging.critical(
                    f"no widget created for {k}, with value {str(v)}. fix this in the schema! TODO: fix the schema reader and UI to support nesting. or use ipyvuetify"
                )

    @property
    def di_widgets_value(self):
        return {k: v.value for k, v in self.di_widgets.items()}

    def disable_edits(self):
        for k, v in self.di_widgets.items():
            try:
                v.disabled = True
            except:
                pass

    @property
    def update_map_widgets(self):
        return self._update_map_widgets

    @update_map_widgets.setter
    def update_map_widgets(self, value):
        self._update_map_widgets = value
        self.widgets_map = aumap.widgets_map(value)


class AutoIpywidget(widgets.VBox):
    fdir = traitlets.Unicode(allow_none=True)
    # TODO: Tasks pending completion -@jovyan at 7/18/2022, 2:06:04 PM
    # consider changing name `update_map_widgets` to `update_widgets_mapper`
    def __init__(self, schema, value=None, update_map_widgets=None, fdir=None):
        self.update_map_widgets = update_map_widgets
        self.fdir = fdir
        self._init_ui(schema)
        if value is not None:
            self.value = value
        else:
            self._on_change("change")

    @property
    def update_map_widgets(self):
        return self._update_map_widgets

    @update_map_widgets.setter
    def update_map_widgets(self, value):
        self._update_map_widgets = value
        self.widgets_map = aumap.widgets_map(value)

    def _init_ui(self, schema):
        self._init_schema(schema)
        self._init_form()
        self._init_trait()
        self._init_controls()

    def _init_trait(self):
        # NOTE: see test for add_traits that demos usage  -@jovyan at 7/18/2022, 12:11:39 PM
        # https://github.com/ipython/ipython/commit/5105f02df27456cc54867dfbe4cef60d91021f92
        trait_type = type(_get_value_trait(self.autowidget))
        self.add_traits(**{"_value": trait_type()})

    def _init_schema(self, schema):
        self.model, schema = _init_model_schema(schema)
        self.schema = aumap.attach_schema_refs(schema)
        self.caller = aumap.map_widget(schema, widgets_map=self.widgets_map)
        if self.fdir is not None:
            v = add_fdir_to_widgetcaller(caller=self.caller, fdir=self.fdir)

    def _init_form(self):
        super().__init__(
            layout=widgets.Layout(width="100%", display="flex", flex="flex-grow")
        )
        self.autowidget = aumap.widgetcaller(self.caller)
        self.children = [self.autowidget]

    def _init_controls(self):
        if self.autowidget.has_trait("value"):
            self.autowidget.observe(self._on_change, "value")
        elif self.autowidget.has_trait("_value"):
            self.autowidget.observe(self._on_change, "_value")
        else:
            pass

    def _on_change(self, change):
        self._value = self.autowidget.value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.autowidget.value = value


# -
if __name__ == "__main__":
    import doctest

    doctest.testmod()

# if __name__ == "__main__":
#     from ipyautoui.test_schema import TestAutoLogic
#     from ipyautoui.constants import load_test_constants

#     test_constants = load_test_constants()
#     test = TestAutoLogic()
#     schema = test.schema()
#     ui = AutoIpywidget(schema)
#     display(ui)

# if __name__ == "__main__":
#     from ipyautoui.test_schema import TestArrays
#     from ipyautoui.constants import load_test_constants

#     test_constants = load_test_constants()
#     test = TestArrays()
#     schema = test.schema()
#     ui = AutoIpywidget(schema)
#     display(ui)
