#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ipyautoui` package."""
from pprint import pprint
import shutil
import pytest

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS
from .example_objects import AutoUiExample, fn_add
from ipyautoui import AutoUi
from ipyautoui.custom.iterable import IterableItem, Array, Dictionary

DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True) 
shutil.rmtree(DIR_TEST_DATA) #  remove previous data. this allows tests to check if files exist.

# Pytest fixture code
# @pytest.fixture(scope="class")
# def test():
#     pass
    
# @pytest.mark.usefixtures("test")

class TestUi:
    def test_auto_ui(self):
        auto_ui_eg = AutoUiExample()
        ui = AutoUi(auto_ui_eg)

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

