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
# %load_ext lab_black

import pathlib
from IPython.display import display
from pydantic import BaseModel
import json
import traitlets as tr
import typing as ty
from ipyautoui.autoform import AutoObjectFormLayout
from ipyautoui.custom import SaveButtonBar  # removing makes circular import error
import json
import logging
from ipyautoui.automapschema import map_widget, widgetcaller, _init_model_schema
import ipywidgets as w
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# +
def parse_json_file(path: pathlib.Path, model=None):
    """read json from file"""
    p = pathlib.Path(path)
    if model is not None:
        return json.loads(model.parse_file(p).json())
    else:
        return json.loads(p.read_text())


def displayfile_renderer(path, renderer=None):
    if renderer is None:
        raise ValueError("renderer must not be None")
    display(renderer(path))


def jsonschema_to_pydantic(
    schema: ty.Type,  #: JsonSchemaObject
    *,
    config: ty.Type = None,  # = JsonSchemaConfig
) -> ty.Optional[ty.Type[BaseModel]]:
    pass  # TODO: https://github.com/samuelcolvin/pydantic/issues/1638


# -


class AutoUiFileMethods(tr.HasTraits):
    """AutoUiFileMethods is a mixin class that adds file methods to a AutoUi class

    Attributes:
        path (tr.Instance(klass=pathlib.PurePath)...): path to file
    """

    path = tr.Instance(klass=pathlib.PurePath, default_value=None, allow_none=True)
    fdir = tr.Instance(klass=pathlib.PurePath, default_value=None, allow_none=True)

    @tr.observe("path")
    def _observe_path(self, proposal):
        self.savebuttonbar.fns_onsave_add_action(self.file, to_beginning=True)
        self.savebuttonbar.fns_onrevert_add_action(self.load_file, to_beginning=True)

    def _get_path(self, path=None) -> pathlib.Path:
        if path is None:
            if self.path is not None:
                return self.path
            else:
                self.savebuttonbar.message.value = "no filepath give"
                raise ValueError("NO PATH GIVEN: path is None and self.path is None")
        else:
            return path

    def _get_value(self, v, p):  # TODO: check this... wasn't working...
        """
        Args:
            v: value
            p: path
        Returns:
            value: dict
        """
        # handle inputs
        if v is None and p is None:
            # v reverts to schema defaults
            return None
        elif v is None and p is not None and p.is_file() == True:
            # load v from p
            return self.parse_file(path=p)
        elif v is None and p is not None and p.is_file() == False:
            # v reverts to schema defaults
            return None
        elif v is not None:
            # v reverts to given v
            return v
        else:
            raise ValueError("_get_value error...?")

    def file(self, path=None):
        p = self._get_path(path=path)
        p.write_text(self.json, encoding="utf-8")
        self.savebuttonbar.unsaved_changes = False

    def parse_file(self, path=None) -> dict:
        p = self._get_path(path=path)
        if p.is_file():
            return parse_json_file(p, model=self.model)
        else:
            raise ValueError("p.is_file() == False")

    def load_value(self, value, unsaved_changes=False):
        self.value = value
        if unsaved_changes:
            self.savebuttonbar.unsaved_changes = False
        else:
            self.savebuttonbar.unsaved_changes = True

    def load_file(self, path=None):
        p = self._get_path(path=path)
        if path is None:
            unsaved_changes = False
        else:
            unsaved_changes = True
        self.load_value(parse_json_file(p, model=self.model), unsaved_changes)

    def get_fdir(self, path=None, fdir=None):
        if path is not None and fdir is None:
            return pathlib.Path(path).parent
        elif path is None and fdir is not None:
            return fdir
        elif path is not None and fdir is not None:
            return fdir
        else:
            return None


def get_from_schema_root(schema: ty.Dict, key: ty.AnyStr) -> ty.AnyStr:
    return schema[key] if key in schema.keys() else ""


class AutoRenderMethods:
    @classmethod
    def create_autoui_renderer(
        cls, schema: ty.Union[ty.Type[BaseModel], dict], path=None, **kwargs
    ):
        if isinstance(schema, dict):
            docstring = f"AutoRenderer for {get_from_schema_root(schema, 'title')}"
        else:
            docstring = f"AutoRenderer for {get_from_schema_root(schema.model_json_schema(), 'title')}"

        class AutoRenderer(cls):
            def __init__(self, path: pathlib.Path = path):
                f"""{docstring}"""
                if path is None:
                    raise ValueError("must give path")
                super().__init__(schema, path=path, value=None, **kwargs)

        return AutoRenderer

    @classmethod
    def create_autodisplay_map(
        cls, schema: ty.Union[ty.Type[BaseModel], dict], ext=".json", **kwargs
    ):
        AutoRenderer = cls.create_autoui_renderer(schema, **kwargs)
        return {ext: AutoRenderer}


# +
class AutoUi(w.VBox, AutoObjectFormLayout, AutoUiFileMethods, AutoRenderMethods):

    """extends AutoObject and AutoUiCommonMethods to create an
    AutoUi user-input form. The data that can be saved to a json
    file `path` and loaded from a json file.

    Attributes:

        # AutoFileMethods
        # ------------------------------
        path (tr.Instance(klass=pathlib.PurePath, ... ): path to file

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
        auto_open (bool, optional): automatically opens the nested_widget. Defaults to True.
        order (list): allows user to re-specify the order for widget rows to appear by key name in self.di_widgets
        order_can_hide_rows (bool): allows user to hide rows by removing them from the order list.
        insert_rows (dict): e.g. {3:w.Button()}. allows user to insert a widget into the rows. its presence
            is ignored by the widget otherwise.
        disabled (bool, optional): disables all widgets. If widgets are disabled
            using schema kwargs this is remembered when re-enabled. Defaults to False.

    """

    schema = tr.Dict()
    model = tr.Type(klass=BaseModel, default_value=None, allow_none=True)
    _value = tr.Any()  # TODO: update trait type on schema change

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """this is for setting the value via the API"""
        if value is not None:
            self.autowidget.value = value

    @tr.observe("schema")
    def _schema(self, on_change):
        self.caller = map_widget(self.schema)
        self.autowidget = widgetcaller(self.caller)
        self.children = [self.autowidget]

    @property
    def jsonschema_caller(self):
        return summarize_di_callers(self)

    def __init__(
        self,
        schema,
        **kwargs,
    ):
        """initialises the AutoUi. in Jupyter hit "cntrl + I" to load "inspector"
        and see the attributes.

        Args:
            schema (ty.Union[ty.Type[BaseModel], dict]): defines the form
            value (dict, optional): form value. Defaults to None.
            path (pathlib.Path, optional): read / write file location. Defaults to None.
            update_map_widgets (dict, optional): allows user to update the map_widgets. Defaults to None.
            fns_onsave (list, optional): list of functions to run on save. Defaults to None.
            fns_onrevert (list, optional): list of functions to run on revert. Defaults to None.
            **kwargs: passed to AutoObject. see attributes for details.
        """
        kwargs["model"], kwargs["schema"] = _init_model_schema(schema)

        super().__init__(
            **kwargs,
        )
        # self.path = path
        if "value" in kwargs:
            self.value = self._get_value(kwargs["value"], self.path)
            self.savebuttonbar.unsaved_changes = False
        self.children = [
            self.savebuttonbar,
            self.hbx_title,
            self.html_description,
            self.autowidget,
            self.vbx_showraw,
        ]
        self._init_controls()
        self._watch_change({"new": None})
        {
            setattr(self.autowidget, k, v)
            for k, v in kwargs.items()
            if k not in self.trait_names() and k in self.autowidget.trait_names()
        }  # pass traits to autowidget on init.

    def _init_controls(self):
        self._init_watch_widget()

    def _init_watch_widget(self):
        v = self.autowidget
        if v.has_trait("value"):
            logger.debug(f"value trait found for: {v.value}")
            v.observe(self._watch_change, "value")
        elif v.has_trait("_value"):
            logger.debug(f"_value trait found for: {v.value}")
            v.observe(self._watch_change, "_value")
        else:
            pass

    def _watch_change(self, on_change):
        if on_change["new"] != self._value:
            self._value = self.autowidget.value
            if hasattr(self, "savebuttonbar"):
                self.savebuttonbar.unsaved_changes = True
            # NOTE: it is required to set the whole "_value" otherwise
            #       traitlets doesn't register the change.

    def get_fdir(self, path=None, fdir=None):
        if path is not None and fdir is None:
            return pathlib.Path(path).parent
        elif path is None and fdir is not None:
            return fdir
        elif path is not None and fdir is not None:
            return fdir
        else:
            return None

    @property
    def json(self):
        return json.dumps(self.autowidget.value, indent=4)


def summarize_di_callers(obj: AutoUi):  # NOTE: mainly used for demo
    fn_ser = lambda k, v: str(v) if k == "autoui" else v
    fn_item = lambda v: {
        k_: fn_ser(k_, v_) for k_, v_ in v.model_dump().items() if k_ != "schema_"
    }
    if hasattr(obj.autowidget, "di_callers"):  # AutoObject
        return {k: fn_item(v) for k, v in obj.autowidget.di_callers.items()}
    else:  # root item
        return fn_item(obj.caller)


#     @classmethod
#     def from_json_schema(cls, schema):
#         schema = replace_refs(schema)

#     def from_pydantic_model(cls, model):
#         schema = replace_refs(model.model_json_schema())


if __name__ == "__main__":
    from ipyautoui.demo_schemas import CoreIpywidgets

    fn = lambda: print("asdf")
    fn.__name__ = "asdf"
    aui = AutoUi(
        CoreIpywidgets,
        path=pathlib.Path("test.json"),
        show_description=True,
        show_raw=True,
        show_savebuttonbar=True,
        fns_onsave=[fn],
    )
    # aui.show_savebuttonbar = False
    display(aui)

# +

# -

if __name__ == "__main__":
    from ipyautoui.demo_schemas import EditableGrid

    fn = lambda: print("asdf")
    fn.__name__ = "asdf"
    aui = AutoUi(
        EditableGrid,
        path=pathlib.Path("test.json"),
        show_description=True,
        show_raw=True,
        show_savebuttonbar=True,
        fns_onsave=[fn],
    )
    # aui.show_savebuttonbar = False
    display(aui)

if __name__ == "__main__":
    from ipyautoui.demo_schemas import RootSimple

    fn = lambda: print("asdf")
    fn.__name__ = "asdf"
    aui = AutoUi(
        RootSimple,
        path=pathlib.Path("test.json"),
        show_description=True,
        show_raw=True,
        show_savebuttonbar=True,
        fns_onsave=[fn],
    )
    # aui.show_savebuttonbar = False
    display(aui)

if __name__ == "__main__":
    from ipyautoui.demo_schemas import RootArray

    fn = lambda: print("asdf")
    fn.__name__ = "asdf"
    aui = AutoUi(
        RootArray,
        path=pathlib.Path("test.json"),
        show_description=True,
        show_raw=True,
        show_savebuttonbar=True,
        fns_onsave=[fn],
    )
    # aui.show_savebuttonbar = False
    display(aui)
