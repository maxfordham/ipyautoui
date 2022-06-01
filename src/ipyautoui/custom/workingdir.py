# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
"""
a UI element that loads a folder for data caching, whilst storing a record of folders in use
"""

# %run __init__.py
# %load_ext lab_black
# -

from pydantic import BaseModel, validator, Field
from ipyautoui.constants import LOAD_BUTTON_KWARGS, BUTTON_MIN_SIZE, BUTTON_WIDTH_MIN
from IPython.display import clear_output, Markdown
from ipyautoui._utils import file
import shutil
import traitlets_paths
import ipywidgets as widgets
import traitlets
from mf_file_utilities.applauncher_wrapper import get_fpth_win
from getpass import getuser
import os
from halo import HaloNotebook
from enum import Enum, IntEnum
import pathlib
from pydantic import BaseModel, ValidationError
import typing
from datetime import datetime
import zipfile
import logging
import seedir
from ipyautoui._utils import obj_to_importstr

# +
setattr(BaseModel, "file", file)

logging.basicConfig(
    level=logging.WARNING
)  # All events at or above debug level will get logged
logging.debug("This will get logged")  # Sent to the console

# +
FDIR_PROJECTS_ROOT = pathlib.Path("/home/jovyan/jobs")
FPTH_WORKING_DIRS = (
    FDIR_PROJECTS_ROOT / "J4321" / "Data" / "working_dirs" / "working_dirs.json"
)


def get_projects():
    return [p.stem for p in list(pathlib.Path(FDIR_PROJECTS_ROOT).glob(pattern="*"))]


# +
class RibaStages(str, Enum):
    stage1 = "Stage1"
    stage2 = "Stage2"
    stage3 = "Stage3"
    stage4 = "Stage4"
    stage5 = "Stage5"
    stage6 = "Stage6"
    stage7 = "Stage7"


class ProcessSubType(str, Enum):
    wufi = "wufi"
    tm52 = "tm52"
    tm54 = "tm54"
    tm59 = "tm59"
    compliance = "compliance"
    compliance_london_plan = "compliance_london_plan"


class Usage(BaseModel):
    user: str
    timestamp: datetime


class WorkingDir(BaseModel):
    process_type: str
    process_subtype: str
    project_number: str
    riba_stage: RibaStages
    fdir: pathlib.Path = None
    key: str = None
    usage: typing.List[Usage] = Field(default_factory=lambda: [])
    dir_model: str

    @validator("fdir", always=True, pre=True)
    def _fdir(cls, v, values):
        return (
            FDIR_PROJECTS_ROOT
            / values["project_number"]
            / values["process_type"]
            / values["process_subtype"]
            / values["riba_stage"].value
        )

    @validator("key", always=True, pre=True)
    def _key(cls, v, values):
        return (
            # ("J" + str(values["project_number"]))
            values["project_number"]
            + "-"
            + values["process_type"]
            + "-"
            + values["process_subtype"]
            + "-"
            + values["riba_stage"].value
        )


description = """
a list of all the active working directories used for jupyter / ipyrun based analyses / processes / workflows
"""


class WorkingDirs(BaseModel):
    name: str = "working dirs"
    description: str = description
    dirs: typing.Dict[str, WorkingDir] = Field(default_factory=lambda: {})


# + tags=[]
def get_user():
    """get user. gets JUPYTERHUB_USER if present."""
    nm = "JUPYTERHUB_USER"
    if nm in list(os.environ.keys()):
        return os.environ[nm]
    else:
        return getuser()


def get_working_dirs(path=FPTH_WORKING_DIRS):
    """loads working dir from folder"""
    if path.exists():
        wdirs = WorkingDirs.parse_file(path)
    else:
        wdirs = WorkingDirs()
        wdirs.file(path)
    return wdirs


# get_working_dirs()

# + tags=[]
class AnalysisDir(BaseModel):
    fdir: pathlib.Path
    reference: pathlib.Path = None
    incoming: pathlib.Path = None
    input_data: pathlib.Path = None
    cad: pathlib.Path = None
    images: pathlib.Path = None
    calcs: pathlib.Path = None
    models: pathlib.Path = None
    outputs: pathlib.Path = None

    @validator("reference", always=True, pre=True)
    def _reference(cls, v, values):
        return values["fdir"] / "00_Reference"

    @validator("incoming", always=True, pre=True)
    def _incoming(cls, v, values):
        return values["fdir"] / "01_Incoming"

    @validator("input_data", always=True, pre=True)
    def _input_data(cls, v, values):
        return values["fdir"] / "02_InputData"

    @validator("cad", always=True, pre=True)
    def _cad(cls, v, values):
        return values["fdir"] / "03_CAD"

    @validator("images", always=True, pre=True)
    def _images(cls, v, values):
        return values["fdir"] / "04_Images"

    @validator("calcs", always=True, pre=True)
    def _calcs(cls, v, values):
        return values["fdir"] / "05_Calcs"

    @validator("models", always=True, pre=True)
    def _models(cls, v, values):
        return values["fdir"] / "06_Models"

    @validator("outputs", always=True, pre=True)
    def _outputs(cls, v, values):
        return values["fdir"] / "99_Outputs"


def add_working_dir(
    wdir: typing.Union[dict, WorkingDir],
    # dir_model=AnalysisDir,
    path: pathlib.Path = FPTH_WORKING_DIRS,
):
    """add a working directory to global json log"""
    if isinstance(wdir, dict):
        wdir = WorkingDir(**wdir)
    wdirs = get_working_dirs(path=path).dict(by_alias=False)
    now_usage = [Usage(user=get_user(), timestamp=datetime.now()).dict()]
    if wdir.key in wdirs["dirs"].keys():
        past_usage = wdirs["dirs"][wdir.key]["usage"]
    else:
        wdirs["dirs"][wdir.key] = wdir.dict()
        past_usage = []
    usage = past_usage + now_usage
    wdirs["dirs"][wdir.key]["usage"] = usage
    WorkingDirs(**wdirs).file(path)
    return None


def is_templated_dir(adir: typing.Type[BaseModel]):
    for k, v in adir.dict().items():
        if not v.exists():
            return False
    else:
        return True


def make_dirs(adir):
    for k, v in adir.dict().items():
        if isinstance(v, pathlib.Path):
            v.mkdir(parents=True, exist_ok=True)
    return adir


def return_fdir_status(adir, display_message=True):
    """checks if a dir is already an analysis dir or not"""
    if is_templated_dir(adir):
        if display_message:
            display(
                Markdown(
                    f"""👍 analysis dir already exists here:  
`{adir.fdir}`  
it will launch on load."""
                )
            )
        return "analysis_dir_exists"
    elif adir.fdir.exists() and not check_if_analysis_dir(adir):
        if display_message:
            display(
                Markdown(
                    f"""⚠️ dir that doensn't match the template already exists here:  
`{adir.fdir}`  
check if you want to add analysis here."""
                )
            )
        return "dir_exists"
    elif not adir.fdir.exists():
        if display_message:
            display(
                Markdown(
                    f"""👍 dir does not currently exist here:  
`{adir.fdir}`  
it will be created on load."""
                )
            )
        return "dir_not_exists"
    else:
        raise ValueError(f"return_fdir_status {adir.fdir} error")


def create_folder_structure(value, model_dirs=AnalysisDir):
    fdir = value["fdir"]
    adir = model_dirs(fdir=fdir)
    status_fdir = return_fdir_status(adir)
    if status_fdir == "analysis_dir_exists":
        pass
    elif status_fdir == "dir_exists":
        make_dirs(adir)
    elif status_fdir == "dir_not_exists":
        make_dirs(adir)
    else:
        raise ValueError(f"create_folder_structure {wdir.fdir} error")


# +
class WorkingDirsUi(widgets.HBox):
    value = traitlets.Dict()
    setup = widgets.ToggleButton(icon="ellipsis-v", layout={"width": BUTTON_WIDTH_MIN})
    load = widgets.Button(**LOAD_BUTTON_KWARGS)
    project_number = widgets.Combobox(
        value="J5001", ensure_option=True, layout={"width": "80px"}
    )
    projects = traitlets.List(default_value=[])
    process_type = widgets.Dropdown(
        value="Calcs",
        options=["Calcs", "Schedule"],
        # disabled=True,
        layout={"width": "80px"},
    )
    process_subtype = widgets.Dropdown(
        value="wufi",
        options=list(ProcessSubType._value2member_map_.keys()),
        # disabled=True,
        layout={"width": "80px"},
    )
    riba_stage = widgets.Dropdown(
        value="Stage1",
        options=list(RibaStages._value2member_map_.keys()),
        # disabled=True,
        layout={"width": "80px"},
    )
    key = widgets.HTML()
    fdir_win = widgets.HTML()
    fdir_win_proposed = widgets.HTML()

    @traitlets.observe("projects")
    def _projects(self, change):
        self.project_number.options = self.projects

    @traitlets.observe("value")
    def _observe_value_key(self, change):
        self.key.value = self.value["key"]

    @traitlets.observe("value")
    def _observe_value_fdir_win_proposed(self, change):
        self.fdir_win_proposed.value = f"<i>{self.fdir_windows}</i>"

    def _update_value(self):
        return WorkingDir(
            project_number=self.project_number.value,
            process_type=self.process_type.value,
            process_subtype=self.process_subtype.value,
            riba_stage=RibaStages(self.riba_stage.value),
            dir_model=obj_to_importstr(self.model_dirs),
        ).dict(by_alias=False)

    @property
    def fdir_windows(self):
        return get_fpth_win(self.value["fdir"])

    def __init__(
        self,
        fn_onload: typing.Union[typing.Callable, typing.List] = lambda: print(
            "fn_onload"
        ),
        model_dirs: typing.Type[BaseModel] = AnalysisDir,
        fix_attributes={},
        projects=get_projects(),
        fdir_projects_root=FDIR_PROJECTS_ROOT,
        fpth_working_dirs=FPTH_WORKING_DIRS,
    ):
        self.projects = projects
        self.fdir_projects_root = fdir_projects_root
        self.fpth_working_dirs = fpth_working_dirs
        self.model_dirs = model_dirs
        self.fn_onload = fn_onload
        super().__init__(
            layout=widgets.Layout(justify_content="flex-end")
        )  # layout={"align-content": "flex-end"}
        self.vbx_main = widgets.VBox()
        self.out = widgets.Output(
            layout=widgets.Layout(justify_content="flex-end", align_content="flex-end")
        )
        self.hbx_select = widgets.HBox(
            layout=widgets.Layout(justify_content="flex-end", align_content="flex-end")
        )
        #     layout=widgets.Layout(justify_content="flex-end")
        # )
        # self.hbx_summary = widgets.HBox(
        #     layout=widgets.Layout(justify_content="flex-end")
        # )
        # self.hbx_message = widgets.HBox(
        #     layout=widgets.Layout(justify_content="flex-end")
        # )
        # self.hbx_summary.children = [self.fdir_win, self.setup]
        # self.children = [self.hbx_summary, self.hbx_select, self.hbx_message]
        self.hbx_select.children = [
            self.project_number,
            self.process_type,
            self.process_subtype,
            self.riba_stage,
            self.fdir_win_proposed,
            self.load,
        ]
        self.vbx_main.children =[self.hbx_select, self.out]
        self.children = [self.vbx_main]
        self._init_controls()
        self.update_from_ui(None)
        self._update_fdir_win()
        self.fix_attributes = fix_attributes

    @property
    def fn_onload(self):
        return self._fn_onload

    @fn_onload.setter
    def fn_onload(self, value):

        if isinstance(value, typing.Callable):
            value = [value]
        elif isinstance(value, typing.List):
            for v in value:
                if not isinstance(v, typing.Callable):
                    raise ValueError(
                        "fn_onload must be a Callable or list of Callables"
                    )
        else:
            raise ValueError("fn_onload must be a Callable or list of Callables")

        self._fn_onload = [add_working_dir, create_folder_structure,] + value

    @property
    def fix_attributes(self):
        return self._fix_attributes

    @fix_attributes.setter
    def fix_attributes(self, value):
        for k, v in value.items():
            setattr(getattr(self, k), "value", v)
            setattr(getattr(self, k), "disabled", True)
        self._fix_attributes = value

    def update_from_ui(self, change):
        self.value = self._update_value()
        with self.out:
            clear_output()
            return_fdir_status(self.model_dirs(fdir=self.value["fdir"]))

    def _init_controls(self):
        self.project_number.observe(self.update_from_ui, "value")
        self.process_type.observe(self.update_from_ui, "value")
        self.process_subtype.observe(self.update_from_ui, "value")
        self.riba_stage.observe(self.update_from_ui, "value")
        # self.setup.observe(self._setup, "value")
        self.load.on_click(self._load)

    # def _setup(self, onchange):
    #     if self.setup.value:
    # self.hbx_select.children = [
    #     self.project_number,
    #     self.process_type,
    #     self.process_subtype,
    #     self.riba_stage,
    #     self.fdir_win_proposed,
    #     self.load,
    # ]
    #         self.hbx_message.children = [self.out]
    #     else:
    #         self.hbx_select.children = []
    #         self.hbx_message.children = []

    def _update_fdir_win(self):
        self.fdir_win.value = f"<b>{self.fdir_windows}</b>"

    def _load(self, onchange):
        self.hbx_select.children = []
        with self.out:
            clear_output()
            spinner = HaloNotebook(text="Loading", spinner="dots")
            spinner.start()
            li = [f(self.value) for f in self.fn_onload]
            # [print(l) for l in li if isinstance(l, typing.Callable)]
            logging.info("this is a loggging message")
            spinner.stop()
            self.setup.value = False
            clear_output()
        self._update_fdir_win()


if __name__ == "__main__":
    fix_attributes = {"process_type": "Calcs", "process_subtype": "wufi"}
    wdir = WorkingDirsUi(fix_attributes=fix_attributes)
    display(wdir)
# -
widgets.HBox(
    [widgets.Button(), widgets.HTML("aasdf")],
    layout=widgets.Layout(justify_content="flex-end"),  # , align_content="flex-end"
)

widgets.HTML("aasdf", layout=widgets.Layout(justify_content="flex-end"))


