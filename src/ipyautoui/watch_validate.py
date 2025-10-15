import traitlets as tr
import typing as ty
import ipywidgets as w
from IPython.display import clear_output
import contextlib
from pydantic import BaseModel, RootModel, ValidationError
from jsonref import replace_refs
import json
import logging

logger = logging.getLogger(__name__)


def pydantic_validate(model: BaseModel, value):
    return model.model_validate(value).model_dump(mode="json", by_alias=True)


class _WatchSilent(tr.HasTraits):  # TODO: contains context manager for silencing traits
    pass


def summarize_di_callers(obj):  # : AutoObject
    fn_ser = lambda k, v: str(v) if k == "autoui" else v
    fn_item = lambda v: {
        k_: fn_ser(k_, v_) for k_, v_ in v.model_dump().items() if k_ != "schema_"
    }
    if hasattr(obj, "di_callers"):  # AutoObject
        return {k: fn_item(v) for k, v in obj.di_callers.items()}
    else:  # root item
        return fn_item(obj.caller)


class WatchValidate(tr.HasTraits):  # TODO: _WatchValidate
    error = tr.Unicode(default_value=None, allow_none=True)
    schema = tr.Dict(default_value=None, allow_none=True)
    model = tr.Type(klass=BaseModel, default_value=None, allow_none=True)
    show_validation = tr.Bool(default_value=True)
    _value = tr.Any()  # TODO: update trait type on schema change
    _silent = tr.Bool(default_value=False)

    @contextlib.contextmanager
    def silence_autoui_traits(self):
        self._silent = True
        try:
            yield
        except Exception as e:
            self._silent = False
            raise e
        self._silent = False

    @tr.observe("error")
    def _error(self, on_change):
        if self.error is None:
            if self.show_validation:
                with self.out_error:
                    clear_output()
                self.out_error.layout = w.Layout(border=None, display="None")
            self.is_valid.value = True
        else:
            if self.show_validation:
                self.out_error.layout = w.Layout(border="2px solid red", display="")
                with self.out_error:
                    clear_output()
                    logging.error(self.error)
            self.is_valid.value = False

    @tr.observe("show_validation")
    def _show_validation(self, on_change):
        if hasattr(self, "out_error"):
            if self.show_validation:
                self.out_error.layout.display = ""
            else:
                self.out_error.layout.display = "none"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: ty.Any):
        if self.model is not None:
            try:
                value = pydantic_validate(self.model, value)
                self.error = None
            except ValidationError as e:
                self.error = str(e)
        if value != self._value:
            with self.hold_trait_notifications():
                # these means that change events will be squashed
                # and trigger after all widgets have changed
                if isinstance(value, dict):
                    self._value = self._value | value
                else:
                    self._value = value
                # NOTE: it is required to set the whole "_value" otherwise
                #       traitlets doesn't register the change.
                with self.silence_autoui_traits():
                    self._update_widgets_from_value()

    @property
    def json(self):
        if self.model is not None:
            return self.model(**self.value).model_dump_json(indent=4)
        else:
            return json.dumps(self.value, indent=4)

    def _set_validate_value(self, v):  # this is called on change of the UI
        if self.model is not None:
            try:
                v_ = pydantic_validate(self.model, v)
                self.error = None
            except ValidationError as e:
                self.error = str(e)
                v_ = v
            if v_ != v:
                try:
                    with self.silence_autoui_traits():
                        # silence trait notications to avoid infinite loop
                        # and push validated value back to widgets
                        self.value = v_
                    pass
                except Exception as e:
                    self.value = v_
            else:
                self._value = v_
        else:
            self._value = v

    def _watch_validate_update_value(self):
        # NOTE: this code only run when triggered by a change in a UI
        #       when value is forced in by the value setter it does not run
        v = self._get_value()
        if v != self._value:
            self._set_validate_value(v)
            if hasattr(self, "savebuttonbar"):
                self.savebuttonbar.unsaved_changes = True

    def _watch_validate_change(self, on_change):
        # NOTE: this method is intended for container widgets and is called
        #       when any child widget changes. that is why the _get_value()
        #       method required. it gets the value from all child widgets.

        # TODO: add log of on_change...
        message = f'change: {str(on_change["old"])} --> {str(on_change["new"])}'
        logger.info(message)
        if not self._silent:
            self._watch_validate_update_value()

    @classmethod
    def from_jsonschema(cls, schema: dict, value: ty.Any = None, **kwargs):
        if not isinstance(schema, dict):
            raise ValueError(
                f"schema must be a dict of type jsonschema, not {type(schema)}"
            )
        else:
            model = None
            if "$defs" in schema.keys():
                try:
                    schema = replace_refs(schema, merge_props=True)
                    schema = {k: v for k, v in schema.items() if k != "$defs"}
                except ValueError as e:
                    logger.warning(f"replace_refs error: \n{e}")
                    pass
        if value is not None:
            schema["value"] = value
        schema = {**schema, **kwargs}
        ui = cls(**schema)
        ui.schema = schema
        return ui

    @classmethod
    def from_pydantic_model(
        cls, model: ty.Type[BaseModel], value: ty.Any = None, by_alias=False, **kwargs
    ):
        if not (issubclass(model, BaseModel) or issubclass(model, RootModel)):
            raise ValueError(f"schema must be a pydantic model, not {type(model)}")
        else:
            schema = model.model_json_schema(by_alias=by_alias)
            if "by_alias" in kwargs.keys():
                by_alias = kwargs["by_alias"]
            schema = replace_refs(schema, merge_props=True)
            schema = {k: v for k, v in schema.items() if k != "$defs"}
        if value is not None:
            schema["value"] = value
        schema = {**schema, **kwargs}
        ui = cls(**schema)
        ui.model = model
        ui.schema = schema
        ui._init_validation_error()
        ui._set_validate_value(ui.value)
        return ui

    def _init_validation_error(self):
        if self.model is not None:
            self.out_error = w.Output()
            self.is_valid = w.Valid(value=True)
            self.vbx_error.children = [self.is_valid, self.out_error]

    @property
    def jsonschema_caller(self):
        #  NOTE: this is only used for demo
        #        it will only work from AutoObject
        #        a better implementation defo possible! ...
        return summarize_di_callers(self)

    # -----------------------------------------------------------
    # implement these methods in your class that uses validation:
    # i.e. AutoObject, AutoArray, EditGrid, etc.
    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

    def _update_widgets_from_value(self):
        # NOTE: fn name requried by WatchValidate base class
        #       `with self.silence_autoui_traits()` applied when
        #       calling this method
        pass

    def _get_value(self, **kwargs):
        # NOTE: fn name requried by WatchValidate base class
        pass  # NOTE: implement this method in your class

    def _init_watcher(self):
        # NOTE: implement a method in your class
        #       it must call `_watch_validate_change` on change
        #       of any child widget. `_init_watcher` name is not
        #       required by this base class but could be used...
        pass
