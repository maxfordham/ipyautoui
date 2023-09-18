import pytest
import pathlib
from pytest_examples import find_examples, CodeExample, EvalExample
from ipyautoui.automapschema import _init_model_schema, map_widget
from ipyautoui.demo_schemas import CoreIpywidgets
import stringcase
from pydantic import BaseModel, Field, conint
from ipyautoui.demo_schemas.array_object_dataframe import ArrayObjectDataframe

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


def test_range_slider():
    class Test(BaseModel):
        # a: int
        b: tuple[conint(ge=0, le=10), conint(ge=0, le=10)] = Field(
            (3, 5),
            title="b title",
            json_schema_extra=dict(tooltip="b tooltip"),
        )

    model, schema = _init_model_schema(Test)
    pr = schema["properties"]
    wi = {
        property_key: map_widget(property_schema)
        for property_key, property_schema in pr.items()
    }
    assert wi["b"].kwargs["tooltip"] == "b tooltip"
    assert wi["b"].kwargs["min"] == 0
    assert wi["b"].kwargs["max"] == 10
    print("done")


def test_core_ipywidgets_map_widget():
    model, schema = _init_model_schema(CoreIpywidgets)
    pr = schema["properties"]
    wi = {
        property_key: map_widget(property_schema, fail_on_error=True)
        for property_key, property_schema in pr.items()
    }
    for k, v in wi.items():
        got, target = v.autoui.__name__, stringcase.pascalcase(k)
        try:
            assert got in target
        except:
            s = v.schema_
            print(got, target)
            raise AssertionError(got, target)


def test_array_object_dataframe_map_widget():
    model, schema = _init_model_schema(ArrayObjectDataframe)
    pr = schema["properties"]
    wi = {
        property_key: map_widget(property_schema, fail_on_error=True)
        for property_key, property_schema in pr.items()
    }
    for k, v in wi.items():
        got, target = v.autoui.__name__, stringcase.pascalcase(k)
        try:
            assert got in target
        except:
            s = v.schema_
            print(got, target)
            raise AssertionError(got, target)
    print("done")
