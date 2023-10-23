#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `ipyautoui` package."""
from pprint import pprint
import shutil
import pathlib


# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from ipyautoui import AutoUi
from ipyautoui.demo_schemas import CoreIpywidgets
from ipyautoui.basemodel import file
import pytest
from pydantic import field_validator, BaseModel
from enum import Enum


DIR_TEST_DATA = DIR_TESTS / "testdata"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True)
value_default = CoreIpywidgets(
    int_slider_req=1, int_text_req=1, int_text_nullable=None
).model_dump(mode="json")

PATH_TEST_AUTO_READ_FILE = DIR_TEST_DATA / "test_auto_read_file.json"
PATH_TEST_AUTO_READ_FILE.unlink(missing_ok=True)
changed = CoreIpywidgets(
    test="changed", int_slider_req=1, int_text_req=1, int_text_nullable=None
)
value_changed = changed.model_dump(mode="json")
file(changed, PATH_TEST_AUTO_READ_FILE)



    


class TestAutoUi:
    @pytest.mark.skip(
        reason="this fails, as widgets auto sets the value...? TODO: resovle."
    )
    def test_auto_ui(self):
        ui = AutoUi(CoreIpywidgets)
        assert ui.value == value_default
        print("done")

    # def test_auto_read_file(self):
    #     ui = AutoUi(CoreIpywidgets, path=PATH_TEST_AUTO_READ_FILE)
    #     assert ui.value["text"] == value_changed["text"]
    #     print("done")

    def test_pass_kwargs(self):
        ui = AutoUi(
            CoreIpywidgets,
            path=PATH_TEST_AUTO_READ_FILE,
            json_schema_extra=dict(show_savebuttonbar=False),
        )
        assert ui.savebuttonbar.layout.display == "None"
        print("done")
        
    def test_pydantic_validation(self):
        
        class Test(BaseModel):
            a: str
            b: str

            @field_validator("a")
            @classmethod
            def name_must(cls, v: str) -> str:
                return "asdf"
            
        ui = AutoUi(Test)
        ui.autowidget.di_widgets["a"].value = "my val"
        assert ui.value == {"a": "asdf", "b":""}
        ui.autowidget.di_widgets["b"].value = "my val"
        assert ui.value == {"a": "asdf", "b":"my val"}
        
    def test_pydantic_validation_list(self):
        
        class TestList(BaseModel):
            a: list[str]
            b: str

            @field_validator("a")
            @classmethod
            def add_val(cls, v: str) -> str:
                if "asdf" not in v:
                    v = ["asdf"] + v
                return v
        ui = AutoUi(TestList)
        ui.autowidget.di_widgets["a"].value = []
        v = ui.value
        assert v == {"a": ["asdf"], "b":""}
        ui.autowidget.di_widgets["a"].li_widgets[0].value = "a"
        v = ui.value
        assert v == {"a": ["asdf","a"], "b":""}
        ui.autowidget.di_widgets["b"].value = "my val"
        v = ui.value
        assert ui.value == {"a": ["asdf","a"], "b":"my val"}
        
        
    def test_pydantic_validation_list_enums(self):
        class RoleEnum(Enum):
            director = "Director in Charge"
            lead_crm = "Client Relationship Management (CRM) Lead"
        
        class Obj(BaseModel):
            c: RoleEnum = RoleEnum.director
            d: int =0
        
        class TestListEnums(BaseModel):
            a: list[Obj]
            b: str

            @field_validator("a")
            @classmethod
            def _document_role(cls, v):
                li = [_.c for _ in v]
                if RoleEnum.director not in li:
                    v = [Obj(**{"a": RoleEnum.director})] + v
                return v
            
        ui = AutoUi(TestListEnums)
        
        # ui.autowidget.di_widgets["a"].value = [Obj()]
        # v = ui.value
        # assert v == {"a": [{"c": "Director in Charge", "d":0}], "b":""}
        ui.value = {"a": [{"c": "Client Relationship Management (CRM) Lead", "d":0}], "b":""}
        v = ui.value
        assert v["a"][1]["c"] == "Client Relationship Management (CRM) Lead"
        assert v == {"a": [{"c": "Director in Charge", "d":0}, {"c": "Client Relationship Management (CRM) Lead", "d":0}], "b":""}



    # def test_display_file(self):
    #     fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
    #     d0 = DisplayFile(fpths[0])


