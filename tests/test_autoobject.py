from pydantic import BaseModel, Field, RootModel
from ipyautoui.autoobject import AutoObject
import pytest
import stringcase
from ipyautoui.demo_schemas import RootEnum, RootArrayEnum, CoreIpywidgets


class TestAutoObject:
    def test_root(self):
        with pytest.raises(ValueError) as e:
            ExampleRoot = RootModel[str]
            ui = AutoObject.from_schema(ExampleRoot)
            assert e == "properties must be in kwargs"

    def test_simple(self):
        class ExampleSchema(BaseModel):
            text: str = Field(default="Test", description="This test is important")

        ui = AutoObject.from_schema(ExampleSchema)
        assert ui.value == {"text": "Test"}
        print("done")


class TestAutoObjectRowOrder:
    ui = AutoObject.from_schema(CoreIpywidgets)

    def test_order(self):
        self.ui = AutoObject.from_schema(CoreIpywidgets)

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
        assert len(self.ui.vbx_main.children) == 3

        self.ui.order_can_hide_rows = False
        assert self.ui.order == self.ui.default_order
        assert len(self.ui.vbx_main.children) == len(self.ui.default_order)
