
import traitlets as tr
import typing as ty
import ipywidgets as w
from IPython.display import clear_output
import contextlib
from pydantic import BaseModel, RootModel, ValidationError
from jsonref import replace_refs
import logging

logger = logging.getLogger(__name__)

def pydantic_validate(model, value):
    return model.model_validate(value).model_dump(mode="json")

class _WatchSilent(tr.HasTraits):  # TODO: contains context manager for silencing traits
    pass

# class _ErrorUi(tr.HasTraits): 
    

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
        yield
        self._silent = False
    
    @tr.observe("error")
    def _error(self, on_change):
        if self.error is None:
            with self.out_error:
                clear_output()
            self.out_error.layout=w.Layout(border=None, display="None")  
            self.is_valid.value = True
        else:
            self.out_error.layout=w.Layout(border='2px solid red', display="")  
            with self.out_error:
                clear_output()
                print(self.error)
            self.is_valid.value = False
                
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value: ty.Any):
        if value != self._value:
            with self.hold_trait_notifications():
                # these means that change events will be squashed
                # and trigger after all widgets have changed
                self._value = value
                # NOTE: it is required to set the whole "_value" otherwise
                #       traitlets doesn't register the change.
                with self.silence_autoui_traits():
                    self._update_widgets_from_value()
        
    def _validate_value(self, v):
        if self.model is not None:
            try:
                v_ = pydantic_validate(self.model, v)
                self.error = None
            except ValidationError as e:
                self.error = str(e)
                v_ = v
            if v_ != v:
                with self.silence_autoui_traits():
                    # silence trait notications to avoid infinite loop
                    # and push validated value back to widgets
                    self.value = v_
            else:
                self._value = v_
        else:
            self._value = v
        
    def _watch_validate_change(self, on_change):
        # NOTE: this method is intended for container widgets and is called
        #       when any child widget changes. that is why the _get_value()
        #       method required. it gets the value from all child widgets.
        
        # TODO: add log of on_change...
        if not self._silent:  
            # NOTE: this code only run when triggered by a change in a UI
            #       when value is forced in by the value setter it does not run
            v = self._get_value(on_change=on_change)
            if v != self._value:
                self._validate_value(v)
                if hasattr(self, "savebuttonbar"):
                    self.savebuttonbar.unsaved_changes = True

            

    @classmethod
    def from_jsonschema(
        cls, schema: dict, value: ty.Any = None
    ):
        if not isinstance(schema, dict):
            raise ValueError(f"schema must be a dict of type jsonschema, not {type(schema)}")
        else:
            model = None
            if "$defs" in schema.keys():
                try:
                    schema = replace_refs(schema)
                except ValueError as e:
                    logger.warning(f"replace_refs error: \n{e}")
                    pass
        if value is not None:
            schema["value"] = value
        ui = cls(**schema)
        return ui
    
    @classmethod
    def from_pydantic_model(
        cls, model: ty.Type[BaseModel], value: ty.Any = None
    ):
        if not issubclass(model, BaseModel) or issubclass(model, RootModel):
            raise ValueError(f"schema must be a pydantic model, not {type(model)}")
        else:       
            schema = replace_refs(model.model_json_schema())
        if value is not None:
            schema["value"] = value
        ui = cls(**schema)
        ui.model = model
        ui._init_validation_error()
        ui._validate_value(ui.value)
        return ui
        
    def _init_validation_error(self):
        if self.model is not None:
            self.out_error = w.Output()
            self.is_valid = w.Valid(value=True)
            self.vbx_error = w.VBox([self.is_valid, self.out_error])
            self.children = [self.vbx_error] + list(self.children)
        
    # -----------------------------------------------------------  
    # implement these methods in your class that uses validation: 
    # i.e. AutoObject, AutoArray, EditGrid, etc.
    # ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓

    def _update_widgets_from_value(self):
        # NOTE: fn name requried by WatchValidate base class
        with self.silence_autoui_traits():
            pass # NOTE: implement this method in your class
        
    def _get_value(self, **kwargs):
        # NOTE: fn name requried by WatchValidate base class
        pass # NOTE: implement this method in your class

    def _init_watcher(self):
        # NOTE: implement a method in your class
        #       it must call `_watch_validate_change` on change
        #       of any child widget. `_init_watcher` name is not
        #       required by this base class.
        pass 