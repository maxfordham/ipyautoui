#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ipyautoui` package."""
from pprint import pprint
import shutil
import pathlib
import pytest

# from src.ipyautoui.test_schema import TestSchema

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES

from ipyautoui import AutoUi, AutoDisplay, AutoVjsf
from ipyautoui.autoipywidget import (
    AutoObject,
    demo_autoobject_form,
    AutoObjectFormLayout,
)
from ipyautoui.demo_schemas import RootEnum, RootArrayEnum
from ipyautoui.test_schema import TestAutoLogicSimple
import stringcase
import ipywidgets as w

from pydantic import BaseModel, Field

DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)
shutil.rmtree(
    DIR_TEST_DATA
)  #  remove previous data. this allows tests to check if files exist.


class TestAutoObjectFormLayout:
    def __init__(self):
        self.form = demo_autoobject_form()

    def test_show_raw(self):
        # check that that showraw gets added and removed on trait change
        assert len(self.form.hbx_title.children) == 1
        self.form.show_raw = True
        assert len(self.form.hbx_title.children) == 2

    def test_show_title(self):
        # check that that title gets display and hidden on trait change
        assert self.form.title.layout.display == ""
        self.form.show_title = True
        assert self.form.title.layout.display == "None"

    def test_show_description(self):
        # check that that description gets display and hidden on trait change
        assert self.form.description.layout.display == ""
        self.form.show_description = True
        assert self.form.description.layout.display == "None"

    def test_show_savebuttonbar(self):
        # check that that description gets display and hidden on trait change
        assert self.form.savebuttonbar.layout.display == ""
        self.form.show_savebuttonbar = True
        assert self.form.savebuttonbar.layout.display == "None"


class TestAutoObject:
    def test_root(self):
        class ExampleRoot(BaseModel):
            __root__: str = Field(default="Test", description="This test is important")

        ui = AutoObject(ExampleRoot)
        assert ui.value == {"__root__": "Test"}
        print("done")

    def test_simple(self):
        class ExampleSchema(BaseModel):
            text: str = Field(default="Test", description="This test is important")

        auto_ui_eg = ExampleSchema()
        ui = AutoObject(auto_ui_eg)
        assert ui.value == {"text": "Test"}
        print("done")

    def test_dict_raises_error(self):
        class ExampleSchema(BaseModel):
            text: dict = Field(
                default={"test": 1}, description="This test is important"
            )

        with pytest.raises(
            ValueError,
            match="AutoUi does not support rendering generic dictionaries."
            " This can be overridden by specifying a `autoui` pyobject renderer.",
        ):
            auto_ui_eg = ExampleSchema()
            ui = AutoObject(auto_ui_eg)

    def test_TestAutoLogicSimple(self):
        ui = AutoObject(TestAutoLogicSimple)
        getstr = (
            lambda obj: str(type(obj))
            .replace("<class 'ipyautoui.autowidgets.", "")
            .replace("'>", "")
            .lower()
        )
        di_check = {
            stringcase.pascalcase(k).lower(): getstr(v)
            for k, v in ui.di_widgets.items()
        }
        for k, v in di_check.items():
            assert v in k or v == "nullable"

        # assert ui.value == {"text": "Test"}
        print("done")

    def test_RootEnum(self):
        ui = AutoObject(RootEnum)
        print("")
        assert "allOf" not in ui.schema.keys()
        print("done")

    def test_RootArrayEnum(self):
        ui = AutoObject(RootArrayEnum)
        assert "allOf" not in ui.schema["$defs"]["UniclassProductsUi"].keys()
        print("done")


class TestAutoObjectStylingOptions:
    def test_align_horizontal(self):
        ui = AutoObject(TestAutoLogicSimple)
        from ipyautoui.custom.showhide import ShowHide

        get_rowbox = lambda ui: list(
            set([type(row) for row in ui.rows if type(row) != ShowHide])
        )[0]

        # default horizontal
        assert get_rowbox(ui) == w.HBox

        # check vertical
        ui.align_horizontal = False
        assert get_rowbox(ui) == w.VBox

        # check back to horizontal
        ui.align_horizontal = False
        assert get_rowbox(ui) == w.VBox


class TestAutoObjectRowOrder:
    ui = AutoObject(TestAutoLogicSimple)

    def test_order(self):
        self.ui = AutoObject(TestAutoLogicSimple)

        self.ui.order_can_hide_rows = False
        # ui.order =
        order = self.ui.default_order[0:3]
        try:
            self.ui.order = order
        except:
            assert True == True

        self.ui.order_can_hide_rows = True
        assert self.ui.order_can_hide_rows == True
        self.ui.order = order
        assert len(self.ui.autowidget.children) == 3

        self.ui.order_can_hide_rows = False
        assert self.ui.order == self.ui.default_order
        assert len(self.ui.autowidget.children) == len(self.ui.default_order)
