# +
"""file upload wrapper"""
# %load_ext lab_black
# %run _dev_sys_path_append.py
# %run __init__.py
#
# %run ../__init__.py
import ipywidgets as w
from markdown import markdown
from IPython.display import display
from pydantic import BaseModel, validator, Field
import pathlib
import typing as ty
import stringcase
from datetime import datetime
import traitlets as tr
import json

from ipyautoui.constants import DELETE_BUTTON_KWARGS
from ipyautoui._utils import getuser
from ipyautoui.autodisplay import DisplayObject
from ipyautoui.custom.iterable import Dictionary
from ipyautoui.autodisplay_renderers import render_file
from IPython.display import clear_output

IS_IPYWIDGETS8 = (lambda: True if "8" in w.__version__ else False)()

# +
# TODO: allow for adding number of allowed files based on schema
# TODO: patterns for types etc.
# TODO: create base object without description and then extend. OR allow for prepopulated and disabled description
# TODO: add "required files" to the upload that detects name and type
# TODO: add optional description to linked files
# -


class File(BaseModel):
    name: str
    type: str = None
    last_modified: datetime = None
    size: int = None
    fdir: pathlib.Path = pathlib.Path(".")
    path: pathlib.Path = None
    caption: str = None
    added_by: str = None

    class Config:
        alias_generator = stringcase.camelcase
        allow_population_by_field_name = True

    @validator("last_modified", always=True, pre=True)
    def _last_modified(cls, v, values):
        if isinstance(v, int):
            v = datetime.fromtimestamp(v / 1e3)
        return v

    @validator("path", always=True, pre=True)
    def _path(cls, v, values):
        return values["fdir"] / values["name"]


class Files(BaseModel):
    __root__: ty.List[File]


# +
# Files.schema()
# -


class Caption(tr.HasTraits):
    show_caption = tr.Bool(default_value=True)

    def _init_caption(self):
        self.caption = w.Textarea(placeholder="add caption")

    def _init_caption_controls(self):
        self.caption.observe(self._caption, names="value")

    def _caption(self, onchange):
        self.value["caption"] = self.caption.value

    @tr.observe("show_caption")
    def _observe_show_caption(self, proposal):
        if proposal["new"]:
            self.caption.layout.display = ""
        else:
            self.caption.layout.display = "None"


# +
class FileUi(w.HBox, Caption):
    _value = tr.Dict()

    """
    UI for a file link. Can be use with the FileUpload button to load files
    into a location. `self.preview` is a `ipyautoui.autodisplay.DisplayObject`
    and its traits can be accessed.
    
    """

    def __init__(self, value: ty.Union[dict, File]):
        self._init_form()
        if isinstance(value, File):
            value = json.loads(value.json())
        self.value = value
        self._init_caption_controls()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.preview = DisplayObject.from_path(
            self.value["path"], order=("exists", "openpreview", "name")
        )
        if self.value["caption"] is not None:
            self.caption.value = self.value["caption"]
        self.children = [self.preview, self.caption]

    def _init_form(self):
        super().__init__()
        self._init_caption()


if __name__ == "__main__":
    f = File(name="__init__.py")
    fui = FileUi(f)
    display(fui)


# +
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


def add_files_ipywidgets7(upld_value, fdir=pathlib.Path(".")):
    di = {}
    for k, v in upld_value.items():
        f = add_file(v, fdir=fdir)
        di[k] = f
    return di


def add_files_ipywidgets8(upld_value, fdir=pathlib.Path(".")):
    di = {}
    for l in upld_value:
        f = add_file(l, fdir=fdir)
        di[l["name"]] = f
    return di


def add_files(upld_value, fdir=pathlib.Path(".")):
    if not pathlib.Path(fdir).exists():
        pathlib.Path(fdir).mkdir(exist_ok=True)
    if IS_IPYWIDGETS8:
        return add_files_ipywidgets8(upld_value, fdir=fdir)
    else:
        return add_files_ipywidgets7(upld_value, fdir=fdir)


class FilesUploadToDir(w.VBox):
    _value = tr.Dict(default_value={})
    _fdir = tr.Unicode()

    def __init__(
        self,
        schema=None,
        value: ty.Union[ty.Dict[str, File], dict] = None,
        fdir="linked_files",
    ):
        self.fdir = fdir
        self._init_form()
        self._init_controls()
        if value is None:
            value = {}

    def fn_remove(self, key=None):
        path = pathlib.Path(self.fdir) / key
        path.unlink()

    @property
    def fdir(self):
        return self._fdir

    @fdir.setter
    def fdir(self, value):
        self._fdir = value

    @staticmethod
    def convert_to_dict(item):
        if isinstance(item, File):
            return json.loads(value.json())
        else:
            return item

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        value = {k: self.convert_to_dict(v) for k, v in value.items()}
        self.arr_files.items = {}
        self.add_files(value)
        self._arr_files("change")

    def _init_form(self):
        super().__init__(layout={"border": "solid LightCyan 2px"})
        self.vbx_buttons = w.VBox()
        self.upld = w.FileUpload(multiple=True, layout={"width": "300px"})
        self.text = w.HTML()
        self.vbx_buttons.children = [self.upld, self.text]
        self.arr_files = Dictionary(
            add_remove_controls="remove_only", show_hash=None, fn_remove=self.fn_remove
        )
        self.children = [self.vbx_buttons, self.arr_files]
        self._update_text("change")

    def _init_controls(self):
        self.upld.observe(self._upld, names="value")
        self.arr_files.observe(self._arr_files, names="value")
        self.observe(self._update_text, names="_fdir")

    def _update_text(self, onchange):
        self.text.value = markdown(f"_`{self.fdir}`/_")

    def _arr_files(self, onchange):
        self._value = self.arr_files.value

    def add_files(self, files):
        for k, v in files.items():
            ui = FileUi(v)
            self.arr_files.add_row(item=ui, new_key=k)

    def _upld(self, onchange):
        upload_files = add_files(self.upld.value, fdir=self.fdir)
        self.add_files(upload_files)
        self.upld._counter = 0


if __name__ == "__main__":
    upld = FilesUploadToDir()
    display(upld)


# +
# TODO: inherit same base as FilesUploadToDir
class FileUploadToDir(w.VBox, Caption):
    _value = tr.Dict(default_value={})
    _fdir = tr.Unicode()

    def __init__(
        self,
        schema=None,
        value: ty.Union[ty.Dict[str, File], dict] = None,
        fdir="linked_files",
        delete_old=True,
    ):
        self.fdir = fdir
        self.delete_old = delete_old
        self._init_caption()
        self._init_form()
        self._init_controls()
        self._init_caption_controls()
        if value is None:
            value = {}
            self.show_caption = False

    @property
    def fdir(self):
        return self._fdir

    @fdir.setter
    def fdir(self, value):
        self._fdir = value

    @staticmethod
    def convert_to_dict(item):
        if isinstance(item, File):
            return json.loads(item.json())
        else:
            return item

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self.delete_old:
            try:
                p = pathlib.Path(self.upld_path)
                if p.is_file():
                    p.unlink()
            except:
                pass
        self._value = value
        with self.out:
            clear_output()
            if self.upld_path is not None:
                display(render_file(self.upld_path))

    def _init_form(self):
        super().__init__(layout={"border": "solid LightCyan 2px"})
        self.out = w.Output()
        self.hbx_buttons = w.HBox(layout={"width": "300px"})
        self.hbx_bbar = w.HBox(layout={"justify-content": "flex-start"})
        self.upld = w.FileUpload(multiple=False, layout={"width": "256px"})
        self.bn_delete = w.Button(**DELETE_BUTTON_KWARGS)
        self.caption.layout.width = "70%"
        self.caption.layout.height = "30px"

        self.hbx_buttons.children = [self.upld, self.bn_delete]
        self.hbx_bbar.children = [self.hbx_buttons, self.caption]
        self.children = [self.hbx_bbar, self.out]

    def _init_controls(self):
        self.upld.observe(self._upld, names="value")
        self.bn_delete.on_click(self._bn_delete)

    def _bn_delete(self, on_click):
        self.show_caption = False
        self.value = {}
        self.upld._counter = 0

    @property
    def upld_path(self):
        try:
            return list(self.value.values())[0]["path"]
        except:
            pass

    def add_files(self, files):
        self.value = {k: json.loads(v.json()) for k, v in files.items()}
        # self.arr_files.children = [render_file(self.upld_path)]

    def _upld(self, onchange):
        self.show_caption = True
        upload_files = add_files(self.upld.value, fdir=self.fdir)
        self.add_files(upload_files)
        self.upld._counter = 0


if __name__ == "__main__":
    upld = FileUploadToDir()
    display(upld)
# -

if __name__ == "__main__":
    from ipyautoui import AutoUi

    class Ui(BaseModel):
        name: str
        files: ty.Dict[str, File] = Field(
            autoui="__main__.FilesUploadToDir", maximumItems=1, minimumItems=0
        )
        file: ty.Dict[str, File] = Field(autoui="__main__.FileUploadToDir")
        description: str

    aui = AutoUi(schema=Ui, path="test.aui.json")
    display(aui)

# + active=""
# if __name__ == "__main__":
#     aui.value = {
#         "name": "file collection",
#         "description": "about stuff",
#         "files": {
#             "make.bat": {
#                 "name": "make.bat",
#                 "type": "",
#                 "last_modified": "2022-03-23T15:27:13.536000",
#                 "size": 896,
#                 "fdir": ".",
#                 "path": "make.bat",
#                 "caption": None,
#                 "added_by": None,
#             },
#             "Makefile": {
#                 "name": "Makefile",
#                 "type": "",
#                 "last_modified": "2022-03-23T15:27:13.518000",
#                 "size": 654,
#                 "fdir": ".",
#                 "path": "Makefile",
#                 "caption": None,
#                 "added_by": None,
#             },
#         },
#     }
