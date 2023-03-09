"""file upload wrapper"""
%load_ext lab_black
%run _dev_sys_path_append.py
%run __init__.py
%run ../__init__.py

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
from ipyautoui.custom.iterable import Dictionary, Array
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
    def __init__(self, value=None, fdir=pathlib.Path("."), **kwargs):
        super().__init__(
            add_remove_controls="remove_only",
            show_hash=None,
        )
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
            self.add_row(item=DisplayPath(str(p)))

    def fn_remove_file(self, key=None):
        p = pathlib.Path(self.map_key_value[key])
        p.unlink(missing_ok=True)

if __name__ == "__main__":
    upld = FilesUploadToDir(
        ["/mnt/c/engDev/git_mf/test.PNG"], fdir=pathlib.Path("/mnt/c/engDev/git_mf")
    )
    display(upld)