# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

"""wrapper for ipyfilechooster.FileChooser"""
# %run _dev_sys_path_append.py
# %run __init__.py
#
# %load_ext lab_black

import pathlib
import traitlets as tr
from traitlets_paths import PurePath  # TODO: create conda recipe for this package
from ipyfilechooser import FileChooser


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

    # _value = PurePath()
    _value = tr.Unicode()

    @tr.default("_value")
    def _default_value(self):
        return str(pathlib.Path("."))

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: PurePath):
        """having the setter allows users to pass a new value field to the class which also updates the
        `selected` argument used by FileChooser"""
        self._value = str(value)
        p = pathlib.Path(self.value)
        if p.is_dir():
            self.reset(self.value, None)
        elif p.is_file():
            self.reset(p.parent, p.name)
        elif p.parent.is_dir():
            self.reset(p.parent, None)
        else:
            raise ValueError(f"{str(p)} not a valid path or dir")
        self._apply_selection()

    def __init__(self, value: pathlib.Path = None, **kwargs):
        try:
            kwargs.pop("title")
        except:
            pass
        if value is None:
            super().__init__(**kwargs)
        else:
            value = pathlib.Path(value)
            if value.is_file():
                if "filename" in kwargs:
                    del kwargs["filename"]
                super().__init__(str(value.parent), filename=value.name, **kwargs)
                self._apply_selection()
            elif value.is_dir():
                super().__init__(str(value), **kwargs)
            else:
                print("path given doesnt exist")
                super().__init__(str(value), **kwargs)
        self._set_value("click")
        self._init_controls()

    def _init_controls(self):
        self._select.on_click(self._set_value)

    def _set_value(self, onchange):
        if self.selected is not None:
            self._value = self.selected


if __name__ == "__main__":
    from ipyautoui.constants import load_test_constants

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
            ".", filter_pattern=["*.py"]
        )  # note. filter_pattern ipyfilechooser kwarg passed on
        string: str = "test"

    ui = AutoUi(Test)
    display(ui)

if __name__ == "__main__":
    display(ui.value)
