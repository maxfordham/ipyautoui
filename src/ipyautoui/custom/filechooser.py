"""wrapper for ipyfilechooster.FileChooser"""


import pathlib
import traitlets as tr
import typing as ty
from ipyfilechooser import FileChooser
import ipywidgets as w
import os
import logging

logger = logging.getLogger(__name__)


def make_path(path):
    if type(path) == str:
        return pathlib.PurePath(path)
    else:
        return path


class FileChooser(FileChooser):
    """inherits ipyfilechooster.FileChooser but initialises
    with a value= kwarg and adds a fc.value property. this
    follows the same convention as ipywidgets and therefore integrates
    better wiht ipyautoui

    Reference:
        https://github.com/crahan/ipyfilechooser
    """

    _value = tr.Unicode()

    @tr.default("_value")
    def _default_value(self):
        return str(pathlib.Path("."))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: ty.Union[str, pathlib.Path]):
        """having the setter allows users to pass a new value field to the class which also updates the
        `selected` argument used by FileChooser"""
        value = str(value)
        p = pathlib.Path(value)
        if p.is_dir():
            self.reset(value, "")
        elif p.is_file():
            self.reset(p.parent, p.name)
        elif p.parent.is_dir():
            self.reset(p.parent, p.name)
        else:
            raise ValueError(f"{str(p)} not a valid path or dir")
        self._apply_selection()
        self._value = value

    def __init__(
        self,
        value=None,
        path: str = os.getcwd(),
        filename: str = "",
        title: str = "",
        select_desc: str = "Select",
        change_desc: str = "Change",
        show_hidden: bool = False,
        select_default: bool = False,
        dir_icon: ty.Optional[str] = "\U0001F4C1 ",
        dir_icon_append: bool = False,
        show_only_dirs: bool = False,
        filter_pattern: ty.Optional[ty.Sequence[str]] = None,
        sandbox_path: ty.Optional[str] = None,
        layout: w.Layout = w.Layout(width="500px"),
        **kwargs,
    ):
        kwargs = kwargs | {
            "path": path,
            "filename": filename,
            # title
            "select_desc": select_desc,
            "change_desc": change_desc,
            "show_hidden": show_hidden,
            "select_default": select_default,
            "dir_icon": dir_icon,
            "dir_icon_append": dir_icon_append,
            "show_only_dirs": show_only_dirs,
            "filter_pattern": filter_pattern,
            "sandbox_path": sandbox_path,
            "layout": layout,
        }

        if value is None:
            super().__init__(**kwargs)
        else:
            value = pathlib.Path(value)
            if value.is_file():
                kwargs["path"] = str(value.parent)
                kwargs["filename"] = value.name
                super().__init__(**kwargs)
                self._apply_selection()
            elif value.is_dir():
                kwargs["path"] = str(value.parent)
                super().__init__(**kwargs)
            else:
                logger.warning("path given doesnt exist")
                super().__init__(**kwargs)
        self._set_value("click")
        self._init_controls()

    def _init_controls(self):
        self._select.on_click(self._set_value)

    def _set_value(self, onchange):
        if self.selected is not None:
            self._value = self.selected


if __name__ == "__main__":
    from ipyautoui.constants import load_test_constants
    from IPython.display import display

    test_constants = load_test_constants()
    fc = FileChooser(test_constants.PATH_TEST_AUI.parent)
    display(fc)

if __name__ == "__main__":
    fc.value = test_constants.PATH_TEST_AUI

if __name__ == "__main__":
    from pydantic import BaseModel, Field
    from ipyautoui import AutoUi

    class Test(BaseModel):
        path: pathlib.Path = Field(
            ".", json_schema_extra=dict(filter_pattern=["*_.py"])
        )  # note. filter_pattern ipyfilechooser kwarg passed on
        string: str = "test"

    ui = AutoUi(Test)
    display(ui)

if __name__ == "__main__":
    display(ui.value)
    display(ui.di_widgets["path"].filter_pattern)
