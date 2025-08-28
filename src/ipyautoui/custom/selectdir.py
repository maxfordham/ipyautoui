# +


from IPython.display import display
from ipyautoui.basemodel import BaseModel
from ipyautoui.basemodel import file
from ipyautoui._utils import file

setattr(BaseModel, "file", file)
from pydantic import ConfigDict, validator, Field, ValidationError
from ipyautoui.constants import LOAD_BUTTON_KWARGS
from IPython.display import clear_output, Markdown

import ipywidgets as w
import traitlets as tr
import typing as ty
import pathlib
from datetime import datetime
from ipyautoui._utils import obj_to_importstr, getuser, make_new_path
from ipyautoui.custom.decision_branch import DecisionUi, TreeModel

# -

try:
    NAME = __spec__.name
except:
    NAME = "__main__."

FDIR_PROJECTS_ROOT = pathlib.Path("/home/jovyan/jobs")
FDIR_LOG_DIRS = FDIR_PROJECTS_ROOT / "J4321" / "Data" / "working_dirs"
FPTH_WORKING_DIRS = FDIR_LOG_DIRS / "working_dirs.json"


# +
class Usage(BaseModel):
    user: str
    timestamp: datetime


from pydantic import PyObject
from ipyautoui._utils import obj_to_importstr


class SelectDirBase(BaseModel):
    fdir_root: pathlib.Path = FDIR_PROJECTS_ROOT
    fdir_log: pathlib.Path = FDIR_LOG_DIRS
    tags: list
    key: str = None
    fdir: pathlib.Path = None
    fpth_log: pathlib.Path = None
    app_name: str = None
    pyobject_read_dir: str = None

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("key", always=True, pre=True)
    def _key(cls, v, values):
        return ("-").join(values["tags"])

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("fdir", always=True, pre=True)
    def _fdir(cls, v, values):
        parts = list(values["fdir_root"].parts) + values["tags"]
        return pathlib.Path(*parts)

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("fpth_log", always=True, pre=True)
    def _fpth_log(cls, v, values):
        if values["fdir_log"] is not None:
            fnm = values["key"] + ".json"
            return pathlib.Path(values["fdir_log"]) / fnm
        else:
            return None

    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={PyObject: obj_to_importstr})


class SelectDir(SelectDirBase):
    usage: ty.List[Usage] = Field(default_factory=lambda: [])
    pyobject: str = NAME + ".SelectDir"


# -

if __name__ == "__main__":

    def get_projects():
        return [
            p.stem for p in list(pathlib.Path(FDIR_PROJECTS_ROOT).glob(pattern="*"))
        ]

    PROJECTS = get_projects()

    config = TreeModel(
        **{
            "options": PROJECTS,
            "placeholder": "select Project...",
            "children": {
                "options": ["Schedule"],
                "disabled": True,
                "value": "Schedule",
            },
            "value": "J5001",
        }
    )
    ui = DecisionUi(config)
    display(ui)

# +
from datetime import datetime
from ipyautoui.basemodel import file


# READ WRITE TO FILE.
def record_load(value):
    fpth_log = value["fpth_log"]
    if fpth_log.is_file():
        log = SelectDir.parse_file(fpth_log)
    else:
        log = SelectDir(**value)
    log.usage.append(Usage(user=getuser(), timestamp=datetime.now()))
    print(log.model_dump())
    file(log, fpth_log)


def print_fdir(value):
    print(f"fn_onload: {value['fdir']}")


class SelectDirUi(w.VBox):
    value = tr.Dict()

    @tr.validate("value")
    def _validate_value(self, proposal):
        try:
            v = SelectDirBase(**proposal["value"])
        except ValidationError as e:
            raise tr.TraitError(e)
        if v.fpth_log.is_file():
            v = SelectDir.parse_file(v.fpth_log)

        return v.model_dump()

    @tr.observe("value")
    def _observe_value_update_path(self, change):
        self.display_path.value = str(make_new_path(self.fdir))

    @tr.observe("value")
    def _observe_value_run_checks(self, change):
        if self.checks is not None:
            messages = []
            for c in self.checks:
                try:
                    messages = messages + [c(self.value)]
                except:
                    pass
            messages = [m for m in messages if m is not None]
            if len(messages) >= 1:
                with self.out:
                    clear_output()
                    [display(Markdown(m)) for m in messages]

    def __init__(
        self,
        config: TreeModel,
        fdir_root: pathlib.Path = None,
        fdir_log: pathlib.Path = None,
        fn_onload: ty.Union[ty.Callable, ty.List] = print_fdir,
        checks: ty.List[ty.Callable] = None,
    ):
        """
        select a directory through a decision tree

        Args:
            config: TreeModel, defines the choices to give to user
            fdir_root: pathlib.Path, new path built on this one
            fdir_log: pathlib.Path, on load a record is added here
            fn_onload: ty.Callable, called on load, passed the "value" trait as an arg
            checks: ty.List[ty.Callable]: a list of callables. each callable is
                initiated with the "value" trait as an arg and returns either a string
                or None
        """
        self.load = w.Button(**dict(LOAD_BUTTON_KWARGS) | {"tooltip": "load project"})
        super().__init__()
        if fdir_root is None:
            self.fdir_root = pathlib.Path(".")
        else:
            self.fdir_root = fdir_root
        self.fdir_log = fdir_log
        self.fn_onload = fn_onload

        self.select = DecisionUi(config)
        self.out = w.Output()
        self.hbx_out = w.HBox([self.out], layout=w.Layout(justify_content="flex-end"))
        self.hbx_select = w.HBox(layout=w.Layout(justify_content="flex-end"))
        self.display_path = w.HTML()
        self.hbx_select.children = [
            self.select,
            self.display_path,
            self.load,
        ]
        self.children = [self.hbx_select, self.hbx_out]
        self._init_controls()
        self.checks = checks
        self.value = {"tags": self.select.value}

    def _init_controls(self):
        self.select.observe(self._update_value, "_value")
        self.load.on_click(self._load)

    def _load(self, onclick):
        [f(self.value) for f in self.fn_onload]

    def _update_value(self, onchange):
        self.value = {
            "tags": onchange["new"],
            "fdir_root": self.fdir_root,
            "fdir_log": self.fdir_log,
        }

    @property
    def fdir(self):
        try:
            return self.value["fdir"]
        except:
            return ""

    @property
    def fn_onload(self):
        return self._fn_onload

    @fn_onload.setter
    def fn_onload(self, value):
        if isinstance(value, ty.Callable):
            value = [value]
        elif isinstance(value, ty.List):
            for v in value:
                if not isinstance(v, ty.Callable):
                    raise ValueError(
                        "fn_onload must be a Callable or list of Callables"
                    )
        else:
            raise ValueError("fn_onload must be a Callable or list of Callables")
        self._fn_onload = [record_load] + value


if __name__ == "__main__":
    c1_str_exists = "📁👍 - `{}` : folder exists in location. press to load."
    c1_str_not_exists = (
        "📁⚠️ - `{}` : folder does not exist in location. It will be created on load"
    )
    c1 = lambda value: (
        c1_str_exists.format(make_new_path(value["fdir"]))
        if value["fdir"].is_dir()
        else c1_str_not_exists.format(make_new_path(value["fdir"]))
    )

    def c2(value):
        if len(list(sdir.value["fdir"].glob(pattern=".aecschedule"))) == 0:
            return "🔧⚠️ - `{}` : not yet configured for schedules, it will be configured on load.".format(
                make_new_path(value["fdir"])
            )
        else:
            return "🔧👍 - `{}` : already configured for `aecschedule`, press to load folder.".format(
                make_new_path(value["fdir"])
            )

    config = TreeModel(
        **{
            "options": PROJECTS,
            "placeholder": "select Project...",
            "children": {
                "options": ["Schedule"],
                "disabled": True,
                "value": "Schedule",
            },
            "value": "J5001",
        }
    )
    sdir = SelectDirUi(
        config, fdir_root=FDIR_PROJECTS_ROOT, fdir_log=".", checks=[c1, c2]
    )
    display(sdir)
# -
