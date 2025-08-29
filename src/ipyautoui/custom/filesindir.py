# +
import pathlib
from wcmatch.pathlib import Path as wcPath
import ipywidgets as w
import traitlets as tr
from typing import List
import functools
from ipyautoui.basemodel import BaseModel
from pydantic import validator, Field

from ipyautoui.custom import FileChooser
from ipyautoui.custom.iterable import Array
from ipyautoui.constants import (
    BUTTON_WIDTH_MIN,
    TRUE_BUTTON_KWARGS,
    FALSE_BUTTON_KWARGS,
    DASH_BUTTON_KWARGS,
)

# +
PATTERNS_DES = """
list of glob pattern match strings that will be searched within fdir
ref: https://facelessuser.github.io/wcmatch/pathlib/
"""


class FilesInDir(BaseModel):
    """object that uses validation to find fpths in fdir that matches patterns"""

    fdir: pathlib.Path
    recursive: bool = True
    patterns: List[str] = Field([], description=PATTERNS_DES)
    fpths: List[pathlib.Path] = []

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("fdir", always=True)
    def _fdir(cls, v, values):
        """if no key given return uuid.uuid4()"""
        v = wcPath(v)
        if not v.is_dir():
            raise ValueError(f"fdir must be a valid file directory, {str(v)} given")
        return v

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("patterns", always=True, pre=True)
    def _patterns(cls, v, values):
        """if no key given return uuid.uuid4()"""
        if type(v) == str:
            return [v]
        else:
            return v

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("fpths", always=True)
    def _fpths(cls, v, values):
        """if no key given return uuid.uuid4()"""
        if values["recursive"]:
            return list(values["fdir"].rglob(values["patterns"]))
        else:
            return list(values["fdir"].glob(values["patterns"]))


# FilesInDir(fdir='.',patterns='*py')


# +
class ListStrings(w.VBox, tr.HasTraits):
    value = tr.List()

    def __init__(self, value):
        self._init_form()
        self._init_controls()
        self.value = value

    def _init_form(self):
        super().__init__()

    def _init_controls(self):
        self.observe(self._value, "value")

    def _value(self, on_change):
        self.children = [w.HTML(str(v)) for v in self.value]


class MatchStrings(ListStrings):
    def __init__(self, value, match_strings=None, fn_onmatch=lambda x: x):
        self.match_strings = match_strings
        if self.match_strings is None:
            self.match_strings = []
        super().__init__(value)

    def assign_status(self, item):
        if item in self.value and item in self.match_strings:
            b = w.Button(**TRUE_BUTTON_KWARGS)
            b.tooltip = "file found from approved list"
            return b
        elif item in self.value and item not in self.match_strings:
            b = w.Button(**DASH_BUTTON_KWARGS)
            b.tooltip = "additional file found that is not on approved list"
            return b
        elif item not in self.value and item in self.match_strings:
            b = w.Button(**FALSE_BUTTON_KWARGS)
            b.tooltip = "file from approved list not found"
            return b

        else:
            raise ValueError("cant find item")

    def _value(self, on_change):
        li = list(set(self.value + self.match_strings))
        self.children = [w.HBox([self.assign_status(v), w.HTML(str(v))]) for v in li]


# -


class FindFiles(w.VBox, tr.HasTraits):
    value = tr.Dict()

    def __init__(
        self,
        fdir: pathlib.Path,
        title="",
        patterns: List = [],
        fpths=None,
        recursive=False,
        editable_fdir=False,
        editable_patterns=False,
        match_files=None,
    ):
        if match_files is None:
            self.cls_listfiles = ListStrings
        else:
            self.cls_listfiles = functools.partial(
                MatchStrings, match_strings=match_files
            )
        self.title = w.HTML(title)
        self._init_form()
        self.recursive = recursive
        self.pydantic_obj = FilesInDir(
            fdir=fdir, patterns=patterns, recursive=recursive
        )
        self.editable_fdir = editable_fdir
        self.editable_patterns = editable_patterns
        self.patterns_ui.items = [self.fn_add_pattern(i) for i in patterns]
        self._init_controls()

    @property
    def fdir(self):
        return self.pydantic_obj.fdir

    @fdir.setter
    def fdir(self, value):
        pass  # make setter work...

    @property
    def patterns(self):
        return self.pydantic_obj.patterns

    @patterns.setter
    def patterns(self, value):
        pass  # make setter work...

    def fn_add_pattern(self, value=None):
        if self.editable_patterns:
            return w.Text(placeholder="add regex glob pattern", value=value)
        else:
            return w.Text(
                placeholder="add regex glob pattern", value=value, disabled=True
            )

    @property
    def pydantic_obj(self):
        return self._pydantic_obj

    @pydantic_obj.setter
    def pydantic_obj(self, value):
        self._pydantic_obj = value
        self.value = self._pydantic_obj.model_dump()
        self.fpths_ui.value = self.pydantic_obj.fpths

    @property
    def editable_fdir(self):
        return self._editable_fdir

    @editable_fdir.setter
    def editable_fdir(self, value):
        self._editable_fdir = value
        if self.editable_fdir:
            self.fdir_ui = FileChooser()
            self.fdir_ui.show_only_dirs = True
            self.fdir_ui.value = self.pydantic_obj.fdir
        else:
            self.fdir_ui = w.HTML()
            self.fdir_ui.value = str(self.pydantic_obj.fdir)
        # self.pydantic_obj = FilesInDir(fdir=self.fdir, patterns=self.patterns_ui.value, recursive=self.recursive)
        self.box_fdir.children = [self.fdir_ui]
        self.fdir_ui.observe(self._fdir, names=["value", "_value"])

    @property
    def editable_patterns(self):
        return self._editable_patterns

    @editable_patterns.setter
    def editable_patterns(self, value):
        self._editable_patterns = value
        self.patterns_ui.fn_add = self.fn_add_pattern
        if self.editable_patterns:
            self.patterns_ui.add_remove_controls = "append_only"
            for i in self.patterns_ui.items:
                i.disabled = False
        else:
            # self.patterns_ui.fn_add = lambda value=None: w.Text(placeholder='add regex glob pattern', value=None, disabled=True)
            self.patterns_ui.add_remove_controls = None
            for i in self.patterns_ui.items:
                i.disabled = True
        self.patterns_ui.observe(self._patterns, names=["value", "_value"])

    def _patterns(self, on_change):
        if self.pydantic_obj.patterns == [p for p in self.patterns_ui.value if p != ""]:
            pass
        else:
            self.pydantic_obj = FilesInDir(
                fdir=self.fdir,
                patterns=self.patterns_ui.value,
                recursive=self.recursive,
            )

    def _fdir(self, on_change):
        self.pydantic_obj = FilesInDir(
            fdir=self.fdir_ui.value,
            patterns=self.pydantic_obj.patterns,
            recursive=self.recursive,
        )

    def _refresh(self, on_click):
        self.pydantic_obj = FilesInDir(
            fdir=self.fdir, patterns=self.patterns, recursive=self.recursive
        )

    def _init_form(self):
        width = "120px"
        # refresh
        self.box_title = w.HBox()
        self.refresh = w.Button(
            icon="refresh",
            layout={"width": BUTTON_WIDTH_MIN},
            tooltip="update file list (search folder again)",
        )
        self.box_title.children = [self.refresh, self.title]

        # fdir
        self.box_fdir = w.HBox()
        self.box_folder = w.HBox(
            [w.HTML("<b>folder:</b> ", layout={"width": width}), self.box_fdir]
        )

        # patterns
        self.patterns_ui = Array(show_hash=None)
        self.box_patterns = w.HBox(
            [
                w.HTML("<b>search patterns:</b> ", layout={"width": width}),
                self.patterns_ui,
            ]
        )

        # fpths
        self.fpths_ui = self.cls_listfiles(value=[])
        self.box_fpths = w.HBox(
            [w.HTML("<b>filepaths:</b> ", layout={"width": width}), self.fpths_ui]
        )

        # box
        super().__init__()
        self.children = [
            self.box_title,
            self.box_folder,
            self.box_patterns,
            self.box_fpths,
        ]

    def _init_controls(self):
        self.refresh.on_click(self._refresh)


if __name__ == "__main__":
    from IPython.display import display

    fdir = "../"
    patterns = ["*file*"]
    pydantic_obj = FilesInDir(fdir=fdir, patterns=patterns)

    ff = FindFiles(
        fdir=fdir,
        patterns=patterns,
        recursive=True,
        title="<b>find files in folder</b>",
        # match_files=[pathlib.Path("filesindir.py"), "fileupload.py",],
    )  # , editable_fdir=True
    display(ff)

if __name__ == "__main__":
    ff.editable_fdir = True

if __name__ == "__main__":
    ff.editable_patterns = False
