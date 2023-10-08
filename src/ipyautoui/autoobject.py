# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.15.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
"""AutoObject - create a 
"""
# %run _dev_sys_path_append.py
# %load_ext lab_black

import logging
import pathlib
import functools
import ipywidgets as w
from IPython.display import display
import traitlets as tr
import typing as ty
import json
import ipyautoui.automapschema as aumap
from ipyautoui._utils import obj_from_importstr
from ipyautoui.autowidgets import Nullable
from ipyautoui.autobox import AutoBox
from jsonref import replace_refs
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# -
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


class AutoObject(w.VBox):
    """creates an ipywidgets form from a json-schema or pydantic model.
    datatype must be "object"

    Attributes:

        # AutoObjectFormLayout
        # -------------------------
        title (str): form title
        description (str): form description
        show_description (bool, optional): show the description. Defaults to True.
        show_title (bool, optional): show the title. Defaults to True.
        show_savebuttonbar (bool, optional): show the savebuttonbar. Defaults to True.
        show_raw (bool, optional): show the raw json. Defaults to False.
        fn_onshowraw (callable): do not edit
        fn_onhideraw (callable): do not edit
        fns_onsave (callable): additional functions to be called on save
        fns_onrevert (callable): additional functions to be called on revert

        # AutoObject
        # -------------------------
        _value (dict): use `value` to set and get. the value of the form. this is a dict of the form {key: value}
        fdir (path, optional): fdir to work from. useful for widgets that link to files. Defaults to None.
        align_horizontal (bool, optional): aligns widgets horizontally. Defaults to True.
        nested_widgets (list, optional): allows user to indicate widgets that should be show / hide type. Defaults to [].
        order (list): allows user to re-specify the order for widget rows to appear by key name in self.di_widgets
        order_can_hide_rows (bool): allows user to hide rows by removing them from the order list.
        insert_rows (dict): e.g. {3:w.Button()}. allows user to insert a widget into the rows. its presence
            is ignored by the widget otherwise.
        disabled (bool, optional): disables all widgets. If widgets are disabled
            using schema kwargs this is remembered when re-enabled. Defaults to False.

    """

    update_map_widgets = tr.Dict()
    widgets_map = tr.Dict()
    type = tr.Unicode(default_value="object")
    allOf = tr.List(allow_none=True, default_value=None)
    properties = tr.Dict()
    _value = tr.Dict(allow_none=True)
    fdir = tr.Instance(klass=pathlib.PurePath, default_value=None, allow_none=True)
    align_horizontal = tr.Bool(default_value=True)
    nested_widgets = tr.List()
    order = tr.List(default_value=None, allow_none=True)
    order_can_hide_rows = tr.Bool(default_value=True)
    insert_rows = tr.Dict(default_value=None, allow_none=True)
    disabled = tr.Bool(default_value=False)
    open_nested = tr.Bool(default_value=None, allow_none=True)

    @tr.default("update_map_widgets")
    def _default_update_map_widgets(self):
        return {}

    @tr.observe("update_map_widgets")
    def _update_map_widgets(self, on_change):
        self.widgets_map = dict(aumap.get_widgets_map(self.update_map_widgets))

    @tr.default("widgets_map")
    def _widgets_map(self):
        return dict(aumap.get_widgets_map(self.update_map_widgets))

    @tr.validate("type")
    def _valid_type(self, proposal):
        if proposal["value"] != "object":
            raise ValueError("AutoObject for object only")
        return proposal["value"]

    @tr.observe("allOf")  # TODO: is this requried?
    def _allOf(self, on_change):
        if self.allOf is not None and len(self.allOf) == 1:
            self.properties = self.allOf[0]["properties"]
        else:
            raise ValueError("allOf not supported from objects")

    @tr.observe("properties")
    def _properties(self, on_change):
        self.di_callers = {
            property_key: aumap.map_widget(
                property_schema, widgets_map=self.widgets_map
            )
            for property_key, property_schema in self.properties.items()
        }
        for k, v in self.di_callers.items():
            if v.autoui in self.nested_widgets:
                v.kwargs_box = v.kwargs_box | {"nested": True}
        self._init_ui()

    @tr.observe("align_horizontal")
    def _align_horizontal(self, on_change):
        [
            setattr(b, "align_horizontal", on_change["new"])
            for b in self.di_boxes.values()
        ]

    @tr.observe("fdir")
    def _fdir(self, on_change):
        [
            setattr(b, "fdir", on_change["new"])
            for b in self.di_boxes.values()
            if "fdir" in b.traits()
        ]

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
            if self.default_order is None:
                return []
            for _ in v:
                if _ not in self.default_order:
                    raise ValueError(f"ERROR: {_} not in {str(self.default_order)}")
            if not self.order_can_hide_rows:
                if set(v) != set(self.default_order):
                    raise ValueError(
                        "set(v) != set(self.default_order)"
                        "if you want to use order to hide rows then set:"
                        "`order_can_hide_rows = True`"
                    )
        return v

    @tr.observe("order")
    def _obs_order(self, on_change):
        if len(on_change["new"]) < len(self.di_boxes) and not self.order_can_hide_rows:
            logger.warning(
                "order_can_hide_rows == False. set to True to use order to filter"
            )
            self.order = on_change["old"]
        else:
            self.vbx_main.children = [self.di_boxes[o] for o in self.order]

    @tr.validate("order_can_hide_rows")
    def _order_can_hide_rows(self, proposal):
        if self.order_can_hide_rows != proposal["value"]:
            if self.order is not None:
                if set(self.order) != set(self.default_order):
                    self.order = self.default_order
        return proposal["value"]

    @tr.default("nested_widgets")
    def _default_nested_widgets(self):
        from ipyautoui.custom.markdown_widget import MarkdownWidget  # , EditGrid
        from ipyautoui.custom.iterable import AutoArray
        from ipyautoui.custom.editgrid import EditGrid  # as EditGridCore
        from ipyautoui import AutoUi

        return [
            AutoArray,
            MarkdownWidget,
            EditGrid,
            AutoUi,
            AutoObject,
        ]

    @tr.validate("nested_widgets")
    def _valid_nested_widgets(self, proposal):
        fn = lambda s: obj_from_importstr(s) if isinstance(s, str) else s
        return [fn(p) for p in proposal["value"]]

    @tr.observe("open_nested")
    def observe_open_nested(self, on_change):
        if self.open_nested:
            self._open_nested()
        else:
            self._close_nested()

    @tr.validate("_value")
    def _valid_value(self, proposal):
        # TODO: add validation?
        return proposal["value"]

    @classmethod
    def trait_order(cls):
        return [k for k, v in cls.__dict__.items() if isinstance(v, tr.TraitType)]

    def get_ordered_kwargs(self, kwargs):
        in_order = list(kwargs.keys())
        tr_order = self.trait_order()
        out_order = tr_order + [i for i in in_order if i not in tr_order]
        return {o: kwargs[o] for o in out_order if o in in_order}

    def __init__(
        self,
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
        self.vbx_main = w.VBox()
        self.model = None
        # if "properties" not in kwargs.keys():
        #     raise ValueError("properties must be in kwargs")
        super().__init__()
        kwargs = self.get_ordered_kwargs(kwargs)
        {setattr(self, k, v) for k, v in kwargs.items()}

        self.children = [self.vbx_main]
        if "value" in kwargs.keys():
            self.value = kwargs["value"]
        else:
            self._value = self.di_widgets_value

    @classmethod
    def from_schema(
        cls, schema: ty.Union[ty.Type[BaseModel], dict], value: dict = None
    ):
        if isinstance(schema, type):
            if issubclass(schema, BaseModel):
                model = schema
                schema = replace_refs(schema.model_json_schema())
        elif isinstance(schema, dict):
            model = None
            if "$defs" in schema.keys():
                try:
                    schema = replace_refs(schema)
                except ValueError as e:
                    logger.warning(f"replace_refs error: \n{e}")
                    pass
        else:
            raise ValueError("schema must be a jsonschema or pydantic model")
        if value is not None:
            schema["value"] = value
        ui = cls(**schema)
        ui.model = model
        return ui

    def _open_nested(self):
        for r in self.di_boxes.values():
            if r.nested:
                r.tgl.value = True

    def _close_nested(self):
        for r in self.di_boxes.values():
            if r.nested:
                r.tgl.value = False

    @property
    def default_order(self):
        try:
            return list(self.di_widgets.keys())
        except:
            None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """this is for setting the value via the API"""
        if value is None:
            pass
        else:
            with self.hold_trait_notifications():
                self._value = value
                if hasattr(self, "di_widgets"):
                    self._update_widgets_from_value()

    @property
    def json(self):
        if self.model is not None:
            return self.model(**self.value).model_dump_json(indent=4)
        else:
            return json.dumps(self.value, indent=4)

    def _init_ui(self):
        self._init_widgets()
        self._init_controls()

    def _init_widgets(self):
        self.di_widgets = {k: aumap.widgetcaller(v) for k, v in self.di_callers.items()}
        self.di_boxes = {
            k: AutoBox(
                **(self.di_callers[k].kwargs_box | {"widget": self.di_widgets[k]})
            )
            for k in self.di_callers.keys()
        }
        self.vbx_main.children = list(self.di_boxes.values())
        self.indent_non_nullable()

    def indent_non_nullable(self):
        li = [v.allow_none for v in self.di_callers.values()]
        if True in li:
            for k, v in self.di_callers.items():
                if not v.allow_none:
                    self.di_boxes[k].indent = True

    def _insert_rows(self):
        if self.insert_rows is not None:
            for k, v in self.insert_rows.items():
                self.rows.insert(k, v)

    def _init_controls(self):
        self._init_watch_widgets()

    def _init_watch_widgets(self):
        for k, v in self.di_widgets.items():
            if v.has_trait("value"):
                logger.debug(f"value trait found for: {k}")
                v.observe(
                    functools.partial(self._watch_change, key=k, watch="value"), "value"
                )
            elif v.has_trait("_value"):
                logger.debug(f"_value trait found for: {k}")
                v.observe(
                    functools.partial(self._watch_change, key=k, watch="_value"),
                    "_value",
                )
            else:
                pass

    def _watch_change(self, change, key=None, watch="value"):
        # if self.validate_on_change:  # TODO
        #     if self.model is not None:
        #         new_value = json.loads(self.model(**self.di_widgets_value).json())
        #     else:
        #         raise ValueError(
        #             "currently a pydantic model is required to validate on change"
        #         )
        self._value = self.di_widgets_value
        if hasattr(self, "savebuttonbar"):
            self.savebuttonbar.unsaved_changes = True
        # NOTE: it is required to set the whole "_value" otherwise
        #       traitlets doesn't register the change.

    def _update_widgets_from_value(self):
        for k, v in self.value.items():
            if k in self.di_widgets.keys():
                if v is None and not isinstance(self.di_widgets[k], Nullable):
                    v = _get_value_trait(self.di_widgets[k]).default()
                try:
                    self.di_widgets[k].value = v
                except tr.TraitError as err:
                    logging.warning(err)
            else:
                logging.critical(
                    f"no widget created for {k}, with value {str(v)}. fix this in the schema!"
                )

    @property
    def di_widgets_value(self):  # used to set _value
        return {k: v.value for k, v in self.di_widgets.items()}


# +
from ipyautoui.autoform import AutoObjectFormLayout

class AutoObjectForm(AutoObject, AutoObjectFormLayout):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
        )
        # self._init_autoform(**kwargs)
        self.children = [
            self.savebuttonbar,
            self.hbx_title,
            self.html_description,
            self.vbx_main,
            self.vbx_showraw,
        ]

    def display_ui(self):  # NOTE: this overwritten this in AutoObjectForm
        self.vbx_main.layout.display = ""

    def display_showraw(self):  # NOTE: this overwritten this in AutoObjectForm
        self.vbx_main.layout.display = "None"
        return self.json

# -

if __name__ == "__main__":
    from ipyautoui.demo_schemas import CoreIpywidgets

    v = {
        "int_slider_req": 1,
        "int_slider_nullable": 2,
        "int_slider": 1,
        "int_text_req": 0,
        "int_text_nullable": None,
        "int_range_slider": [0, 1],
        "int_range_slider_disabled": [0, 1],
        "float_slider": 0,
        "float_text": 0,
        "float_text_locked": 0,
        "float_range_slider": [0.0, 1.1],
        "checkbox": False,
        "dropdown": None,
        "dropdown_int": 1,
        "combobox": "apple",
        "combobox1": "apple",
        "dropdown_edge_case": "apple",
        "dropdown_simple": "asd",
        "text": "adsf",
        "text_short": "short text",
        "textarea": "long text long text " * 20,
    }
    s = replace_refs(CoreIpywidgets.model_json_schema())
    # s["align_horizontal"] = False
    s["order_can_hide_rows"] = True
    s["order"] = ["int_slider_req", "dropdown_int", "int_range_slider_disabled"]
    ui = AutoObjectForm.from_schema(s, value=v)
    display(ui)

if __name__ == "__main__":
    ui.order_can_hide_rows = False

if __name__ == "__main__":
    ui.show_savebuttonbar = True

if __name__ == "__main__":
    from ipyautoui.demo_schemas import NestedEditableGrid, ComplexSerialisation

    s = replace_refs(NestedEditableGrid.model_json_schema())
    s["order_can_hide_rows"] = False
    s["open_nested"] = True
    ui = AutoObject.from_schema(s)
    display(ui)

# +
# ui.schema
# -

if __name__ == "__main__":
    from ipyautoui.demo_schemas import NestedEditableGrid, ComplexSerialisation

    s = replace_refs(ComplexSerialisation.model_json_schema())
    s["order_can_hide_rows"] = False
    ui = AutoObject.from_schema(s)
    display(ui)

if __name__ == "__main__":
    from ipyautoui.demo_schemas import CoreIpywidgets

    v = {
        "int_slider_req": 1,
        "int_slider_nullable": 2,
        "int_slider": 1,
        "int_text_req": 0,
        "int_text_nullable": None,
        "int_range_slider": [0, 1],
        "int_range_slider_disabled": [0, 1],
        "float_slider": 0,
        "float_text": 0,
        "float_text_locked": 0,
        "float_range_slider": [0.0, 1.1],
        "checkbox": False,
        "dropdown": None,
        "dropdown_int": 1,
        "combobox": "apple",
        "combobox1": "apple",
        "dropdown_edge_case": "apple",
        "dropdown_simple": "asd",
        "text": "adsf",
        "text_short": "short text",
        "textarea": "long text long text" * 20,
    }
    s = replace_refs(CoreIpywidgets.model_json_schema())
    # s["align_horizontal"] = False
    s["order_can_hide_rows"] = False
    ui = AutoObject.from_schema(s, value=v)
    display(ui)

if __name__ == "__main__":
    s["value"] = v
    ui = AutoObject(**s)
    display(ui)

if __name__ == "__main__":
    s["value"] = v
    ui = AutoObject(**s)
    display(ui)


