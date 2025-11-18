import pytest
import pathlib
import sys
from pytest_examples import find_examples, CodeExample, EvalExample
from ipyautoui.automapschema import (
    _init_model_schema,
    map_widget,
    pydantic_model_from_json_schema,
)
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
from enum import Enum, IntEnum
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


PROJECT_BUILDING_AREA_TARGET_YEARS = [
    2025,
    2026,
    2027,
    2028,
    2029,
    2030,
    2031,
    2032,
    2033,
    2034,
    2035,
    2036,
    2037,
    2038,
    2039,
    2040,
    2050,
]


PROJECT_BUILDING_AREA_SCHEMA = {
    "title": "Project Building Area",
    "type": "array",
    "format": "DataFrame",
    "hide_nan": True,
    "datagrid_index_name": ["section", "title"],
    "items": {
        "title": "Project Buildings",
        "description": "Add any buildings that exist within the project",
        "type": "object",
        "parameter_type": "T",
        "override_units": True,
        "classification": "",
        "properties": {
            "Abbreviation": {
                "enum": ["BLDG"],
                "type": "string",
                "revit_data_type": "TEXT",
                "ifc_data_type": "IfcText",
                "namespace_uri": None,
                "guid": "4ec7e9b3-b1f0-4b76-b0d4-9dd1338b8c2f",
                "guid_source": "MXF",
                "title": "Abbreviation",
                "name": "Abbreviation",
                "description": "equipment type abbreviation, alphabetic characters only, variable length, between 2 and 6 characters",
                "category": "Specifications",
                "section": "Identity Data",
                "tooltip": "asset abbreviation is defined by the [BDNS](https://github.com/theodi/BDNS). Abbreviations must be from those defined in the [BDNS_Abbreviations_Register.csv](https://github.com/theodi/BDNS/blob/master/BDNS_Abbreviations_Register.csv)",
                "property_value_kind": "Single",
                "unit": "",
                "unit_code": "",
                "parameter_type": "T",
                "pset": "Pset_IdentityCore",
                "id": 2696,
                "default": "BLDG",
            },
            "TypeReference": {
                "type": "integer",
                "revit_data_type": "INTEGER",
                "ifc_data_type": "IfcInteger",
                "namespace_uri": None,
                "guid": "f2cb3fad-ff04-4e62-bffa-80d6d3fd2862",
                "guid_source": "MXF",
                "title": "Type Reference",
                "name": "TypeReference",
                "description": "equipment type reference, integer only. Refers to equipment type, there may be multiple instances of the same type",
                "category": "Specifications",
                "section": "Identity Data",
                "tooltip": "",
                "property_value_kind": "Single",
                "unit": "",
                "unit_code": "",
                "parameter_type": "T",
                "pset": "Pset_IdentityCore",
                "id": 2698,
                "default": 1,
            },
            "TargetYear": {
                "enum": PROJECT_BUILDING_AREA_TARGET_YEARS.copy(),
                "revit_data_type": "INTEGER",
                "ifc_data_type": "IfcInteger",
                "namespace_uri": None,
                "guid": "38d4ec6a-9fbb-458f-88a2-b29b33c1ec48",
                "guid_source": "MXF",
                "title": "Target Year",
                "name": "TargetYear",
                "description": "Net Zero Carbon targets change annually. This defined what year the Benchmark Targets should be defined by.",
                "category": "Specifications",
                "section": "Identity Data",
                "tooltip": None,
                "property_value_kind": "Single",
                "unit": "",
                "unit_code": "",
                "parameter_type": "T",
                "pset": "BuildingArea",
                "id": 3090,
                "type": "integer",
            },
            "Name": {
                "revit_data_type": "TEXT",
                "ifc_data_type": "IfcText",
                "namespace_uri": "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/Name",
                "guid": "a13b623a-94ea-4864-a42c-76d3a40acd47",
                "guid_source": "MXF",
                "title": "Building Name",
                "name": "Name",
                "description": "Optional. Add a building name as used in the project for easier identification.",
                "category": "Facilities/Asset Management",
                "section": "Identity Data",
                "tooltip": None,
                "property_value_kind": "Single",
                "unit": "",
                "unit_code": "",
                "parameter_type": "T",
                "pset": "BuildingArea",
                "id": 3091,
                "type": "string",
            },
            "Id": {
                "format": "default",
                "revit_data_type": "INTEGER",
                "ifc_data_type": "IfcInteger",
                "namespace_uri": None,
                "guid": "958e6995-9f04-49d3-ba03-738b6bd66fd0",
                "guid_source": "MXF",
                "title": "Id",
                "name": "Id",
                "description": "",
                "category": "Undefined",
                "section": "Identity Data",
                "tooltip": None,
                "property_value_kind": "Single",
                "unit": "",
                "unit_code": "",
                "parameter_type": "T",
                "pset": "",
                "id": 0,
                "type": "integer",
            },
        },
        "id": 835,
    },
}


def test_pydantic_model_from_json_schema_project_building_area_int_enum():
    model = pydantic_model_from_json_schema(PROJECT_BUILDING_AREA_SCHEMA)
    module = sys.modules[model.__module__]
    target_year_enum = getattr(module, "TargetYear")

    assert issubclass(target_year_enum, IntEnum)
    assert {member.value for member in target_year_enum} == set(
        PROJECT_BUILDING_AREA_TARGET_YEARS
    )

    validated = model.model_validate(
        [
            {
                "Abbreviation": "BLDG",
                "TypeReference": 1,
                "TargetYear": 2025,
                "Name": "Main Building",
                "Id": 1,
            }
        ]
    )
    
    validated_string_date = model.model_validate(
        [
            {
                "Abbreviation": "BLDG",
                "TypeReference": 1,
                "TargetYear": "2025",
                "Name": "Main Building",
                "Id": 1,
            }
        ]
    )
    
    assert validated, validated_string_date