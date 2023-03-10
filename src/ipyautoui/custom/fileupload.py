"""file upload wrapper"""
# %load_ext lab_black
# %run _dev_sys_path_append.py
# %run __init__.py
# %run ../__init__.py

import ipywidgets as w
from markdown import markdown
from IPython.display import display, clear_output
from pydantic import BaseModel, validator, Field
import pathlib
import typing as ty
import stringcase
from datetime import datetime
import traitlets as tr
import json
import logging

from ipyautoui.constants import DELETE_BUTTON_KWARGS
from ipyautoui._utils import getuser
from ipyautoui.autodisplay import DisplayObject, DisplayPath
from ipyautoui.custom.iterable import Array
from ipyautoui.autodisplay_renderers import render_file
from ipyautoui.env import Env

IPYAUTOUI_ROOTDIR = Env().IPYAUTOUI_ROOTDIR
IS_IPYWIDGETS8 = (lambda: True if "8" in w.__version__ else False)()
logger = logging.getLogger(__name__)

class File(BaseModel):
    name: str
    fdir: pathlib.Path = pathlib.Path(".")
    path: pathlib.Path = None

    @validator("path", always=True, pre=True)
    def _path(cls, v, values):
        return values["fdir"] / values["name"]


def read_file_upload_item(di: dict, fdir=pathlib.Path("."), added_by=None):
    if added_by is None:
        added_by = getuser()
    if IS_IPYWIDGETS8:
        _ = di
    else:
        _ = di["metadata"]
    _["fdir"] = fdir
    _["added_by"] = added_by
    return File(**_)


def add_file(upld_item, fdir=pathlib.Path(".")):
    f = read_file_upload_item(upld_item, fdir=fdir)
    f.path.write_bytes(upld_item["content"])
    return f


def add_files_ipywidgets8(upld_value, fdir=pathlib.Path(".")):
    di = {}
    for l in upld_value:
        f = add_file(l, fdir=fdir)
        di[l["name"]] = f
    return [v.path for v in di.values()]


def add_files(upld_value, fdir=pathlib.Path(".")):
    if not pathlib.Path(fdir).exists():
        pathlib.Path(fdir).mkdir(exist_ok=True)
    return add_files_ipywidgets8(upld_value, fdir=fdir)


class FilesUploadToDir(Array):
    def __init__(
        self,
        value=None,
        fdir=pathlib.Path("."),
        kwargs_display_path: ty.Optional[dict] = None,
        **kwargs
    ):
        super().__init__(
            add_remove_controls="remove_only",
            show_hash=None,
        )
        coerce_none = lambda v: {} if v is None else v
        self.kwargs_display_path = coerce_none(kwargs_display_path)
        self.rows_box.layout = {"border": "solid LightCyan 2px"}
        self.fdir = fdir
        self.upld = w.FileUpload(**kwargs)
        self.children = [self.upld] + list(self.children)
        if value is not None:
            self.add_files(value)
        self._init_controls_FilesUploadToDir()
        self.fn_remove = self.fn_remove_file

    def _init_controls_FilesUploadToDir(self):
        self.upld.observe(self._upld, "value")

    def _upld(self, on_change):
        paths = add_files(self.upld.value, fdir=self.fdir)
        self.add_files(paths)
        self.upld.value = ()

    def add_files(self, paths: list[str]):
        for p in paths:
            self.add_row(item=DisplayPath(str(p), **self.kwargs_display_path))

    def fn_remove_file(self, key=None):
        p = pathlib.Path(self.map_key_value[key])
        p.unlink(missing_ok=True)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.items = []
        self.add_files(value)


class AutoUploadPaths(FilesUploadToDir):
    def __init__(
        self,
        schema=None,
        value=None,
        fdir=pathlib.Path("."),
        kwargs_display_path: ty.Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(
            value=value, fdir=fdir, kwargs_display_path=kwargs_display_path, **kwargs
        )

if __name__ == "__main__":
    upld = FilesUploadToDir(
        ["/mnt/c/engDev/git_mf/test.PNG"], fdir=pathlib.Path("/mnt/c/engDev/git_mf")
    )
    display(upld)

if __name__ == "__main__":
    upld.value = ["EquipmentReferences-MaxFordhamStandard.pdf", "GenesisCroixDeFer.jpg"]

if __name__ == "__main__":
    from pydantic import BaseModel, Field
    from ipyautoui.custom.fileupload import AutoUploadPaths
    from ipyautoui import AutoUi

    class Test(BaseModel):
        string: str
        paths: list[pathlib.Path] = Field(
            autoui="__main__.AutoUploadPaths",
            title="A longish title about something",
            description="with a rambling description as well...",
        )

    value = {"string": "string", "paths": ["bdns.csv"]}
    aui = AutoUi(Test, value=value, nested_widgets=[AutoUploadPaths])
    display(aui)


# +
class AutoUploadPathsValueString(w.VBox):
    _value = tr.Unicode()

    def __init__(
        self,
        schema=None,
        value=None,
        fdir=pathlib.Path("."),
        kwargs_display_path: ty.Optional[dict] = None,
        **kwargs,
    ):
        super().__init__()
        self.upld = AutoUploadPaths(
            schema=None,
            value=None,
            fdir=fdir,
            kwargs_display_path=kwargs_display_path,
            **kwargs,
        )
        self.children = [self.upld]
        self._init_controls()
        self.value = value

    def _init_controls(self):
        self.upld.observe(self._update_value, "_value")

    def _update_value(self, on_change):
        self._value = json.dumps(self.upld.value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is not None:
            self.upld.value = json.loads(value)


if __name__ == "__main__":
    from pydantic import BaseModel, Field
    from ipyautoui.custom.fileupload import AutoUploadPaths
    from ipyautoui import AutoUi

    class Test(BaseModel):
        paths: list[pathlib.Path] = Field(autoui="__main__.AutoUploadPathsValueString")

    aui = AutoUi(Test)
    display(aui)
# -

if __name__ == "__main__":
    upld = AutoUploadPathsValueString(
        fdir=pathlib.Path("/mnt/c/engDev/git_mf"),
    )
    display(upld)

if __name__ == "__main__":
    upld.value = (
        '["EquipmentReferences-MaxFordhamStandard.pdf", "GenesisCroixDeFer.jpg"]'
    )

if __name__ == "__main__":
    aui = AutoUploadPathsValueString(
        value='["EquipmentReferences-MaxFordhamStandard.pdf", "GenesisCroixDeFer.jpg"]'
    )
    display(aui)


