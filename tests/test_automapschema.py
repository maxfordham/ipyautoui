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
from ipyautoui.autoipywidget import AutoObject
from ipyautoui.demo_schemas import (
    CoreIpywidgets,
    RootArrayEnum,
    Nested,
    Filter,
)
from ipyautoui.demo_schemas.ruleset import ScheduleRuleSet
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

    def test_Nested(self):
        model, schema = _init_model_schema(Nested)
        aui = AutoObject(schema=Nested)
        assert list(aui.di_widgets.keys()) == [
            "nested",
            "recursive_nest",
            "array_simple",
            "array_objects",
            "nullable_list",
            "nullable_object",
        ]

        print("done")

    def test_Rule(self):
        model, schema = _init_model_schema(ScheduleRuleSet)
        aui = AutoObject(schema=ScheduleRuleSet)
        assert list(aui.di_widgets.keys()) == ["set_type", "rules"]
        print("done")

    def test_Filter(self):
        aui = AutoObject(schema=Filter)
        print("done")
