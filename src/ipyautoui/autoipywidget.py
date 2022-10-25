# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.8
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
import traitlets as tr

# TODO: Tasks pending completion -@jovyan at 7/18/2022, 2:07:55 PM
# use traitlets_paths or not... pull request to main traitlets?
import typing
from ipyautoui.constants import DOWNARROW_BUTTON_KWARGS

from ipyautoui.custom.showhide import ShowHide
import ipyautoui.automapschema as aumap
import immutables
import inspect

frozenmap = immutables.Map


# +
def _init_widgets_and_labels(
    pr: typing.Dict,
) -> tuple((typing.List[widgets.HBox], typing.Dict)):
    """initiates widget for from dict built from schema

    Args:
        pr (typing.Dict): schema properties - sanitised for ipywidgets

    Returns:
        (widgets.VBox, typing.Dict): box with widgets, di of widgets
    """

    _init_widget = lambda v: aumap.widgetcaller(v)
    _make_label = lambda title, description: f"<b>{title}</b>, <i>{description}</i>"
    _get = lambda schema, var: schema[var] if var in schema.keys() else ""

    di_widgets = {k: _init_widget(v) for k, v in pr.items()}
    di_labels = {
        k: _make_label(_get(v.schema_, "title"), _get(v.schema_, "description"))
        for k, v in pr.items()
    }

    return di_labels, di_widgets


def _init_model_schema(schema, by_alias=False):
    if type(schema) == dict:
        model = None  # jsonschema_to_pydantic(schema)
        # IDEA: Possible implementations -@jovyan at 8/24/2022, 12:05:02 PM
        # jsonschema_to_pydantic
        # https://koxudaxi.github.io/datamodel-code-generator/using_as_module/
    else:
        model = schema  # the "model" passed is a pydantic model
        schema = model.schema(by_alias=by_alias).copy()

    schema = aumap.attach_schema_refs(schema)
    return model, schema


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


def horizontal_row_nested(widget, label, auto_open=False):
    # BUG: Reported defects -@jovyan at 8/23/2022, 10:30:52 PM
    # ^ buggy behaviour associated to ShowHide class for nested objects observed in
    # example form linked to `horizontal_row_nested`
    return ShowHide(
        fn_display=lambda: widget,
        title=label,
        auto_open=auto_open,
        button_width="300px",
    )


def horizontal_row_simple(widget, label):
    return widgets.HBox([widget, widgets.HTML(label)])


def vertical_row(widget, label, auto_open=None):
    return widgets.VBox(
        [
            widgets.HTML(label),
            widgets.HBox([widgets.HBox(layout={"width": "40px"}), widget]),
        ]
    )


def create_row(
    widget, label, align_horizontal=True, auto_open=False, nested_widgets=None
):
    """creates a row for a given widget. applies

    Args:
        widget (_type_): _description_
        label (_type_): _description_
        align_horizontal (bool, optional): _description_. Defaults to True.
        auto_open (bool, optional): _description_. Defaults to False.
        nested_widgets (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: a widget box that is added to the list of children in AutoObject
    """
    if nested_widgets is None:
        nested_widgets = []
    if align_horizontal:
        if True in [isinstance(widget, w) for w in nested_widgets]:
            return horizontal_row_nested(widget, label, auto_open=auto_open)
        else:
            return horizontal_row_simple(widget, label)
    else:
        return vertical_row(widget, label)


class AutoObject(widgets.VBox):
    """creates an ipywidgets form from a json-schema or pydantic model. datatype must be "object" """

    _value = traitlets.Dict(allow_none=True)
    fdir = traitlets.Unicode(allow_none=True)
    align_horizontal = traitlets.Bool(default_value=True)
    auto_open = traitlets.Bool(default_value=False)
    nested_widgets = traitlets.List()
    order = traitlets.List(default_value=None, allow_none=True)
    insert_rows = traitlets.Dict(default_value=None, allow_none=True)

    @traitlets.validate("insert_rows")
    def _insert_rows(self, proposal):
        fn_checkisintkeys = (
            lambda di: True
            if [isinstance(l, int) == True for l in di.keys()]
            else False
        )
        v = proposal["value"]
        if v is None:
            return None
        else:
            if not isinstance(v, dict):
                raise ValueError("insert_rows must be a dict")
            if not fn_checkisintkeys(v):
                raise ValueError("keys of insert_rows must be integers")
        return v

    @traitlets.validate("order")
    def _order(self, proposal):
        v = proposal["value"]
        if v is None:
            return None
        else:
            if set(self.default_order) != set(v):
                raise ValueError("set(self.default_order) != set(proposal['value'])")
        return v

    @traitlets.default("nested_widgets")
    def _default_nested_widgets(self):
        from ipyautoui.autowidgets import AutoMarkdown  # , EditGrid
        from ipyautoui.custom.iterable import AutoArray
        from ipyautoui.custom.editgrid import EditGrid  # as EditGridCore
        from ipyautoui import AutoUi

        default_nested = [
            AutoIpywidget,
            AutoArray,
            AutoMarkdown,
            EditGrid,
            AutoUi,
            AutoObject,
        ]
        return default_nested

    @traitlets.validate("nested_widgets")
    def _valid_nested_widgets(self, proposal):
        return proposal["value"]

    @traitlets.validate("_value")
    def _valid_value(self, proposal):
        return proposal["value"]

    @property
    def default_order(self):
        return list(self.di_widgets.keys())

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
        self,
        schema,
        value=None,
        by_alias=False,
        update_map_widgets=None,
        fdir=None,
        order=None,
        insert_rows=None,
        nested_widgets=None,
    ):
        """creates a widget input form from schema. datatype must be "object"

        Args:
            schema (dict): json schema defining widget to generate
            value (dict, optional): value of json. Defaults to None.
            update_map_widgets (frozenmap, optional): frozen dict of widgets to map to schema items. Defaults to None.
            fdir (path, optional): fdir to work from. useful for widgets that link to files. Defaults to None.
            order (list): allows user to re-specify the order for widget rows to appear by key name in self.di_widgets
            insert_rows (dict): e.g. {3:widgets.Button()}. allows user to insert a widget into the rows. its presence
                is ignored by the widget otherwise.
            nested_widgets (list): e.g. [FileUploadToDir]. allows user to indicate widgets that should be show / hide
                type

        Returns:
            AutoIpywidget(widgets.VBox)
        """
        setdefault = lambda val, default: default if val is None else val
        self.insert_rows = insert_rows
        self.update_map_widgets = update_map_widgets
        self.fdir = fdir
        self._init_schema(schema, by_alias=by_alias)
        self._init_ui()
        self.order = setdefault(order, None)
        if value is not None:
            self.value = value

    def _init_ui(self):
        self._init_widgets()
        self._init_form()
        self._init_controls()

    def _init_schema(self, schema, by_alias=False):
        self.model, self.schema = _init_model_schema(schema, by_alias=by_alias)
        if "type" not in self.schema.keys() and self.schema["type"] != "object":
            raise ValueError(
                '"type" must be in schema keys and "type" must == "object"'
            )
        pr = self.schema["properties"]
        self.pr = {
            k: aumap.map_widget(v, widgets_map=self.widgets_map) for k, v in pr.items()
        }
        if self.fdir is not None:
            for v in self.pr.values():
                v = add_fdir_to_widgetcaller(v, self.fdir)

    def _init_widgets(self):
        self.di_labels, self.di_widgets = _init_widgets_and_labels(self.pr)
        self._value = self.di_widgets_value
        self._update_widgets_from_value()

    def _init_form(self):
        super().__init__(
            layout=widgets.Layout(
                width="100%",
                display="flex",
                flex="flex-grow",
            )
        )
        self._format_rows()

    def _insert_rows(self):
        if self.insert_rows is not None:
            for k, v in self.insert_rows.items():
                self.rows.insert(k, v)

    def _format_rows(self):
        set_order = lambda _: self.default_order if _ is None else self.order
        order = set_order(self.order)
        self.rows = [
            create_row(
                self.di_widgets[row],
                self.di_labels[row],
                align_horizontal=self.align_horizontal,
                auto_open=self.auto_open,
                nested_widgets=self.nested_widgets,
            )
            for row in order
        ]
        self._insert_rows()
        self.children = self.rows

    def _init_controls(self):
        self._init_watch_widgets()
        self._init_update_row_format()

    def _init_watch_widgets(self):
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

    def _call_format_rows(self, onchange):
        self._format_rows()

    def _init_update_row_format(self):
        self.observe(
            self._call_format_rows,
            names=[
                "align_horizontal",
                "order",
                "auto_open",
                "insert_rows",
                "nested_widgets",
            ],
        )

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
        for v in self.di_widgets.values():
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


# -
class AutoIpywidget(widgets.VBox):
    """Automatically generates the widget based on an input schema"""

    fdir = traitlets.Unicode(allow_none=True)
    # TODO: Tasks pending completion -@jovyan at 7/18/2022, 2:06:04 PM
    # consider changing name `update_map_widgets` to `update_widgets_mapper`

    # TODO: Tasks pending completion -@jovyan at 9/07/2022, 2:06:04 PM
    # consider whether this shouldn't inherit AutoObject afterall...
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
        self.model, self.schema = _init_model_schema(schema)
        self.caller = aumap.map_widget(self.schema, widgets_map=self.widgets_map)
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


if __name__ == "__main__":
    import doctest

    doctest.testmod()

if __name__ == "__main__":
    from ipyautoui.constants import load_test_constants
    from ipyautoui.test_schema import TestAutoLogicSimple

    test_constants = load_test_constants()
    test = TestAutoLogicSimple()
    schema = test.schema()
    ui = AutoObject(schema)
    display(ui)

if __name__ == "__main__":
    display(schema)

if __name__ == "__main__":
    li = ui.default_order.copy()
    li.reverse()
    ui.order = li

if __name__ == "__main__":
    ui.align_horizontal = True

if __name__ == "__main__":
    ui.auto_open = True

# +
# if __name__ == "__main__":
#     from ipyautoui.test_schema import TestAutoLogic
#     from ipyautoui.constants import load_test_constants

#     test_constants = load_test_constants()
#     test = TestAutoLogic()
#     schema = test.schema()
#     ui = AutoIpywidget(schema)
#     display(ui)


# + active=""
# if __name__ == "__main__":
#     from ipyautoui.test_schema import TestArrays
#     from ipyautoui.constants import load_test_constants
#     test_constants = load_test_constants()
#     test = TestArrays()
#     schema = test.schema()
#     ui = AutoIpywidget(schema)
#     display(ui)
# -

#
