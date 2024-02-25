from pydantic import BaseModel, Field, RootModel, ConfigDict
from ipyautoui.autoobject import AutoObject, AutoObjectForm
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
        assert len(ui.vbx_widget.children) == 3

        ui.order_can_hide_rows = False
        assert ui.order == ui.default_order
        assert len(ui.vbx_widget.children) == len(ui.default_order)
        

    def test_order_on_init(self):
        class ExampleSchema(BaseModel):
            a: str = Field(default="Test", description="This test is important")
            b: str = Field(default="Test1", description="This test is important too")
            model_config = ConfigDict(json_schema_extra=dict(order=["a"]))
            
        ui = AutoObject.from_pydantic_model(ExampleSchema)
        assert ui.value == {"a": "Test", "b": "Test1"}
        assert len(ui.vbx_widget.children) == 1

        

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


def test_show_null():
    ui = AutoObjectForm.from_pydantic_model(CoreIpywidgets)  # NOTE: CoreIpywidgets has a Nullable values
    assert ui.display_bn_shownull == True
    assert ui.bn_shownull.layout.display == ""
    
def test_show_null_twice():
    from ipyautoui.autoform import demo_autoobject_form
    import ipywidgets as w
    
    # one
    form = demo_autoobject_form()
    assert isinstance(form.bn_shownull, w.ToggleButton)
    assert form.display_bn_shownull == True
    assert form.bn_shownull.layout.display == ""
    form.display_bn_shownull = False
    assert form.bn_shownull.layout.display == "None"
    assert form.display_bn_shownull == False
    
    # two
    ui = AutoObjectForm.from_pydantic_model(CoreIpywidgets)  # NOTE: CoreIpywidgets has a Nullable values
    assert ui.display_bn_shownull == True
    assert ui.bn_shownull.layout.display == "" # or equals("") 
    
def test_dont_show_null():
    class NoNullables(BaseModel):
        a: str = Field(default="Test", description="This test is important")
        b: str = Field(default="Test1", description="This test is important too")

    ui = AutoObjectForm.from_pydantic_model(NoNullables)
    assert ui.display_bn_shownull == False
    assert ui.bn_shownull.layout.display == "None"
    
def test_null_display_on_value_change():
    """Check that displays of widgets are set appropriately when value is changed."""
    class Nullables(BaseModel):
        a: ty.Optional[str] = Field(default=None)
        b: str = Field(default="Test")
        c: ty.Optional[str] = Field(default="Test")

    ui = AutoObject.from_pydantic_model(Nullables)
    assert ["None", "", ""] == [v.layout.display for k, v in ui.di_boxes.items()]
    ui.value = {'a': 'Test', 'b': "Test", 'c': "Test"}
    assert ["", "", ""] == [v.layout.display for k, v in ui.di_boxes.items()]
    ui.value = {'a': 'Test', 'b': "Test", "c": None}
    assert ["", "", "None"] == [v.layout.display for k, v in ui.di_boxes.items()]
  
    
def test_show_title_description():
    #290 
    
    from typing import Annotated
    from pydantic import BaseModel, Field

    from ipyautoui.autoobject import AutoObject


    class NestedStr(BaseModel):
        """A nested model"""
        string: str = Field(description = "nested")
        

    class NestedStrWithTitle(NestedStr):
        """nested string with title"""
        model_config = ConfigDict(title="NestedStrWithTitle")

    class Compound(BaseModel):
        """My compound model"""
        nest_str_1: Annotated[
            NestedStr,
            Field(title="AnnotatedTitle", description="Overridden description nest_str_1, title not coming through")
        ]
        nest_str_2: NestedStr = Field(description="d2")
        nest_str_3: NestedStr = Field(title="nest_str_3", description="d3")
        nest_str_4: NestedStrWithTitle

        
    assert Compound.model_json_schema()["$defs"]["NestedStr"]["title"] == "NestedStr" 
    ui = AutoObject.from_pydantic_model(Compound)
    
    for k in ui.schema["properties"].keys():
        property = (lambda ui, k: ui.schema["properties"][k]["allOf"][0] if "allOf" in ui.schema["properties"][k] else ui.schema["properties"][k])(ui, k)
        assert "title" in property
        bx = ui.di_boxes[k]
        assert "title" in ui.jsonschema_caller[k]["kwargs_box"]
        assert bx.title is not None
    
    titles = ["AnnotatedTitle", "NestedStr", "nest_str_3", "NestedStrWithTitle"]
    for l, t in zip(ui.di_boxes.values(), titles):
        assert l.html_title.value == f"<b>{t}</b>"