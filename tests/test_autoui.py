#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ipyautoui` package."""
from pprint import pprint
import shutil
import pathlib

# from src.ipyautoui.test_schema import TestSchema

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from .example_objects import ExampleSchema
from ipyautoui import AutoUi, AutoDisplay, AutoVjsf
from ipyautoui.autoipywidget import AutoObject

DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)
shutil.rmtree(
    DIR_TEST_DATA
)  #  remove previous data. this allows tests to check if files exist.


class TestAutoUi:
    def test_auto_ui(self):
        auto_ui_eg = ExampleSchema()
        ui = AutoUi(auto_ui_eg)
        assert ui.value == {"text": "Test"}
        print("done")

    # def test_display_file(self):
    #     fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
    #     d0 = DisplayFile(fpths[0])
