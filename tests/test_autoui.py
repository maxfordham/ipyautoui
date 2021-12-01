#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ipyautoui` package."""
import sys
import pathlib
from pprint import pprint
import shutil

sys.path.append(str(pathlib.Path(__file__).parents[1])) # append mfom root
DIR_TEST = pathlib.Path(__file__).parent / "test_data"
DIR_TEST.mkdir(parents=True, exist_ok=True) 
shutil.rmtree(DIR_TEST) #  remove previous data. this allows tests to check if files exist.

from ipyautoui.tests import test_display_widget_mapping

class TestAutoUi:
    def test_widget_mapping(self):
        #di_test_autologic = di_test_autologic
        test_display_widget_mapping(di_test_autologic)
