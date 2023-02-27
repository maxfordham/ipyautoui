#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ipyautoui` package."""
from pprint import pprint
import shutil
import pathlib

# from src.ipyautoui.test_schema import TestSchema

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from ipyautoui import AutoUi
from ipyautoui.demo_schemas import CoreIpywidgets
from ipyautoui.basemodel import file
import json
import pytest

DIR_TEST_DATA = DIR_TESTS / "testdata"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)

value_default = json.loads(CoreIpywidgets(int_slider_req=1).json())
PATH_TEST_AUTO_READ_FILE = DIR_TEST_DATA / "test_auto_read_file.json"
PATH_TEST_AUTO_READ_FILE.unlink(missing_ok=True)
changed = CoreIpywidgets(text="changed", int_slider_req=1)
value_changed = json.loads(changed.json())
file(changed, PATH_TEST_AUTO_READ_FILE)


class TestAutoUi:
    @pytest.mark.skip(
        reason="this fails, as widgets auto sets the value...? TODO: resovle."
    )
    def test_auto_ui(self):
        ui = AutoUi(CoreIpywidgets)
        assert ui.value == value_default
        print("done")

    def test_auto_read_file(self):
        ui = AutoUi(CoreIpywidgets, path=PATH_TEST_AUTO_READ_FILE)
        assert ui.value["text"] == value_changed["text"]
        print("done")


    def test_pass_kwargs(self):
        ui = AutoUi(CoreIpywidgets, path=PATH_TEST_AUTO_READ_FILE, show_savebuttonbar=False)
        assert ui.savebuttonbar.layout.display == "None"
        print("done")

    # def test_display_file(self):
    #     fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
    #     d0 = DisplayFile(fpths[0])
