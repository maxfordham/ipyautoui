# +
"""autoui is used to automatically create ipywidget user input (UI) form from a pydantic model or jsonschema.

Pydantic fields are mapped to appropriate widgets based on type to display the data in the UI.
It also supports extension, but mapping custom datatypes onto custom widget classes.

Example:

    from ipyautoui import AutoUi, demo
    demo()
"""


import pathlib
import json
import logging
import functools
import traitlets as tr
import typing as ty
import ipywidgets as w
from pydantic import BaseModel, ValidationError
from IPython.display import display

from ipyautoui.custom import SaveButtonBar  # removing makes circular import error
from ipyautoui.autobox import AutoBox
from ipyautoui.autoform import (
    AutoObjectFormLayout,
    TitleDescription,
    WrapSaveButtonBar,
    ShowRaw,
    ShowNull,
)
from ipyautoui.custom.editgrid import EditGrid
from ipyautoui.automapschema import (
    get_widgets_map,
    get_containers_map,
    map_widget,
    widgetcaller,
    _init_model_schema,
    pydantic_validate,
)

logger = logging.getLogger(__name__)


# +
def wrapped_partial(func, *args, **kwargs):
    # http://louistiao.me/posts/adding-__name__-and-__doc__-attributes-to-functoolspartial-objects/
    partial_func = functools.partial(func, *args, **kwargs)
    functools.update_wrapper(partial_func, func)
    return partial_func


def parse_json_file(path: pathlib.Path, model=None):
    """read json from file"""
    p = pathlib.Path(path)
    if model is not None:
        return model(
            **json.loads(p.read_text())
        ).model_dump()  # json.loads(model.parse_file(p).json())
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
        elif v is None and p is not None and p.is_file():
            # load v from p
            return self.parse_file(path=p)
        elif v is None and p is not None and not p.is_file():
            # v reverts to schema defaults
            return None
        elif v is not None:
            if p is not None and p.is_file():
                logger.warning("both a value and a path given. value will be used.")
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


class AutoRenderMethods:  # NOT IN USE
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


def get_autoui(schema: ty.Union[ty.Type[BaseModel], dict], **kwargs):
    model, schema = _init_model_schema(schema)
    schema = {**schema, **kwargs}
    try:
        # assumes the root object is a container so reduces the search space
        caller = map_widget(
            schema, widgets_map=get_containers_map(), fail_on_error=True
        )
        is_container = True
        if issubclass(caller.autoui, EditGrid):
            li = [caller.autoui, TitleDescription, ShowRaw, AutoUiFileMethods]

            class AutoUi(*li):
                def _set_children(self):
                    self.children = [
                        w.HBox([self.bn_showraw, self.html_title]),
                        self.html_description,
                        self.vbx_error,
                        self.vbx_widget,
                        self.vbx_showraw,
                    ]

        else:

            class AutoUi(
                caller.autoui,
                ShowRaw,
                ShowNull,
                TitleDescription,
                WrapSaveButtonBar,
                AutoUiFileMethods,
            ):
                def _set_children(self):
                    self.children = [
                        self.savebuttonbar,
                        w.HBox([self.bn_showraw, self.bn_shownull, self.html_title]),
                        self.html_description,
                        self.vbx_error,
                        self.vbx_widget,
                        self.vbx_showraw,
                    ]
                    self.show_hide_bn_nullable()

        if model is not None:
            return wrapped_partial(
                AutoUi.from_pydantic_model, model
            )  # TODO: this is inefficient as the top-level mapping is called twice.
        else:
            return wrapped_partial(AutoUi.from_jsonschema, schema)

    except:
        # increases the search spaces to include all widgets
        caller = map_widget(schema, widgets_map=get_widgets_map())
        is_container = False
        return wrapped_partial(
            AutoBox.wrapped_widget,
            caller.autoui,
            kwargs_box=caller.kwargs_box,
            kwargs_fromcaller=caller.kwargs,
        )


def get_autodisplay_map(
    schema: ty.Union[ty.Type[BaseModel], dict], ext=".json", **kwargs
):
    ui = get_autoui(schema, **kwargs)

    def renderer(
        path: pathlib.Path,
    ):  # TODO: this is a hack. better to generalise CRUD operations.
        _ui = ui(value=None, **kwargs)
        _ui.path = path
        _ui.load_file(path)
        _ui.savebuttonbar.unsaved_changes = False
        return _ui

    return {ext: renderer}


def autoui(schema: ty.Union[ty.Type[BaseModel], dict], value=None, path=None, **kwargs):
    """
    Example:
    
        from ipyautoui import AutoUi
        from ipyautoui.demo_schemas import CoreIpywidgets
        AutoUi(CoreIpywidgets)
    """
    ui = get_autoui(schema, **kwargs)  # TODO: resolve how path is handled
    if value is None:
        return ui(**kwargs)
    else:
        return ui(value=value, **kwargs)


AutoUi = autoui


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
