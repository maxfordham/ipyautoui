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

import pathlib
from IPython.display import display
from pydantic import BaseModel
import json
import traitlets as tr
import traitlets_paths
import typing as ty

from ipyautoui.custom import SaveButtonBar  # removing makes circular import error
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
    """AutoUiFileMethods is a mixin class that adds file methods to a AutoUi class

    Attributes:
        path (traitlets_paths.Path): path to file
    """

    path = traitlets_paths.Path(allow_none=True)

    @tr.validate("path")
    def _path(self, proposal):
        if proposal["value"] is not None:
            return pathlib.Path(proposal["value"])

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
        return {ext: AutoRenderer}


# +
class AutoUi(AutoObject, AutoUiFileMethods, AutoRenderMethods):
    """extends AutoObject and AutoUiCommonMethods to create an
    AutoUi user-input form. The data that can be saved to a json
    file `path` and loaded from a json file.

    Attributes:
        # inherited from AutoFileMethods
        # ------------------------------
        path (traitlets_paths.Path): path to file

        # inherited from AutoObject
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

        # inherited from AutoObjectFormLayout
        # ----------------------------------
        show_raw (bool, optional): show the raw json. Defaults to False.
        show_description (bool, optional): show the description. Defaults to True.
        show_title (bool, optional): show the title. Defaults to True.
        show_savebuttonbar (bool, optional): show the savebuttonbar. Defaults to True.

    """

    def __init__(
        self,
        schema: ty.Union[ty.Type[BaseModel], dict],
        value: dict = None,
        path: pathlib.Path = None,  # TODO: generalise data retrieval?
        update_map_widgets=None,
        fns_onsave=None,
        fns_onrevert=None,
        # validate_onchange=True,  # TODO: sort out how the validation works
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

        fdir = self.get_fdir(path=path, fdir=kwargs.get("fdir", None))
        # init app
        super().__init__(
            schema,
            value=None,
            update_map_widgets=update_map_widgets,
            fdir=fdir,
            fns_onsave=fns_onsave,
            fns_onrevert=fns_onrevert,
            **kwargs,
        )
        self.path = path
        self.value = self._get_value(value, self.path)

    def get_fdir(self, path=None, fdir=None):

        if path is not None and fdir is None:
            return pathlib.Path(path).parent
        elif path is None and fdir is not None:
            return fdir
        elif path is not None and fdir is not None:
            return fdir
        else:
            return None


if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic, TestAutoLogicSimple

    aui = AutoUi(
        TestAutoLogicSimple,
        path="test.json",
        show_description=False,
        show_raw=True,  
        show_savebuttonbar=False,
    )
    # aui.show_savebuttonbar = False
    display(aui)

# +
# aui.savebuttonbar.layout.display

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
