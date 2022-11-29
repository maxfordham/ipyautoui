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
# %run __init__.py
# #%load_ext lab_black

import pathlib
from IPython.display import display
from pydantic import BaseModel
import json
import traitlets as tr
import traitlets_paths
import typing as ty

from ipyautoui.custom import (
    SaveButtonBar,
)  # NOTE: removing this unused import creates circular import errors
from ipyautoui.autoipywidget import AutoObject, get_from_schema_root


# +


def rename_vjsf_schema_keys(obj, old="x_", new="x-"):
    """recursive function to replace all keys beginning x_ --> x-
    this allows schema Field keys to be definied in pydantic and then
    converted to vjsf compliant schema"""

    if type(obj) == list:
        for l in list(obj):
            if type(l) == str and l[0:2] == old:
                l = new + l[2:]
            if type(l) == list or type(l) == dict:
                l = rename_vjsf_schema_keys(l)
            else:
                pass
    if type(obj) == dict:
        for k, v in obj.copy().items():
            if k[0:2] == old:
                obj[new + k[2:]] = v
                del obj[k]
            if type(v) == list or type(v) == dict:
                v = rename_vjsf_schema_keys(v)
            else:
                pass
    else:
        pass
    return obj


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
    path = traitlets_paths.Path(allow_none=True)

    @tr.validate("path")
    def _path(self, proposal):
        if proposal["value"] is not None:
            return pathlib.Path(proposal["value"])

    @tr.observe("path")
    def _observe_path(self, proposal):
        self.savebuttonbar.fns_onsave_add_action(self.file, to_beginning=True)
        self.savebuttonbar.fns_onrevert_add_action(self.load_file, to_beginning=True)
        self.show_savebuttonbar = True

    def _get_path(self, path=None):
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
            return self.parse_file()
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
            return parse_json_file(self.path, model=self.model)
        else:
            raise ValueError("path.is_file() == False")

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


# +


class AutoRenderMethods:
    @classmethod
    def create_autoui_renderer(
        cls,
        schema: ty.Union[ty.Type[BaseModel], dict],
        show_raw: bool = True,
        path=None,
        fns_onsave=None,
        fns_onrevert=None,
    ):
        if isinstance(schema, dict):
            docstring = f"AutoRenderer for {get_from_schema_root(schema, 'title')}"
        else:
            docstring = (
                f"AutoRenderer for {get_from_schema_root(schema.schema(), 'title')}"
            )

        # TODO: revert to using *args and **kwargs for these types of wrappers
        #       so they only need redefining once in the main __init__

        class AutoRenderer(cls):
            def __init__(self, path: pathlib.Path = path):
                f"""{docstring}"""
                if path is None:
                    raise ValueError("must give path")
                super().__init__(
                    schema,
                    path=path,
                    value=None,
                    show_raw=show_raw,
                    fns_onsave=fns_onsave,
                    fns_onrevert=fns_onrevert,
                )

        return AutoRenderer

    @classmethod
    def create_autodisplay_map(
        cls,
        schema: ty.Union[ty.Type[BaseModel], dict],
        ext=".json",
        show_raw: bool = True,
        fns_onsave=None,
        fns_onrevert=None,
    ):
        AutoRenderer = cls.create_autoui_renderer(
            schema, show_raw=show_raw, fns_onsave=fns_onsave, fns_onrevert=fns_onrevert
        )
        # if isinstance(schema, dict):
        #     AutoRenderer.__doc__ = (
        #         f"AutoRenderer for {get_from_schema_root(schema, 'title')}"
        #     )
        # else:
        #     AutoRenderer.__doc__ = (
        #         f"AutoRenderer for {get_from_schema_root(schema.schema(), 'title')}"
        #     )
        return {ext: AutoRenderer}


# +
class AutoUi(AutoObject, AutoUiFileMethods, AutoRenderMethods):
    """extends AutoObject and AutoUiCommonMethods to create an
    AutoUi capable of interacting with a json file"""

    def __init__(
        self,
        schema: ty.Union[ty.Type[BaseModel], dict],
        value: dict = None,
        path: pathlib.Path = None,  # TODO: generalise data retrieval?
        show_raw: bool = True,
        validate_onchange=True,  # TODO: sort out how the validation works
        update_fdir_to_path_parent=True,
        **kwargs,
    ):

        if path is not None:
            fdir = str(pathlib.Path(path).parent)  # TODO: use traitlets_paths
        else:
            fdir = None

        # init app
        super().__init__(
            schema, value=value, update_map_widgets=None, fdir=fdir, **kwargs
        )
        self.path = path
        self.show_raw = show_raw


if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic, TestAutoLogicSimple

    aui = AutoUi(
        TestAutoLogicSimple,
        path="test.json",
        show_raw=True,
    )
    aui.show_savebuttonbar = True
    display(aui)

# + active=""
# aui.save_actions.fns_onrevert[1]()

# + active=""
# aui.value = parse_json_file(aui._get_path(), model=aui.model)

# + active=""
# v = {'string': 'asdfasdfasdfasdf',
#  'int_slider': 1,
#  'int_text': 1,
#  'int_range_slider': (0, 3),
#  'float_slider': 2,
#  'float_text': 2.2,
#  'float_text_locked': 2.2,
#  'float_range_slider': (0.0, 2.2),
#  'checkbox': True,
#  'dropdown': 'male',
#  'dropdown_edge_case': 'female',
#  'dropdown_simple': 'asd',
#  'combobox': 'asd',
#  'text': 'short text',
#  'text_area': 'long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text long text ',
#  'markdown': '\nSee details here: [__commonmark__](https://commonmark.org/help/)\n\nor press the question mark button. \n'}

# +

if __name__ == "__main__":
    TestRenderer = AutoUi.create_autoui_renderer(TestAutoLogicSimple, path="test.json")
    r = TestRenderer()
    r.show_savebuttonbar = True
    display(r)


if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic, TestAutoLogicSimple

    aui = AutoUi(
        TestAutoLogicSimple,
        path="test.json",
        show_raw=True,
        fn_onsave=lambda: print("test onsave"),
    )
    display(aui)
# -

if __name__ == "__main__":
    aui.show_description = False
    aui.show_title = False
    aui.show_raw = False

# + tags=[]
if __name__ == "__main__":
    # Renderer = AutoUi.create_autoui_renderer(schema)
    from ipyautoui.autoipywidget import get_from_schema_root

    Renderer = AutoUi.create_autoui_renderer(TestAutoLogic, show_raw=False)
    display(Renderer(path="test1.json"))
