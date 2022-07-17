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
# TODO: add title and description to nested sections of the UI
# TODO: make layout of name, widget, description configurable...
# %run __init__.py
# #%load_ext lab_black
import logging
import pathlib
import functools
import ipywidgets as widgets
from IPython.display import display, Markdown, clear_output
from pydantic import BaseModel, Field
from markdown import markdown
import immutables
import json
import traitlets
import traitlets_paths
import typing
from enum import Enum

from ipyautoui._utils import display_python_string
from ipyautoui.custom import SaveButtonBar  #  Grid, FileChooser,
from ipyautoui.constants import BUTTON_WIDTH_MIN
from ipyautoui.autoipywidget import AutoIpywidget, AutoPydanticHandler

# from ipyautoui.autovjsf import AutoVjsf

# -


class SaveControls(str, Enum):
    save_buttonbar = "save_buttonbar"
    save_on_edit = "save_on_edit"  #  TODO: test this
    disable_edits = "disable_edits"  #  TODO: implement this
    # archive_versions = 'archive_versions' #  TODO: implement this?


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


# +
def displayfile_renderer(path, renderer=None):
    if renderer is None:
        raise ValueError("renderer must not be None")
    display(renderer(path))


def jsonschema_to_pydantic(
    schema: typing.Type,  #: JsonSchemaObject
    *,
    config: typing.Type = None,  # = JsonSchemaConfig
) -> typing.Type[BaseModel]:
    pass  # TODO: https://github.com/samuelcolvin/pydantic/issues/1638


def get_schema_title(schema):

    if type(schema) != dict:
        schema = schema.schema()
    if "title" in schema.keys():
        return schema["title"]
    else:
        return ""


class AutoUiCommonMethods(traitlets.HasTraits, AutoPydanticHandler):
    """methods for: 
    - reading and writing to file
    - showing raw json form data
    - creating displayfile_renderer and autoui_renderer
    """

    save_controls = traitlets.UseEnum(SaveControls)  # default is save_on_edit
    path = traitlets_paths.Path(allow_none=True)
    show_raw = traitlets.Bool(default_value=True)
    show_description = traitlets.Bool(default_value=True)

    @traitlets.validate("path")
    def _path(self, proposal):
        if proposal["value"] is not None:
            return pathlib.Path(proposal["value"])

    @traitlets.validate("save_controls")
    def _save_controls(self, proposal):
        if self.path is not None:
            map_save_dialogue = immutables.Map(
                save_buttonbar=self.call_save_buttonbar,  # only this one currently works
                save_on_edit=self.call_save_on_edit,
                disable_edits=self.call_disable_edits,
            )
            map_save_dialogue[proposal["value"]]()
        else:
            logging.info("self.path == None. must be a valid path to save as json")

        return proposal["value"]

    @property
    def json(self):
        if self.model is not None:
            return self.model(**self.value).json(indent=4)
        else:
            return json.dumps(self.value, indent=4)

    def _init_AutoUiCommonMethods(self):
        self._init_autoui_form()
        self._init_bn_showraw_controls()
        self._init_observe_show_raw()

    def _init_observe_show_raw(self):
        self.observe(self._show_raw, "show_raw")

    def _show_raw(self, onchange):
        self._update_show_raw()

    def _init_autoui_form(self):
        self._init_titlebox()
        self._init_bn_showraw()
        li = list(self.children)
        li = [self.vbx_header] + li + [self.vbx_raw]
        self.children = li

    def _init_bn_showraw(self):
        self.vbx_raw = widgets.VBox()
        self.out_raw = widgets.Output()
        self.vbx_raw.children = [self.out_raw]

    def _init_titlebox(self):
        # init containers
        self.vbx_header = widgets.VBox()  #  overall header container
        self.hbx_savecontrols = widgets.HBox()  #  with save controls
        self.hbx_title_toggle = widgets.HBox()  #  with show_raw toggle and title
        self.hbx_description = widgets.HBox()  #  with description
        self.vbx_header.children = [
            self.hbx_savecontrols,
            self.hbx_title_toggle,
            self.hbx_description,
        ]

        # init content
        self.title = widgets.HTML(f"<big><b>{self.schema['title']}</b></big>")
        self.bn_showraw = widgets.ToggleButton(
            icon="code",
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
            tooltip="show raw data",
            style={"font_weight": "bold", "button_color": None},
        )
        self._update_show_raw()
        self.description = widgets.HTML()
        self._init_description()

        # fill containers
        self.hbx_title_toggle.children = [self.bn_showraw, self.title]
        self.hbx_description.children = [self.description]

    def _init_description(self):
        if "description" in self.schema.keys():
            self.description.value = markdown(f"{self.schema['description']}")
        if self.show_description:
            self.description.layout.display = ""
        else:
            self.description.layout.display = "None"

    def _update_show_raw(self):
        if self.show_raw:
            self.bn_showraw.layout.display = ""
        else:
            self.bn_showraw.layout.display = "None"

    def _init_bn_showraw_controls(self):
        self.bn_showraw.observe(self._bn_showraw, "value")

    def _bn_showraw(self, onchange):
        if self.bn_showraw.value:
            self.bn_showraw.tooltip = "show user interface"
            self.bn_showraw.icon = "user-edit"
            self.ui_main.layout.display = "None"
            self.vbx_raw.layout.display = ""
            with self.out_raw:
                clear_output()
                display_python_string(self.json)
        else:
            self.bn_showraw.tooltip = "show raw data"
            self.bn_showraw.icon = "code"
            self.ui_main.layout.display = ""
            self.vbx_raw.layout.display = "None"

    def _get_path(self, path=None):
        if path is None:
            if self.path is not None:
                return self.path
            else:
                self.save_buttonbar.message.value = "no filepath give"
                raise ValueError("NO PATH GIVEN: path is None and self.path is None")
        else:
            return path

    def _get_value(self, v, p):
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

    def parse_file(self, path=None):
        if self.path is not None and self.path.is_file():
            return parse_json_file(self.path, model=self.model)
        else:
            raise ValueError("self.path is not None and self.path.is_file() == False")

    def load_file(self, path=None):
        p = self._get_path(path=path)
        self.value = parse_json_file(p, model=self.model)
        try:
            self.save_buttonbar._unsaved_changes(False)
        except:
            pass

    @classmethod
    def create_autoui_renderer(
        cls,
        schema: typing.Union[typing.Type[BaseModel], dict],
        save_controls: SaveControls = SaveControls.save_buttonbar,
        show_raw: bool = True,
        fn_onsave: typing.Union[
            typing.Callable, typing.List[typing.Callable]
        ] = lambda: None,
        path=None,
    ):
        # ext = path.suffixes.join(".")
        docstring = f"AutoRenderer for {get_schema_title(schema)}"

        class AutoRenderer(cls):
            def __init__(self, path: pathlib.Path = path):
                f"""{docstring}"""
                if path is None:
                    raise ValueError("must give path")
                super().__init__(
                    schema,
                    path=path,
                    value=None,
                    save_controls=save_controls,
                    show_raw=show_raw,
                    fn_onsave=fn_onsave,
                )

        return AutoRenderer

    @classmethod
    def create_autodisplay_map(
        cls,
        schema: typing.Union[typing.Type[BaseModel], dict],
        ext=".json",
        save_controls: SaveControls = SaveControls.save_buttonbar,
        show_raw: bool = True,
        fn_onsave: typing.Union[
            typing.Callable, typing.List[typing.Callable]
        ] = lambda: None,
    ):
        AutoRenderer = cls.create_autoui_renderer(
            schema, save_controls=save_controls, show_raw=show_raw, fn_onsave=fn_onsave
        )
        docstring = f"AutoRenderer for {get_schema_title(schema)}"
        return {ext: AutoRenderer}

    def _revert(self):  # TODO: check this!
        assert self.path is not None, f"self.path = {self.path}. must not be None"
        self.load_file(self.path)
        self.save_buttonbar._unsaved_changes(False)

    def call_save_buttonbar(self):
        self.save_buttonbar = SaveButtonBar(
            save=self.file, revert=self._revert, fn_onsave=self.fn_onsave,
        )
        self.hbx_savecontrols.children = [self.save_buttonbar]
        self.fn_onvaluechange = functools.partial(
            self.save_buttonbar._unsaved_changes, True
        )
        self.save_buttonbar._unsaved_changes(False)
        self.observe(self.call_unsaved_changes, "_value")

    def call_unsaved_changes(self, on_change):
        self.fn_onvaluechange()

    def call_save_on_edit(self):
        pass  # TODO - call_save_on_edit

    def call_disable_edits(self):
        pass  # TODO - call_disable_edits

    # def _init_model_schema(self, schema):
    #     if type(schema) == dict:
    #         model = None  # jsonschema_to_pydantic(schema)  # TODO: do this!
    #     else:
    #         model = schema  # the "model" passed is a pydantic model
    #         schema = model.schema(by_alias=False)
    #     return model, schema


class AutoUi(AutoIpywidget, AutoUiCommonMethods):
    """extends AutoIpywidget and AutoUiCommonMethods to create an 
    AutoUi capable of interacting with a json file"""

    def __init__(
        self,
        schema: typing.Union[typing.Type[BaseModel], dict],
        value: dict = None,
        path: pathlib.Path = None,  # TODO: generalise data retrieval?
        save_controls: SaveControls = SaveControls.save_buttonbar,
        show_raw: bool = True,
        fn_onsave: typing.Union[
            typing.Callable, typing.List[typing.Callable]
        ] = lambda: None,
        validate_onchange=True,  # TODO: sort out how the validation works
        update_fdir_to_path_parent=True,
    ):
        self.path = path
        if self.path is not None:
            self.fdir = str(self.path.parent)  # TODO: use traitlets_paths
        else:
            self.fdir = None
        self.show_raw = show_raw

        # accept schema or pydantic schema
        self.model, schema = self._init_model_schema(schema)
        self.value = self._get_value(value, self.path)

        # list of actions to be called on save
        self.fn_onsave = fn_onsave

        # init app
        super().__init__(
            schema=schema, value=self.value, widgets_mapper=None, fdir=self.fdir,
        )
        self._init_AutoUiCommonMethods()
        self.save_controls = save_controls


# -

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic, TestAutoLogicSimple

    schema = TestAutoLogicSimple.schema()
    aui = AutoUi(
        TestAutoLogicSimple,
        path="test.json",
        show_raw=False,
        fn_onsave=lambda: print("test onsave"),
    )
    display(aui)

# + tags=[]
if __name__ == "__main__":
    # Renderer = AutoUi.create_autoui_renderer(schema)
    Renderer = AutoUi.create_autoui_renderer(
        TestAutoLogic, path="test.json", show_raw=False
    )
    display(Renderer(path="test1.json"))


# -


if __name__ == "__main__":

    class AnalysisPaths(BaseModel):
        analysis_type: str = Field(
            default=None,
            enum=["Overheating", "PartL", "Daylighting", "WUFI"],
            autoui="ipyautoui.autowidgets.Combobox",
        )
        project_stage: str = Field(
            default=None,
            enum=["Stage1", "Stage2", "Stage3", "Stage4"],
            autoui="ipyautoui.autowidgets.Combobox",
        )

    aui = AutoUi(AnalysisPaths, show_raw=True)
    display(aui)



