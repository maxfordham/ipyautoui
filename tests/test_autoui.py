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
from ipyautoui import AutoUi
from ipyautoui.displayfile import DisplayFile


DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True) 
shutil.rmtree(DIR_TEST_DATA) #  remove previous data. this allows tests to check if files exist.
 

class TestUi:
    def test_auto_ui(self):
        auto_ui_eg = ExampleSchema()
        ui = AutoUi(auto_ui_eg)
        li_keys = [key for key in ui.di_widgets.keys()]
        assert li_keys[0] == 'text'

    def test_display_file(self):
        fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
        d0 = DisplayFile(fpths[0])


    
