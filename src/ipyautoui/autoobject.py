# +
import logging
import pathlib
import ipywidgets as w
import traitlets as tr
from IPython.display import display
from jsonref import replace_refs
from pydantic import ValidationError

import ipyautoui.automapschema as aumap
from ipyautoui._utils import obj_from_importstr, is_null, trait_order
from ipyautoui.nullable import Nullable
from ipyautoui.autobox import AutoBox
from ipyautoui.autoform import AutoObjectFormLayout
from ipyautoui.watch_validate import WatchValidate, pydantic_validate
from ipyautoui.custom.title_description import TitleDescription

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


class AutoObject(w.VBox, WatchValidate):
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
    # model - pydantic model from WatchValidate
    # schema - json schema from WatchValidate
    nested_widgets = tr.List()
    update_map_widgets = tr.Dict()
    widgets_map = tr.Dict()
    type = tr.Unicode(default_value="object")
    allOf = tr.List(allow_none=True, default_value=None)
    properties = tr.Dict()
    _value = tr.Dict(
        allow_none=True
    )  # NOTE: value setter and getter in `WatchValidate`
    fdir = tr.Instance(klass=pathlib.PurePath, default_value=None, allow_none=True)
    align_horizontal = tr.Bool(default_value=True)
    order = tr.List(default_value=None, allow_none=True)
    order_can_hide_rows = tr.Bool(default_value=True)
    insert_rows = tr.Dict(default_value=None, allow_none=True)
    disabled = tr.Bool(default_value=False)
    open_nested = tr.Bool(default_value=None, allow_none=True)
    show_null = tr.Bool(default_value=False)
    # show_raw = tr.Bool(default_value=False)  # TODO: match logic for show_null

    def update_model(self, model):
        self.update_schema(model.model_json_schema())
        self.model = model
        try:
            self.value = pydantic_validate(self.model, self.value)
            self._update_widgets_from_value()  # NOTE: this should be called by the value setter...
            self.error = None
        except ValidationError as e:
            self.error = str(e)


    def update_schema(self, schema):
        schema = replace_refs(schema, merge_props=True)
        self.properties = schema["properties"]
        updates = {k: v for k, v in schema.items() if k in self.traits() and k != "properties" and k != "value"}
        {setattr(self, k, v) for k, v in updates.items()}
        self.schema = schema


    @tr.observe("show_null", "_value")
    def observe_show_null(self, on_change):
        self._show_null(self.show_null)

    def _show_null(self, yesno: bool):
        for k, v in self.di_boxes.items():
            if k in self.value.keys():
                if is_null(self.value[k]):
                    v.layout.display = (lambda yesno: "" if yesno else "None")(yesno)
                else:
                    v.layout.display = ""
            else:
                # If no value passed assume value is None
                v.layout.display = (lambda yesno: "" if yesno else "None")(yesno)

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

    @tr.observe("allOf")
    def _allOf(self, on_change):
        if self.allOf is not None and len(self.allOf) == 1:
            self.properties = self.allOf[0]["properties"]
        else:
            raise ValueError("allOf not supported from objects")

    @tr.observe("properties")
    def _properties(self, on_change):
        if hasattr(self, "di_callers"): # updating schema...
            di_callers = self._get_di_callers(self.properties)
            if {k: v.autoui for k,v in di_callers.items()} != {k: v.autoui for k,v in self.di_callers.items()}:
                self.properties = on_change["old"]
                raise ValueError("widgets must match on schema change. changes intended for modifications of existing widgets only.")
            for k, v in di_callers.items():
                {setattr(self.di_widgets[k], _k, _v) for _k, _v in v.kwargs.items() if _k != "value"}
                {setattr(self.di_boxes[k], _k, _v) for _k, _v in v.kwargs_box.items() if _k != "value"}
            self.di_callers = di_callers
        else: # instantiating...
            self.di_callers = self._get_di_callers(self.properties)
            self._init_ui()

    def _get_di_callers(self, properties):
        di_callers = {
            pkey: aumap.map_widget(
                pschema, widgets_map=self.widgets_map
            )
            for pkey, pschema in properties.items()
        }
        for v in di_callers.values():
            if v.autoui in self.nested_widgets:
                v.kwargs = v.kwargs | {"show_title": False, "show_description": False}
                # NOTE: ^ this avoids nested widgets having title and description both in AutoBox and in themselves
                v.kwargs_box = v.kwargs_box | {"nested": True}
        return di_callers

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
        fn_checkisintkeys = lambda di: (
            True if [isinstance(l, int) == True for l in di.keys()] else False
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
                if (
                    "disabled" in self.properties[k].keys()
                    and self.properties[k]["disabled"]
                ):
                    logger.info(
                        f"{k}: widget is disabled in base schema. Enabling not allowed."
                    )
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
            self.vbx_widget.children = [self.di_boxes[o] for o in self.order]

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

    def get_ordered_kwargs(self, kwargs):
        in_order = list(kwargs.keys())
        tr_order = trait_order(type(self))
        if isinstance(self, AutoObjectForm): # HACK: traits not found in inherited class...
            tr_order = trait_order(AutoObject)

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
        self.vbx_error = w.VBox()
        self.vbx_widget = w.VBox()
        # TODO: ^ move common container attributes to WatchValidate

        self.model = None
        super().__init__()
        kwargs = self.get_ordered_kwargs(kwargs)
        {setattr(self, k, v) for k, v in kwargs.items()}

        if "value" in kwargs.keys():
            self.value = self.di_widgets_value | kwargs["value"]
        else:
            self._value = self.di_widgets_value
        self._show_null(self.show_null)
        self._set_children()
        self._post_init(**kwargs)

    def _set_children(self):
        self.children = [self.vbx_widget]

    def _post_init(self, **kwargs):
        pass

    def _open_nested(self):
        if getattr(self, "di_boxes", None) is not None: # HACK: as AutoArray doesn't have di_boxes
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
            return None

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
        self.vbx_widget.children = list(self.di_boxes.values())
        self.indent_widgets()

    def indent_widgets(self):
        """Indent the widgets appropriately based on the schema.
        Any widget that is not nullable and has a type of "array" will be indented."""
        li = [v.allow_none for v in self.di_callers.values()]
        if True in li:
            for k, v in self.di_callers.items():
                if not v.allow_none:
                    self.di_boxes[k].indent = True
                if "type" in v.kwargs and v.kwargs["type"] == "array":
                    self.di_boxes[k].indent = True

    def _insert_rows(self):
        if self.insert_rows is not None:
            for k, v in self.insert_rows.items():
                self.rows.insert(k, v)

    def _init_controls(self):
        self._init_watch_widgets()

    def set_watcher(self, key, widget, watch):
        logger.debug(f"{watch} trait found for: {key}")
        widget.observe(
            self._watch_validate_change,
            watch,  # NOTE: `_watch_validate_change` in WatchValidate
        )

    def _init_watch_widgets(self):
        for k, v in self.di_widgets.items():
            for watch in ["_value", "value"]:
                if v.has_trait(watch):
                    self.set_watcher(k, v, watch)
                    break  # if `_value` is found don't look for `value`

    def _update_widgets_from_value(self):
        with self.silence_autoui_traits():
            for k, v in self.value.items():
                if k in self.di_widgets.keys():
                    if is_null(v) and not isinstance(self.di_widgets[k], Nullable):
                        v = _get_value_trait(self.di_widgets[k]).default()
                    try:
                        self.di_widgets[k].value = v
                    except tr.TraitError as err:
                        logging.warning(err)
                else:
                    logging.critical(
                        f"no widget created for {k}, with value {str(v)}. fix this in the schema!"
                    )

    def _get_value(self):
        return self.di_widgets_value

    @property
    def di_widgets_value(self):  # used to set _value
        return {k: v._value if "_value" in v.traits() else v.value for k, v in self.di_widgets.items()}

    def check_for_nullables(self) -> bool:
        """Search through widgets and as soon as a Nullable widget is found, return True.
        Else, return False."""
        for v in self.di_widgets.values():
            if isinstance(v, Nullable):
                return True
        return False


class AutoObjectForm(AutoObject, AutoObjectFormLayout, TitleDescription):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
        )

        self.children = [
            w.HBox([self.bn_shownull, self.savebuttonbar]),
            self.html_title,
            self.html_description,
            self.vbx_widget,
            self.vbx_showraw,
        ]
        self.show_hide_bn_nullable()

    def display_ui(self):
        self.vbx_widget.layout.display = ""

    def display_showraw(self):
        self.vbx_widget.layout.display = "None"
        return self.json

    def _set_children(self):
        self.children = [self.hbx_title_description, self.vbx_widget]


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
    s = replace_refs(CoreIpywidgets.model_json_schema(), merge_props=True)
    # s["align_horizontal"] = False
    s["order_can_hide_rows"] = True
    s["order"] = ["int_slider_req", "dropdown_int", "int_range_slider_disabled"]
    ui = AutoObjectForm.from_jsonschema(s, value=v)
    display(ui)

if __name__ == "__main__":
    ui.order_can_hide_rows = False

if __name__ == "__main__":
    ui.show_savebuttonbar = True

if __name__ == "__main__":
    from ipyautoui.demo_schemas import NestedEditableGrid, ComplexSerialisation

    s = replace_refs(NestedEditableGrid.model_json_schema(), merge_props=True)
    s["order_can_hide_rows"] = False
    s["open_nested"] = True
    ui = AutoObject.from_jsonschema(s)
    display(ui)

if __name__ == "__main__":
    from ipyautoui.demo_schemas import NestedEditableGrid, ComplexSerialisation

    s = replace_refs(ComplexSerialisation.model_json_schema(), merge_props=True)
    s["order_can_hide_rows"] = False
    ui = AutoObject.from_jsonschema(s)
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
    s = replace_refs(CoreIpywidgets.model_json_schema(), merge_props=True)
    # s["align_horizontal"] = False
    s["order_can_hide_rows"] = False
    ui = AutoObject.from_jsonschema(s, value=v)
    display(ui)

if __name__ == "__main__":
    s["value"] = v
    ui = AutoObject(**s)
    display(ui)

if __name__ == "__main__":
    s["value"] = v
    ui = AutoObject(**s)
    display(ui)
