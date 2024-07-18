import shutil
import pytest


# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
import ipywidgets as w
import traitlets as tr
import typing as ty
from ipyautoui.custom import (
    Array,
    MultiSelectSearch,
    SaveButtonBar,
    LoadProject,
)
from ipyautoui.custom.modelrun import RunName
from ipyautoui.custom.editgrid import AutoGrid, EditGrid
from ipyautoui.custom.buttonbars import CrudButtonBar


DIR_TEST_DATA = DIR_TESTS / "testdata"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)
shutil.rmtree(DIR_TEST_DATA)
# ^ remove previous data. this allows tests to check if files exist.


class MyItem(w.HBox, tr.HasTraits):
    value = tr.Dict()

    def __init__(self, di: ty.Dict):
        self.value = di
        self._init_form()
        self._init_controls()

    def _init_form(self):
        self._label = w.HTML(f"{list(self.value.keys())[0]}")
        self._bool = w.ToggleButton(list(self.value.values())[0])
        super().__init__(children=[self._bool, self._label])  # self._acc,

    def _init_controls(self):
        self._bool.observe(self._set_value, names="value")

    def _set_value(self, change):
        self.value = {self._label.value: self._bool.value}


def fn_add():
    return MyItem(di={"Example": 1})


class TestCustom:
    def test_iterables_array(self):
        di_arr = {
            "widgets": [fn_add()],
            "fn_add": fn_add,
            "max_items": 10,
            # "show_hash": "index",
            "title": "Array",
            "add_remove_controls": "append_only",
            "align_horizontal": False,
        }
        arr = Array(**di_arr)

    def test_model_run(self):
        run = RunName(value="03-lean-description", index=3)
        run.value = "06-green-thingymabob"

    def test_multiselect_search(self):
        descriptions = "a b c d e f g h".split(" ")
        m = MultiSelectSearch(options=descriptions)

    def test_save_button_bar(self):
        save_button_bar = SaveButtonBar()

    def test_load_project(self):
        load_project = LoadProject()
