#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ipyautoui` package."""
from pprint import pprint
import shutil
import pathlib

# from src.ipyautoui.test_schema import TestSchema

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from .example_objects import ExampleRoot, ExampleSchema
from ipyautoui import AutoUi, AutoDisplay, AutoVjsf
from ipyautoui.autoipywidget import AutoObject, demo_autoobject_form

DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)
shutil.rmtree(
    DIR_TEST_DATA
)  #  remove previous data. this allows tests to check if files exist.

form = demo_autoobject_form()


class AutoObjectFormLayout:
    def test_show_raw(self):
        # check that that showraw gets added and removed on trait change
        assert len(form.hbx_title.children) == 1
        form.show_raw = True
        assert len(form.hbx_title.children) == 2

    def test_show_title(self):
        # check that that title gets display and hidden on trait change
        assert form.title.layout.display == ""
        form.show_title = True
        assert form.title.layout.display == "None"

    def test_show_description(self):
        # check that that description gets display and hidden on trait change
        assert form.description.layout.display == ""
        form.show_description = True
        assert form.description.layout.display == "None"


class TestAutoObject:
    def test_root(self):
        # auto_ui_eg = ExampleRoot()
        ui = AutoObject(ExampleRoot)
        assert ui.value == {"__root__": "Test"}
        print("done")

    def test_simple(self):
        auto_ui_eg = ExampleSchema()
        ui = AutoObject(auto_ui_eg)
        assert ui.value == {"text": "Test"}
        print("done")
