from pydantic import BaseModel, Field, RootModel
from ipyautoui.autoobject import AutoObject
import pytest
import stringcase
from ipyautoui.demo_schemas import RootEnum, RootArrayEnum, CoreIpywidgets
import typing as ty
from enum import Enum

class TestAutoObject:
    def test_root(self):
        with pytest.raises(ValueError) as e:
            ExampleRoot = RootModel[str]
            ui = AutoObject.from_pydantic_model(ExampleRoot)
            assert e == "properties must be in kwargs"

    def test_simple(self):
        class ExampleSchema(BaseModel):
            text: str = Field(default="Test", description="This test is important")

        ui = AutoObject.from_pydantic_model(ExampleSchema)
        assert ui.value == {"text": "Test"}
        print("done")


class TestAutoObjectRowOrder:
    def test_order(self):
        ui = AutoObject.from_pydantic_model(CoreIpywidgets)

        ui.order_can_hide_rows = False
        # ui.order =
        order = ui.default_order[0:3]
        try:
            ui.order = order
        except:
            assert True == True

        ui.order_can_hide_rows = True
        assert ui.order_can_hide_rows == True
        ui.order = order
        assert len(ui.vbx_main.children) == 3

        ui.order_can_hide_rows = False
        assert ui.order == ui.default_order
        assert len(ui.vbx_main.children) == len(ui.default_order)

class TestAnyOf:
    def test_recursive_anyof(self):

        class RuleSetType(str, Enum):
            """how the rules logically multiply. Must be `AND` for schedules"""
            AND: str = "AND"
            OR: str = "OR"

        class Obj(BaseModel):
            a: int
            b: str

        ObjSet = ty.ForwardRef("ObjSet")

        class ObjSet(BaseModel):
            op_type: RuleSetType
            obj_set: list[ty.Union[Obj, ObjSet]]

        ui = AutoObject.from_pydantic_model(ObjSet)
        assert "anyOf" in ui.di_callers['obj_set'].kwargs["items"]

