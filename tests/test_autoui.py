#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ipyautoui` package."""
from pprint import pprint
import shutil
import pytest
import pathlib

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from .example_objects import AutoUiExample, fn_add, get_descriptions
from ipyautoui import AutoUi
from ipyautoui.displayfile import DisplayFile
from ipyautoui.custom import Array, Dictionary, Grid, RunName, MultiSelectSearch, SaveButtonBar, LoadProject


DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True) 
shutil.rmtree(DIR_TEST_DATA) #  remove previous data. this allows tests to check if files exist.

# Pytest fixture code
@pytest.fixture
def load_display_file_types():
    fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
    return fpths
    

class TestUi:
    def test_auto_ui(self):
        auto_ui_eg = AutoUiExample()
        ui = AutoUi(auto_ui_eg)
        li_keys = [key for key in ui.di_widgets.keys()]
        assert li_keys[0] == 'text'

    def test_iterables_array(self):
        di_arr = {
            "items": [fn_add()],
            "fn_add": fn_add,
            "maxlen": 10,
            "show_hash": "index",
            "toggle": True,
            "title": "Array",
            "add_remove_controls": "append_only",
            "orient_rows": False,
        }
        arr = Array(**di_arr)

    def test_iterables_dict(self):
        di_arr = {
            "items": {"key": fn_add()},
            "fn_add": fn_add,
            "maxlen": 10,
            "show_hash": None,
            "toggle": True,
            "title": "Array",
            "add_remove_controls": "append_only",
            "orient_rows": True,
        }
        arr = Dictionary(**di_arr)

    def test_display_file(self):
        fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
        d0 = DisplayFile(fpths[0])

    def test_grid(self):
        gr = Grid()

    def test_model_run(self):
        run = RunName(value='03-lean-description', index=3)
        run.value = '06-green-thingymabob' 

    def test_multiselect_search(self):
        descriptions = get_descriptions()
        m = MultiSelectSearch(options=descriptions)

    def test_save_button_bar(self):
        save_button_bar = SaveButtonBar()

    def test_load_project(self):
        load_project = LoadProject()
