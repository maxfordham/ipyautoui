
"""file upload wrapper"""


# +
import ipywidgets as w
from IPython.display import display
from pydantic import BaseModel, field_validator, Field, ValidationInfo, BeforeValidator
import pathlib
import typing as ty
import traitlets as tr
import logging
import time
import tempfile

from ipyautoui.constants import DELETE_BUTTON_KWARGS
from ipyautoui._utils import getuser, trait_order
from ipyautoui.autodisplay import (
    DisplayPath,
    ORDER_NOTPATH,
)
from ipyautoui.custom.iterable import Array
from ipyautoui.env import Env
from ipyautoui.custom.title_description import TitleDescription
from typing_extensions import Annotated


IPYAUTOUI_ROOTDIR = Env().IPYAUTOUI_ROOTDIR
logger = logging.getLogger(__name__)


# +
try:
    from ipyvuetify.extra import FileInput

    class VuetifyFileUplad(w.Box):
        value = tr.List(trait=tr.Dict())
        # NOTE: haven't implemented a value setter as for this
        #       application it is not required.

        def __init__(self, **kwargs):
            self.upld = FileInput(**kwargs)
            super().__init__([self.upld])
            self._init_controls()

        def _init_controls(self):
            self.upld.observe(self._upld, "file_info")

        def _upld(self, on_change):
            self.value = [
                f | {"content": d["file_obj"].read()}
                for f, d in zip(self.upld.file_info, self.upld.get_files())
            ]

except ImportError as e:
    logger.warning(f"ipyvuetify not installed. {e}")

    class VuetifyFileUplad(w.Box):
        value = tr.Unicode(
            "ipyvuetify not installed. you must install it to use the `ipyvuetify.extra import FileInput`"
        )

        def __init__(self, **kwargs):
            super().__init__()
            self.children = [w.HTML(self.value)]


# +
def make_validator(label: str) -> ty.Callable[[ty.Any, ValidationInfo], bytes]:
    def validator(v: ty.Any, info: ValidationInfo) -> bytes:
        if not isinstance(v, bytes):
            v = v.tobytes()
        return v

    return validator


class File(BaseModel):
    name: str
    size: int
    type: str
    # last_modified: int =Field(serialization_alias ="lastModified") # ignore for now
    content: Annotated[bytes, BeforeValidator(make_validator("make-bytes"))]
    fdir: pathlib.Path = pathlib.Path(".")
    path: pathlib.Path = Field(pathlib.Path("overide.me"), validate_default=True)

    @field_validator("path")
    @classmethod
    def _path(cls, v, info: ValidationInfo):
        values = info.data
        return values["fdir"] / values["name"]


# +
def read_file_upload_item(di: dict, fdir=pathlib.Path("."), added_by=None):
    if added_by is None:
        added_by = getuser()
    return File(**di | dict(fdir=fdir, added_by=added_by))


def add_file(upld_item, fdir=pathlib.Path(".")):
    f = read_file_upload_item(upld_item, fdir=fdir)
    if f.path.is_file():
        raise ValueError(f"{f.path} already exist. exiting operation.")
    # f.path.write_bytes(upld_item["content"])
    f.path.write_bytes(f.content)
    return f


def add_files_to_dir(upld_value, fdir=pathlib.Path("."), message=None):
    di = {}
    for l in upld_value:
        try:
            f = add_file(l, fdir=fdir)
            di[l["name"]] = f
        except Exception as e:
            if message is not None:
                message.value = f"<i>{str(e)}</i>"
                time.sleep(2)
            pass
    return [v.path for v in di.values()]


# +
def add_files(upld_value, fdir=pathlib.Path("."), message=None):
    if not pathlib.Path(fdir).exists():
        pathlib.Path(fdir).mkdir(exist_ok=True)
    return add_files_to_dir(upld_value, fdir=fdir, message=message)


class FileUploadToDir(w.VBox):
    _value = tr.Unicode(default_value=None, allow_none=True)
    fdir = tr.Instance(klass=pathlib.PurePath, default_value=pathlib.Path("."))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if pathlib.Path(value).is_file():
            self.add_file([pathlib.Path(value)])
        else:
            pass

    @property
    def path(self):
        if self.value is None:
            return None
        else:
            return pathlib.Path(self.value)

    def __init__(self, **kwargs):
        self.upld = w.FileUpload()
        self.bn_delete = w.Button(**DELETE_BUTTON_KWARGS)
        self._show_bn_delete("")
        self.fdisplay = DisplayPath(value=None, order=("exists", "openpreview", "name"))
        self._init_controls()
        super().__init__(**kwargs)
        if "value" in kwargs:
            self.value = kwargs["value"]
        self.children = [
            w.HBox([self.bn_delete, self.upld, self.fdisplay]),
            self.fdisplay.bx_out,
        ]
        self.fdisplay.children = [self.fdisplay.bx_bar]

    def _init_controls(self):
        self.upld.observe(self._upld, "value")
        self.observe(self._show_bn_delete, "_value")
        self.bn_delete.on_click(self._bn_delete)

    def _upld(self, on_change):
        paths = add_files(self.upld.value, fdir=self.fdir)
        self.add_file(paths)
        self.upld.value = ()

    def _bn_delete(self, on_click):
        self.path.unlink()
        self._value = None
        self.fdisplay.value = None

    def _show_bn_delete(self, on_change):
        if self.value is None:
            self.bn_delete.layout.display = "None"
        else:
            self.bn_delete.layout.display = ""

    def add_file(self, paths: list[str]):
        if len(paths) > 1:
            raise ValueError("asdf")
        elif len(paths) == 0:
            return
        else:
            if self.path is not None:
                self.path.unlink(missing_ok=True)
            self.fdisplay.value = str(paths[0])
            self._value = str(paths[0])


if __name__ == "__main__":
    fupld = FileUploadToDir(value="IMG_0688.jpg")
    display(fupld)
# +
class TempFileUploadProcessor(FileUploadToDir):
    """A wrapper widget that uploads a file, processes it via callback, and deletes it after use."""
    fn_process = tr.Callable(default_value=None, allow_none=True)
    allowed_file_type = tr.Unicode(default_value="", allow_none=True)

    def __init__(self, **kwargs):
        self.fn_process = kwargs.pop("fn_process", None)
        allowed_file_type = kwargs.pop("allowed_file_type", None)
        super().__init__(**kwargs)
        self.children = [w.HBox([self.bn_delete, self.upld])]
        if allowed_file_type is not None:
            self.allowed_file_type = allowed_file_type
        self._apply_allowed_file_type()

    def _upld(self, on_change):
        """Override upload handler to use temp directory and auto-delete."""
        if not self.upld.value:
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = pathlib.Path(tmpdir)

            paths = add_files(self.upld.value, fdir=tmp_path)

            # Run callback on uploaded file(s)
            if self.fn_process is not None:
                try:
                    for path in paths:
                        self.fn_process(path)
                except Exception as e:
                    logger.exception("Processing failed", exc_info=e)
                    
        self.upld.value = ()

    def _apply_allowed_file_type(self):
        """Sync the trait with the widget accept attribute."""
        if hasattr(self, "upld"):
            self.upld.accept = self.allowed_file_type or ""

    @tr.observe("allowed_file_type")
    def _obs_allowed_file_type(self, change):
        self._apply_allowed_file_type()

if __name__ == "__main__":
    def process_file_callback(path: pathlib.Path):
        print(f"Processing uploaded file: {path}")
    upload_widget = TempFileUploadProcessor(fn_process=process_file_callback)
    display(upload_widget)
# +
MAP_FILEUPLOAD_TYPE = {True: VuetifyFileUplad, False: w.FileUpload}
MAP_CLEARFILEUPLOAD = {
    True: lambda wgdt: wgdt.upld.clear(),
    False: lambda wgdt: setattr(wgdt, "value", ()),
}


class FilesUploadToDir(Array, TitleDescription):
    use_vuetify = tr.Bool(default_value=None, allow_none=False)
    fdir = tr.Instance(klass=pathlib.PurePath, default_value=pathlib.Path("."))
    kwargs_display_path = tr.Dict(default_value={}, allow_none=False)
    kwargs_file_upload = tr.Dict(default_value={}, allow_none=False)

    @tr.observe("use_vuetify")
    def _obs_use_vuetify(self, value):
        if value["new"] != value["old"]:
            self._init_upld()

    @tr.default("kwargs_file_upload")
    def _kwargs_file_upload(self):
        return dict(multiple=True)

    @tr.observe("kwargs_file_upload")
    def _obs_kwargs_file_upload(self, value):
        value = value["new"] | dict(multiple=True)
        if self.use_vuetify:
            widg = self.upld.upld
        else:
            widg = self.upld
        {setattr(widg, k, v) for k, v in value.items()}


    def get_ordered_kwargs(self, kwargs):
        in_order = list(kwargs.keys())
        tr_order = trait_order(self)
        out_order = tr_order + [i for i in in_order if i not in tr_order]
        return {o: kwargs[o] for o in out_order if o in in_order}

    def __init__(self, **kwargs):
        self.hbx_upload = w.HBox()
        self.message = w.HTML()
        super().__init__()
        kwargs = self.get_ordered_kwargs(kwargs)
        {setattr(self, k, v) for k, v in kwargs.items()}

    def _init_upld(self):
        self.upld = MAP_FILEUPLOAD_TYPE[self.use_vuetify]()
        self.hbx_upload.children = [self.upld, self.message]
        self._init_controls_FilesUploadToDir()

    def _init_controls_FilesUploadToDir(self):
        self.upld.observe(self._upld, "value")

    def _post_init(self, **kwargs):
        self.fn_remove = self.fn_remove_file
        self.add_remove_controls = "remove_only"
        self.show_hash = None
        value = kwargs.get("value")
        if value is not None:
            self.add_files(value)
        kwargs_display_path = kwargs.get("kwargs_display_path")
        self.kwargs_display_path = (lambda v: {} if v is None else v)(
            kwargs_display_path
        )

        self.children = [
            self.html_title,
            self.hbx_upload,
            self.bx_boxes,
        ]

    def _upld(self, on_change):
        paths = add_files(self.upld.value, fdir=self.fdir, message=self.message)
        self.add_files(paths)
        self.message.value = ""
        MAP_CLEARFILEUPLOAD[self.use_vuetify](self.upld)

    def add_files(self, paths: list[str]):
        for p in paths:
            self.add_row(
                widget=DisplayPath(
                    str(p), **self.kwargs_display_path | dict(order=ORDER_NOTPATH)
                )
            )

    def fn_remove_file(self, bx=None):
        p = pathlib.Path(bx.widget.value)
        p.unlink(missing_ok=True)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.boxes = []
        self.add_files(value)


# -

if __name__ == "__main__":
    p = pathlib.Path()
    p_ = list(IPYAUTOUI_ROOTDIR.parents)[2] / "docs" / "images" / "logo.png"
    upld = FilesUploadToDir(
        value=[str(p_)],
        kwargs_file_upload=dict(accept=".asc, .png, .jpg", multiple=True),
        use_vuetify=True,
    )
    display(upld)
    # test

if __name__ == "__main__":
    upld.value = ["__init__.py", "../automapschema.yaml"]

if __name__ == "__main__":
    from pydantic import BaseModel, Field
    from ipyautoui.custom.fileupload import AutoUploadPaths
    from ipyautoui import AutoUi

    class Test(BaseModel):
        string: str
        paths: list[pathlib.Path] = Field(
            title="A longish title about something",
            description="with a rambling description as well...",
            json_schema_extra=dict(autoui="__main__.FilesUploadToDir"),
        )

    value = {"string": "string", "paths": ["__init__.py"]}
    aui = AutoUi(Test, value=value, nested_widgets=[AutoUploadPaths])
    display(aui)
