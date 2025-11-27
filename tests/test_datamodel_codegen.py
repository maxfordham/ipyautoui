import pytest
from pydantic import BaseModel
from src.ipyautoui._utils import pydantic_model_from_json_schema
import casefy
from datamodel_code_generator.parser.base import title_to_class_name


@pytest.mark.parametrize("title,expected_name", [
    ("AHU Detailed Specification", "AhuDetailedSpecification"),
    ("Air Handling Unit (AHU)", "AirHandlingUnitAhu"),
    ("Cable Conduit", "CableConduit"),
    ("Cast-in-socket", "CastInSocket"),
    ("Electrical Socket-Outlet", "ElectricalSocketOutlet"),
    ("PTZ CCTV Camera", "PtzCctvCamera"),
    ("Combined Smoke & Heat Detector", "CombinedSmokeHeatDetector"),
    ("Sensor CO2 Monitor", "SensorCo2Monitor"),
])
def test_title_to_classname_conversion(title, expected_name):
    """Test that various title formats convert to expected class names"""
    schema = {
        "title": title,
        "type": "object",
        "properties": {"value": {"type": "string"}}
    }
    
    resolved_title = title_to_class_name(title)
    assert expected_name == resolved_title



@pytest.mark.parametrize("title,expected_name", [
    ("AHU Detailed Specification", "AhuDetailedSpecification"),
    ("Air Handling Unit (AHU)", "AirHandlingUnitAhu"),
    ("Cable Conduit", "CableConduit"),
    ("Cast-in-socket", "CastInSocket"),
    ("Electrical Socket-Outlet", "ElectricalSocketOutlet"),
    ("PTZ CCTV Camera", "PtzCctvCamera"),
    ("Combined Smoke & Heat Detector", "CombinedSmokeHeatDetector"),
    ("Sensor CO2 Monitor", "SensorCo2Monitor"),
])
def test_title_to_classname_conversion_manual(title, expected_name):
    """Test that various title formats convert to expected class names"""
    schema = {
        "title": title,
        "type": "object",
        "properties": {"value": {"type": "string"}}
    }
    
    words = title.split()
    converted_title = ''.join(word.capitalize() for word in words)
    casefy_title = casefy.pascalcase(converted_title)
    
    assert casefy_title == expected_name
    
    
@pytest.mark.parametrize("title,expected_name", [
    ("AHU Detailed Specification", "AhuDetailedSpecification"),
    ("Air Handling Unit (AHU)", "AirHandlingUnitAhu"),
    ("Cable Conduit", "CableConduit"),
    ("Cast-in-socket", "CastInSocket"),
    ("Electrical Socket-Outlet", "ElectricalSocketOutlet"),
    ("PTZ CCTV Camera", "PtzCctvCamera"),
    ("Combined Smoke & Heat Detector", "CombinedSmokeHeatDetector"),
    ("Sensor CO2 Monitor", "SensorCo2Monitor"),
])
def test_title_to_classname_conversion_with_codegen_function(title, expected_name):
    """Test that various title formats convert to expected class names"""
    schema = {
        "title": title,
        "type": "object",
        "properties": {"value": {"type": "string"}}
    }
    
    model = pydantic_model_from_json_schema(schema)
    assert issubclass(model, BaseModel)
    assert model.__name__ == expected_name


def test_pydantic_model_from_json_schema_acronym():
    """Test that acronyms are converted correctly: 'AHU' -> 'Ahu'"""
    schema = {
        "title": "AHU Detailed Specification",
        "type": "object",
        "properties": {
            "model": {"type": "string"},
            "capacity": {"type": "number"}
        }
    }
    
    model = pydantic_model_from_json_schema(schema)
    
    # Check that model is a BaseModel subclass
    assert issubclass(model, BaseModel)
    
    # Check model name matches expected conversion
    assert model.__name__ == "AhuDetailedSpecification"
    
    # Test instantiation
    instance = model(model="AHU-100", capacity=5000.0)
    assert instance.model == "AHU-100"
    assert instance.capacity == 5000.0


def test_pydantic_model_from_json_schema_multi_word():
    """Test multi-word title conversion"""
    schema = {
        "title": "Project Building Area",
        "type": "object",
        "properties": {
            "area": {"type": "number"},
            "units": {"type": "string"}
        }
    }
    
    model = pydantic_model_from_json_schema(schema)
    
    assert issubclass(model, BaseModel)
    assert model.__name__ == "ProjectBuildingArea"


def test_pydantic_model_from_json_schema_no_title():
    """Test model generation when no title is provided"""
    schema = {
        "type": "object",
        "properties": {
            "value": {"type": "string"}
        }
    }
    
    model = pydantic_model_from_json_schema(schema)
    
    assert issubclass(model, BaseModel)
    # Should default to "Model"
    assert model.__name__ == "Model"