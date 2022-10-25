# +
"""file upload wrapper"""
# %load_ext lab_black
import ipywidgets as widgets
from markdown import markdown
from IPython.display import display
from pydantic import BaseModel, validator, Field
import pathlib
import typing as ty
import stringcase
from datetime import datetime
import traitlets as tr
import json
import traitlets_paths

from ipyautoui.automapschema import attach_schema_refs
from ipyautoui.constants import BUTTON_MIN_SIZE, KWARGS_OPENFOLDER
from ipyautoui._utils import open_file, obj_to_importstr, getuser
from ipyautoui.autodisplay import AutoDisplay, DisplayObject
from ipyautoui.custom.iterable import Array, AutoArray, Dictionary

IS_IPYWIDGETS8 = (lambda: True if "8" in widgets.__version__ else False)()

# +
# TODO: allow for adding number of allowed files based on schema
# TODO: patterns for types etc.
# TODO: create base object without description and then extend. OR allow for prepopulated and disabled description
# TODO: add "required files" to the upload that detects name and type
# TODO: add optional description to linked files
# -


class File(BaseModel):
    name: str
    type: str
    last_modified: datetime
    size: int
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


class FileUi(widgets.HBox):
    _value = tr.Dict()

    # @tr.validate("_value")
    # def _valid_value(self, proposal):
    #     return json.loads(File(**proposal["value"]).json())

    def __init__(self, value: typing.Union[dict, File]):
        self._init_form()
        if isinstance(value, File):
            value = json.loads(value.json())
        self.value = value
        self._init_controls()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.preview = DisplayObject.from_path(self.value["path"])
        if self.value["caption"] is not None:
            self.caption.value = self.value["caption"]
        self.children = [self.preview, self.caption]

    def _init_form(self):
        super().__init__()
        self.caption = widgets.Textarea(placeholder="add caption")

    def _init_controls(self):
        self.caption.observe(self._caption, names="value")

    def _caption(self, onchange):
        self.value["caption"] = self.caption.value


# +
def read_file_upload_item(di: dict, fdir=pathlib.Path("."), added_by=None):
    if added_by is None:
        added_by = getuser()
    map_version = {True: di, False: di["metadata"]}
    _ = map_version[IS_IPYWIDGETS8]
    _["fdir"] = fdir
    _["added_by"] = added_by
    return File(**_)


def add_files_ipywidgets7(upld_value, fdir=pathlib.Path(".")):
    di = {}
    for k, v in upld_value.items():
        f = read_file_upload_item(v, fdir=fdir)
        f.path.write_bytes(v["content"])
        di[k] = f
    return di


def add_files_ipywidgets8(upld_value, fdir=pathlib.Path(".")):
    di = {}
    for l in upld_value:
        f = read_file_upload_item(l, fdir=fdir)
        f.path.write_bytes(l.content.tobytes())
        di[k] = f
    return di


def add_files(upld_value, fdir=pathlib.Path(".")):
    if not pathlib.Path(fdir).exists():
        pathlib.Path(fdir).mkdir(exist_ok=True)
    if IS_IPYWIDGETS8:
        return add_files_ipywidgets8(upld_value, fdir=fdir)
    else:
        return add_files_ipywidgets7(upld_value, fdir=fdir)


class FileUploadToDir(widgets.VBox):
    _value = tr.Dict(default_value={})
    _fdir = tr.Unicode()

    def __init__(
        self,
        schema=None,
        value: typing.Union[typing.Dict[str, File], dict] = None,
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
        self.vbx_buttons = widgets.VBox()
        self.upld = widgets.FileUpload(multiple=True, layout={"width": "300px"})
        self.text = widgets.HTML()
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
    upld = FileUploadToDir()
    display(upld)
# -

if __name__ == "__main__":
    from ipyautoui import AutoUi

    class Ui(BaseModel):
        name: str
        files: typing.Dict[str, File] = Field(
            autoui="__main__.FileUploadToDir", maximumItems=1, minimumItems=0
        )
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
# -
