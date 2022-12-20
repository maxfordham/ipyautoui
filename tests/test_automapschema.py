#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ipyautoui` package."""
from pprint import pprint
import shutil
import pathlib

# from src.ipyautoui.test_schema import TestSchema

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from ipyautoui.automapschema import _init_model_schema  # AutoUiSchema,
from ipyautoui.demo_schemas import CoreIpywidgets, RootArrayEnum
import json
import pytest


class TestAutoUiSchema:
    # def test_demo_schema(self):
    #     sch = AutoUiSchema(CoreIpywidgets)
    #     assert type(sch.schema) == dict
    #     print("done")

    # def test_demo_RootArrayEnum(self):
    #     sch = AutoUiSchema(RootArrayEnum)
    #     print("done")

    def test_demo_init_model_schema_RootArrayEnum(self):
        model, schema = _init_model_schema(RootArrayEnum)
        assert "allOf" not in schema["definitions"]["UniclassProductsUi"].keys()
        print("done")

    def test_demo_init_model_schema_check_nullable(self):
        model, schema = _init_model_schema(CoreIpywidgets)
        # assert schema
        assert schema["properties"]["int_slider_nullable"]["nullable"]
        assert "nullable" not in schema["properties"]["int_slider_req"].keys()
        print("done")
