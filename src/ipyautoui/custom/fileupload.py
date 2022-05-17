"""file upload wrapper"""
# %load_ext lab_black
import ipywidgets as widgets
from ipyautoui.constants import BUTTON_MIN_SIZE
from ipyautoui._utils import open_file

class FileUpload(widgets.FileUpload):
    """file upload wrapper"""

    def __init__(self, value: None = None, path=None, **kwargs):
        super().__init__(**kwargs)


f = FileUpload()

# +
from ipyautoui.autodisplay import AutoDisplay, DisplayObject

# #  ?DisplayObject.from_path

# +

BUTTON_MIN_SIZE
# -





# +
from pydantic import BaseModel, validator, Field
import pathlib
import typing
from ipyautoui.automapschema import attach_schema_refs
from ipyautoui.custom.iterable import Array, AutoArray, Dictionary
import stringcase
from datetime import datetime


class UploadedFile(BaseModel):
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


def read_file_upload_item(di: dict, fdir=pathlib.Path(".")):
    _ = di["metadata"]
    _["fdir"] = fdir
    f = UploadedFile(**_)
    return f


def add_files(upld_value, fdir=pathlib.Path(".")):
    di = {}
    for k, v in upld_value.items():
        f = read_file_upload_item(v, fdir=fdir)
        f.path.write_bytes(v["content"])
        di[k] = f
    return di


class Files(BaseModel):
    fdir: pathlib.Path = pathlib.Path(".")
    files: typing.Dict[str, UploadedFile] = Field(default_factory=lambda: {})


# -

Files()

# +
from ipyautoui._utils import obj_to_importstr

obj_to_importstr(FileUploadToDir)
# -



d = Dictionary(add_remove_controls="remove_only", show_hash=None)
d.add_row

upld = widgets.FileUpload(multiple=True)
upld

value = upld.value

# # ?AutoArray
sch = attach_schema_refs(Files.schema())
# sch["properties"]["files"]

Files.schema()["properties"]

Files()

f = read_file_upload_item(upld.value["README.txt"])

# +
import traitlets
import json
import traitlets_paths


class UploadedFileUi(widgets.HBox):
    _value = traitlets.Dict()

    # @traitlets.validate("_value")
    # def _valid_value(self, proposal):
    #     return json.loads(UploadedFile(**proposal["value"]).json())

    def __init__(self, value: typing.Union[dict, UploadedFile]):
        self._init_form()
        if isinstance(value, UploadedFile):
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
class FileUploadToDir(widgets.VBox):
    _value = traitlets.Dict(default_value=[])

    def __init__(self, schema=None, value=None):

        self._init_form()
        self._init_controls()
        if value is None:
            value = Files()

    def fn_remove(self, key=None):

        path = pathlib.Path(self.fdir) / key
        path.unlink()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, Files):
            value = json.loads(value.json())
        if value == {}:
            value = json.loads(Files().json())
        self.arr_files.items = {}
        self.fdir = value["fdir"]
        self.add_files(value["files"])
        self._arr_files("change")
        # self._value = value
        # print(self.value)

    def _init_form(self):
        super().__init__()
        self.upld = widgets.FileUpload(multiple=True)
        self.arr_files = Dictionary(
            add_remove_controls="remove_only", show_hash=None, fn_remove=self.fn_remove
        )
        self.children = [self.upld, self.arr_files]

    def _init_controls(self):
        self.upld.observe(self._upld, names="value")
        self.arr_files.observe(self._arr_files, names="value")

    def _arr_files(self, onchange):
        self._value = json.loads(
            Files(fdir=self.fdir, files=self.arr_files.value).json()
        )
        print(self.value)

    def add_files(self, files):
        for k, v in files.items():
            ui = UploadedFileUi(v)
            self.arr_files.add_row(item=ui, new_key=k)

    def _upld(self, onchange):
        upload_files = add_files(self.upld.value, fdir=self.fdir)
        self.add_files(upload_files)
        self.upld._counter = 0


upld = FileUploadToDir()
# -

upld

json.loads(Files(fdir=".", files={}).json())

from ipyautoui import AutoUi


# +
class Ui(BaseModel):
    name: str
    description: str
    files: Files = Field(autoui="__main__.FileUploadToDir")


aui = AutoUi(schema=Ui)
aui
# -

upld.value = {
    "fdir": ".",
    "files": {
        "make.bat": {
            "name": "make.bat",
            "type": "",
            "last_modified": "2022-03-23T15:27:13.536000",
            "size": 896,
            "fdir": ".",
            "path": "make.bat",
            "caption": None,
            "added_by": None,
        },
        "Makefile": {
            "name": "Makefile",
            "type": "",
            "last_modified": "2022-03-23T15:27:13.518000",
            "size": 654,
            "fdir": ".",
            "path": "Makefile",
            "caption": None,
            "added_by": None,
        },
    },
}

# +
import getpass

user = getpass.getuser()
user
# -

upld.value

upld.fn_remove(key="README.txt")

upld.value

os.environ



# +

pathlib.Path(upld.value[key]["path"]).unlink()

# +
key = "Makefile"

path = pathlib.Path(upld.value[key]["path"])
path
# -

up.value

f = widgets.HBox(
    [
        DisplayObject.from_path("edit_grid.py"),
        widgets.Textarea(placeholder="add caption"),
        widgets.Button(
            button_style="danger", icon="trash", layout=dict(BUTTON_MIN_SIZE)
        ),
    ]
)
widgets.VBox([f, f, f])

sch["properties"]["files"]

add_files(upld.value)

# +

f = open(pathlib.Path("sample.txt"), "wb")
f. write(by)
f. close()
# -

pathlib.Path("sample.txt").write_bytes(by)

by = upld.value['README.txt']['content']

di = upld.value['README.txt']['metadata']

# +


stringcase.camelcase('last_modified')

# +

    
di['fdir'] = pathlib.Path('')
FileMetadata(**di)
# -



# ?datetime.fromtimestamp

def 

# +

        
        
