import pytest
import pathlib
from pytest_examples import find_examples, CodeExample, EvalExample
from ipyautoui.automapschema import _init_model_schema, map_widget
import casefy
from pydantic import BaseModel, Field, conint
from ipyautoui.demo_schemas import (
    ArrayObjectDataframe,
    CoreIpywidgets,
    ComplexSerialisation,
    RootEnum,
)
import typing as ty
from typing_extensions import Annotated
from enum import Enum
from jsonref import replace_refs
from ipyautoui.automapschema import widgetcaller

fpth_module = (
    pathlib.Path(__file__).parent.parent / "src" / "ipyautoui" / "automapschema.py"
)


@pytest.mark.parametrize("example", find_examples(fpth_module), ids=str)
def test_docstrings(example: CodeExample, eval_example: EvalExample):
    eval_example.run_print_check(example)


def test_simple():
    class Test(BaseModel):
        # a: int
        b: int = Field(
            1, title="b title", ge=0, le=10, json_schema_extra=dict(tooltip="b tooltip")
        )

    model, schema = _init_model_schema(Test)
    pr = schema["properties"]
    wi = {
        property_key: map_widget(property_schema)
        for property_key, property_schema in pr.items()
    }
    assert wi["b"].kwargs["tooltip"] == "b tooltip"
    print("done")


def assert_widget_map(pydantic_model):
    model, schema = _init_model_schema(pydantic_model)
    pr = schema["properties"]
    wi = {
        property_key: map_widget(property_schema)
        for property_key, property_schema in pr.items()
    }
    for k, v in wi.items():
        got, target = v.autoui.__name__, casefy.pascalcase(k)
        try:
            assert got in target
        except:
            s = v.schema_
            print(got, target)
            raise AssertionError(got, target)


def test_range_slider():
    class Test(BaseModel):
        """this is a test UI form to demonstrate how pydantic class can  be used to generate an ipywidget input form.
        only simple datatypes used (i.e. not lists/arrays or objects)
        """

        int_slider_nullable: ty.Optional[Annotated[int, Field(ge=1, le=3)]] = None

    model, schema = _init_model_schema(Test)
    assert_widget_map(schema)


def test_combobox():
    class FruitEnum(str, Enum):
        """fruit example."""

        apple = "apple"
        pear = "pear"
        banana = "banana"
        orange = "orange"

    class Test(BaseModel):
        """this is a test UI form to demonstrate how pydantic class can  be used to generate an ipywidget input form.
        only simple datatypes used (i.e. not lists/arrays or objects)
        """

        combobox: ty.Union[str, FruitEnum] = Field("apple")

    assert_widget_map(Test)


def test_combobox_mapped():
    class Test(BaseModel):
        """Test to see that widgets with private traits are captured by kwargs when mapping to the widget.
        E.g. ComboboxMapped has the traits `_value` and `_options` which should be captured by kwargs.
        """

        combobox_mapped: str = Field(
            "apple",
            json_schema_extra=dict(
                options={"APPLE": "apple", "PEAR": "pear"},
                autoui="ipyautoui.custom.combobox_mapped.ComboboxMapped",
            ),
        )

    model, schema = _init_model_schema(Test)
    assert_widget_map(schema)
    widget_caller = map_widget(schema["properties"]["combobox_mapped"])
    assert widget_caller.kwargs["value"] == "apple"
    assert widget_caller.kwargs["options"] == {"APPLE": "apple", "PEAR": "pear"}


def test_CoreIpywidgets():
    assert_widget_map(CoreIpywidgets)


def test_ArrayObjectDataframe():
    assert_widget_map(ArrayObjectDataframe)


def test_ComplexSerialisation():
    assert_widget_map(ComplexSerialisation)


def test_union():
    class MyObject(BaseModel):
        stringy: str = Field("stringy", description="asdfsadf")
        inty: int = 1
        floaty: ty.Union[float, str] = 1.5

    di = replace_refs(MyObject.model_json_schema(), merge_props=True)
    caller = map_widget(di)
    assert "anyOf" in caller.kwargs["properties"]["floaty"]
    ui = widgetcaller(caller)
    assert len(ui.di_widgets["floaty"].anyOf) == 2
