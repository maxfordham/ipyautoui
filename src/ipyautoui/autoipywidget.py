# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
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
# %run _dev_sys_path_append.py
# %run __init__.py
#
# %load_ext lab_black
import logging
import pathlib
import functools
import ipywidgets as w
from IPython.display import display
import traitlets as tr
import typing as ty
import inspect
import json
from IPython.display import display, clear_output
import ipyautoui.automapschema as aumap
from ipyautoui.constants import BUTTON_WIDTH_MIN
from ipyautoui._utils import display_python_string, obj_from_importstr
from ipyautoui.custom.buttonbars import SaveButtonBar
from ipyautoui.custom.showhide import ShowHide
from ipyautoui.autowidgets import Nullable

logger = logging.getLogger(__name__)


# -


def _init_widgets_and_labels(
    pr: ty.Dict,
) -> tuple[ty.Dict[str, w.HBox], ty.Dict]:
    """initiates widget for from dict built from schema

    Args:
        pr (ty.Dict): schema properties - sanitised for ipywidgets

    Returns:
        (w.VBox, ty.Dict): box with widgets, di of widgets
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


# + tags=[]
def _get_value_trait(obj_with_traits):
    """gets the trait type for a given object (looks for "_value" and
    "value" allowing use of setters and getters)

    Args:
        obj_with_traits (tr.Type): obj with traits

    Raises:
        ValueError: if "_value" or "value" traits don't exist

    Returns:
        ty.Type: trait type of traitlet
    """
    if "_value" in obj_with_traits.traits().keys():
        return obj_with_traits.traits()["_value"]
    elif "value" in obj_with_traits.traits().keys():
        return obj_with_traits.traits()["value"]
    else:
        raise ValueError(
            f"{str(type(obj_with_traits))}: has no '_value' or 'value' trait"
        )


def get_from_schema_root(schema: ty.Dict, key: ty.AnyStr) -> ty.AnyStr:
    return schema[key] if key in schema.keys() else ""


def add_fdir_to_widgetcaller(
    caller, fdir: str
): # TODO: deprecate this by making fdir a trait and passing as **kwargs
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


def add_spacer_to_form_with_nullables(children, widget, contains_nullable):
    if contains_nullable and not isinstance(widget, Nullable):
        children = [w.HBox(layout={"width": "45px"})] + children
    return children


def horizontal_row_simple(widget, label, contains_nullable=False):
    children = [widget, w.HTML(label)]
    children = add_spacer_to_form_with_nullables(children, widget, contains_nullable)
    return w.HBox(children)


def vertical_row(widget, label, auto_open=None, contains_nullable=False):
    children = [w.HBox(layout={"width": "40px"}), widget]
    children = add_spacer_to_form_with_nullables(children, widget, contains_nullable)
    return w.VBox(
        [
            w.HTML(label),
            w.HBox(children),
        ]
    )


def create_row(
    widget,
    label,
    align_horizontal=True,
    auto_open=False,
    nested_widgets=None,
    contains_nullable=False,
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
            return horizontal_row_simple(
                widget, label, contains_nullable=contains_nullable
            )
    else:
        return vertical_row(widget, label, contains_nullable=contains_nullable)


def show_hide_widget(widget, show: bool):
    try:
        if show:
            widget.layout.display = ""
        else:
            widget.layout.display = "None"
    except:
        ValueError(str(widget) + "failed to change layout.display")


# +
def make_bold(s: str) -> str:
    return f"<big><b>{s}</b></big>"


class AutoObjectFormLayout(w.VBox):

    show_description = tr.Bool(default_value=True)
    show_title = tr.Bool(default_value=True)
    show_savebuttonbar = tr.Bool(default_value=False)
    fn_onshowraw = tr.Callable(default_value=lambda: "{'test':'json'}")
    fn_onhideraw = tr.Callable(default_value=lambda: None)
    show_raw = tr.Bool(default_value=False)

    @tr.observe("show_raw")
    def _observe_show_raw(self, change):
        show_hide_widget(self.bn_showraw, self.show_raw)

    @tr.observe("show_description")
    def _observe_show_description(self, change):
        show_hide_widget(self.description, self.show_description)

    @tr.observe("show_title")
    def _observe_show_title(self, change):
        show_hide_widget(self.title, self.show_title)

    @tr.observe("show_savebuttonbar")
    def _observe_show_savebuttonbar(self, change):
        show_hide_widget(self.savebuttonbar, self.show_savebuttonbar)

    def __init__(self, fns_onsave=None, fns_onrevert=None, **kwargs):

        self._init_form()
        self._init_bn_showraw_controls()
        self.fn_onshowraw = self.display_showraw
        self.fn_onhideraw = self.display_ui
        if fns_onsave is not None:
            self.fns_onsave = fns_onsave
        if fns_onrevert is not None:
            self.fns_onrevert = fns_onrevert
        super().__init__(
            layout=w.Layout(
                width="100%",
                display="flex",
                flex="flex-grow",
            ),
            **kwargs,
        )
        self.children = [
            self.savebuttonbar,
            self.hbx_title,
            self.description,
            self.autowidget,
            self.vbx_showraw,
        ]

    def _init_form(self):
        self.autowidget = w.VBox()
        self.hbx_title = w.HBox()
        self.savebuttonbar = SaveButtonBar(layout={"display": "None"})  #
        self.title = w.HTML()
        self._init_bn_showraw()
        self.hbx_title.children = [self.bn_showraw, self.title]
        self.description = w.HTML()  #

    def _init_bn_showraw(self):
        self.bn_showraw = w.ToggleButton(
            icon="code",
            layout=w.Layout(width=BUTTON_WIDTH_MIN, display="None"),
            tooltip="show raw data",
            style={"font_weight": "bold", "button_color": None},
        )
        self.vbx_showraw = w.VBox()
        self.out_raw = w.Output()
        self.vbx_showraw.children = [self.out_raw]

    def _init_bn_showraw_controls(self):
        self.bn_showraw.observe(self._bn_showraw, "value")

    def _bn_showraw(self, onchange):
        if self.bn_showraw.value:
            self.bn_showraw.tooltip = "show user interface"
            self.bn_showraw.icon = "user-edit"
            di = self.fn_onshowraw()
            self.vbx_showraw.layout.display = ""

            with self.out_raw:
                clear_output()
                display_python_string(di)

        else:
            self.bn_showraw.tooltip = "show raw data"
            self.bn_showraw.icon = "code"
            self.fn_onhideraw()
            self.vbx_showraw.layout.display = "None"

    def display_ui(self):
        self.autowidget.layout.display = ""

    def display_showraw(self):  # NOTE: this overwritten this in AutoObject
        self.autowidget.layout.display = "None"
        return '{"test": "json"}'

    @property
    def fns_onsave(self):
        return self.savebuttonbar.fns_onsave

    @fns_onsave.setter
    def fns_onsave(self, value):
        if isinstance(value, list):
            [self.savebuttonbar.fns_onsave_add_action(v) for v in value]
        elif isinstance(value, ty.Callable):
            self.savebuttonbar.fns_onrevert_add_action(value)
        else:
            raise ValueError("fns_onsave must be a callable or list of callables")

    @property
    def fns_onrevert(self):
        return self.savebuttonbar.fns_onrevert

    @fns_onrevert.setter
    def fns_onrevert(self, value):
        if isinstance(value, list):
            [self.savebuttonbar.fns_onrevert_add_action(v) for v in value]
        elif isinstance(value, ty.Callable):
            self.savebuttonbar.fns_onrevert_add_action(value)
        else:
            raise ValueError("fns_onrevert must be a callable or list of callables")


if __name__ == "__main__":
    ui = AutoObjectFormLayout(description="description", show_savebuttonbar=True)
    display(ui)

# +
def demo_autoobject_form(title="test", description="a description of the title"):
    """for docs and testing only..."""
    from ipyautoui.custom.buttonbars import SaveButtonBar

    form = AutoObjectFormLayout()
    form.title.value = make_bold(title)
    form.description.value = description
    form.show_raw = True
    form.show_description = True
    form.show_title = True
    form.show_savebuttonbar = True
    form.savebuttonbar.layout = {"border": "solid red 2px"}
    form.savebuttonbar.children = [SaveButtonBar()]
    form.hbx_title.layout = {"border": "solid blue 2px"}
    form.autowidget.layout = {"border": "solid green 2px", "height": "200px"}
    form.autowidget.children = [w.Button(description="PlaceHolder Widget")]
    form.vbx_showraw.layout = {
        "border": "solid orange 2px",
        "height": "200px",
    }
    form.layout = {"border": "solid yellow 2px"}
    form._bn_showraw("d")
    return form


if __name__ == "__main__":
    form = demo_autoobject_form()
    display(form)

# +
# form.show_raw = True
# -

if __name__ == "__main__":
    form.show_savebuttonbar = False
    form.show_description = False
    form.show_title = False
    form.show_raw = False

if __name__ == "__main__":
    form.show_savebuttonbar = True
    form.show_description = True
    form.show_title = True
    form.show_raw = True


def autogen(schema) -> object:
    pass  #


# +
class AutoObject(AutoObjectFormLayout):  # w.VBox
    """creates an ipywidgets form from a json-schema or pydantic model.
    datatype must be "object"

    Attributes:
        _value (dict): use `value` to set and get. the value of the form. this is a dict of the form {key: value}
        fdir (path, optional): fdir to work from. useful for widgets that link to files. Defaults to None.
        align_horizontal (bool, optional): aligns widgets horizontally. Defaults to True.
        nested_widgets (list, optional): allows user to indicate widgets that should be show / hide type. Defaults to [].
        auto_open (bool, optional): automatically opens the nested_widget. Defaults to True.
        order (list): allows user to re-specify the order for widget rows to appear by key name in self.di_widgets
        order_can_hide_rows (bool): allows user to hide rows by removing them from the order list.
        insert_rows (dict): e.g. {3:w.Button()}. allows user to insert a widget into the rows. its presence
            is ignored by the widget otherwise.
        disabled (bool, optional): disables all widgets. If widgets are disabled
            using schema kwargs this is remembered when re-enabled. Defaults to False.

        # inherited from AutoObjectFormLayout

        show_raw (bool, optional): show the raw json. Defaults to False.
        show_description (bool, optional): show the description. Defaults to True.
        show_title (bool, optional): show the title. Defaults to True.
        show_savebuttonbar (bool, optional): show the savebuttonbar. Defaults to True.

    """

    _value = tr.Dict(allow_none=True)
    fdir = tr.Instance(klass=pathlib.PurePath, default_value=None, allow_none=True)
    align_horizontal = tr.Bool(default_value=True)
    auto_open = tr.Bool(default_value=True)
    nested_widgets = tr.List()
    order = tr.List(default_value=None, allow_none=True)
    order_can_hide_rows = tr.Bool(default_value=True)
    insert_rows = tr.Dict(default_value=None, allow_none=True)
    disabled = tr.Bool(default_value=False)

    def __init__(
        self,
        schema,
        by_alias=False,
        value=None,
        update_map_widgets=None,
        fns_onsave=None,
        fns_onrevert=None,
        **kwargs,
    ):
        """creates a widget input form from schema. datatype must be "object"

        Args:
            schema (dict): json schema defining widget to generate
            by_alias (bool, optional): use alias in schema. Defaults to False.
            value (dict, optional): value of json. Defaults to None.
            update_map_widgets (frozenmap, optional): frozen dict of widgets to map to schema items. Defaults to None.
            fn_onsave (callable, optional): function to run on save. Defaults to None.
            fn_onrevert (callable, optional): function to run on revert. Defaults to None.

        Returns:
            AutoObject(w.VBox)
        """

        self.update_map_widgets = update_map_widgets
        self._init_schema(schema, by_alias=by_alias)  # TODO: make schema a trait
        self._init_ui()
        super().__init__(fns_onsave=fns_onsave, fns_onrevert=fns_onrevert, **kwargs)
        self.title.value = make_bold(self.get_title())
        self.description.value = self.get_description()
        self._format_rows()
        if value is not None:
            self.value = value
        else:
            self._value = self.di_widgets_value

    @tr.validate("insert_rows")
    def validate_insert_rows(self, proposal):
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

    @tr.observe("disabled")
    def observe_disabled(self, on_change):
        if self.disabled:
            for k, v in self.di_widgets.items():
                try:
                    v.disabled = True
                except:
                    logger.warning(f"{k}: widget does not have a `disabled` traitlet")
        else:
            for k, v in self.di_widgets.items():
                if "disabled" in self.pr[k].schema_ and self.pr[k].schema_["disabled"]:
                    logger.info(f"{k}: widget disabled in base schema")
                else:
                    try:
                        v.disabled = False
                    except:
                        logger.warning(
                            f"{k}: widget does not have a `disabled` traitlet"
                        )

    @tr.validate("order")
    def _order(self, proposal):
        v = proposal["value"]
        if v is not None:
            for _ in v:
                if _ not in self.default_order:
                    raise ValueError(f"ERROR: {_} not in {str(self.default_order)}")
            if not self.order_can_hide_rows:
                if set(v) != set(self.default_order):
                    raise ValueError(
                        "set(v) != set(self.default_order)"
                        "if you want to use order to hide rows then set:"
                        "`order_hides_rows = True`"
                    )
        return v

    @tr.validate("order_can_hide_rows")
    def _order_can_hide_rows(self, proposal):
        if self.order_can_hide_rows != proposal["value"]:
            if self.order is not None:
                if set(self.order) != set(self.default_order):
                    self.order = self.default_order
        return proposal["value"]

    @tr.default("nested_widgets")
    def _default_nested_widgets(self):
        from ipyautoui.autowidgets import AutoMarkdown  # , EditGrid
        from ipyautoui.custom.iterable import AutoArray
        from ipyautoui.custom.editgrid import EditGrid  # as EditGridCore
        from ipyautoui import AutoUi

        default_nested = [
            AutoArray,
            AutoMarkdown,
            EditGrid,
            AutoUi,
            AutoObject,
        ]
        return default_nested

    @tr.validate("nested_widgets")
    def _valid_nested_widgets(self, proposal):
        fn = lambda s: obj_from_importstr(s) if isinstance(s, str) else s
        return [fn(p) for p in proposal["value"]]

    @tr.validate("_value")
    def _valid_value(self, proposal):
        # TODO: add validation?
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
        if value is None:
            pass
        else:
            self._value = value
            if hasattr(self, "di_widgets"):
                self._update_widgets_from_value()

    def display_showraw(self):
        self.autowidget.layout.display = "None"
        return self.json

    @property
    def json(self):
        if self.model is not None:
            return self.model(**self.value).json(indent=4)
        else:
            return json.dumps(self.value, indent=4)

    def get_description(self):
        return get_from_schema_root(self.schema, "description")

    def get_title(self):
        return get_from_schema_root(self.schema, "title")

    def _init_ui(self):
        self._init_widgets()
        self._init_controls()

    def _init_schema(self, schema, by_alias=False):
        self.model, self.schema = aumap._init_model_schema(schema, by_alias=by_alias)
        if "properties" in self.schema.keys():
            pr = self.schema["properties"]
        else:
            pr = {"__root__": self.schema}
        self.pr = {
            property_key: aumap.map_widget(
                property_schema, widgets_map=self.widgets_map
            )
            for property_key, property_schema in pr.items()
        }
        self.contains_nullable = False
        for v in self.pr.values():
            if "nullable" in v.schema_:
                self.contains_nullable = True
                break

        if self.fdir is not None:
            for v in self.pr.values():
                v = add_fdir_to_widgetcaller(v, self.fdir)

    def _init_widgets(self):
        self.di_labels, self.di_widgets = _init_widgets_and_labels(self.pr)

    def _insert_rows(self):
        if self.insert_rows is not None:
            for k, v in self.insert_rows.items():
                self.rows.insert(k, v)

    def _format_rows(self):
        set_order = lambda _: self.default_order if _ is None else _
        order = set_order(self.order)
        self.rows = [
            create_row(
                self.di_widgets[row],
                self.di_labels[row],
                align_horizontal=self.align_horizontal,
                auto_open=self.auto_open,
                nested_widgets=self.nested_widgets,
                contains_nullable=self.contains_nullable,
            )
            for row in order
        ]
        self._insert_rows()
        self.autowidget.children = self.rows

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
            ],  # type: ignore
        )

    def _watch_change(self, change, key=None, watch="value"):
        # if self.validate_on_change:
        #     if self.model is not None:
        #         new_value = json.loads(self.model(**self.di_widgets_value).json())
        #     else:
        #         raise ValueError(
        #             "currently a pydantic model is required to validate on change"
        #         )

        self._value = self.di_widgets_value
        self.savebuttonbar.unsaved_changes = True
        # NOTE: it is required to set the whole "_value" otherwise
        #       traitlets doesn't register the change.
        #       -@jovyan at 7/18/2022, 12:45:48 PMsavebuttonbar

    def _update_widgets_from_value(self):
        for k, v in self.value.items():
            if k in self.di_widgets.keys():
                if v is None and not isinstance(self.di_widgets[k], Nullable):
                    v = _get_value_trait(self.di_widgets[k]).default()
                self.di_widgets[k].value = v
            else:
                logging.critical(
                    f"no widget created for {k}, with value {str(v)}. fix this in the schema!"
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
        self.widgets_map = aumap.get_widgets_map(value)


if __name__ == "__main__":
    from ipyautoui.demo_schemas import CoreIpywidgets

    ui = AutoObject(
        CoreIpywidgets,
        order=["text", "int_text", "int_slider", "int_slider_nullable"],
        show_description=False,
        show_title=False,
        show_savebuttonbar=False,
        show_raw=False,
    )
    display(ui)

# +
# ui.show_savebuttonbar = True

# +
if __name__ == "__main__":
    order = [
        "text",
        "int_text",
        "int_slider",
        "int_slider_nullable",
        "int_range_slider",
        "int_range_slider_disabled",
        # "float_slider",
        # "float_text",
        # "float_text_locked",
        # "float_range_slider",
        # "checkbox",
        # "dropdown",
        # "dropdown_edge_case",
        # "dropdown_simple",
        "text_short",
        "text_area",
    ]
    ui.order = order

# "combobox", "auto_markdown"
# -

if __name__ == "__main__":
    ui.disabled = True

if __name__ == "__main__":
    ui.disabled = False

if __name__ == "__main__":
    ui.align_horizontal = False

if __name__ == "__main__":
    ui.align_horizontal = True

# +
if __name__ == "__main__":
    ui.nested_widgets = []

if __name__ == "__main__":
    ui.auto_open = True

if __name__ == "__main__":
    ui.show_savebuttonbar = False
    ui.show_description = False
    ui.show_title = False
    ui.show_raw = False

if __name__ == "__main__":
    ui.show_savebuttonbar = True
    ui.show_description = True
    ui.show_title = True
    ui.show_raw = True
