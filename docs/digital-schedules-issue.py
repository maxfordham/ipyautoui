from ipyautoui.automapschema import pydantic_model_from_json_schema
from ipyautoui.automapschema import pydantic_model_file_from_json_schema
from ipyautoui.custom.edittsv import EditTsvWithDiff
import pathlib
import numpy as np


json_schema = {
    "$defs": {
        "DistributionBoardItem": {
            "properties": {
                "InstanceReference": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": 1,
                    "description": "equipment instance reference, integer only. Refers to equipment instance.",
                    "title": "Instance Reference",
                },
                "LevelReference": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": "indicates the floor level an element is located on",
                    "title": "Level Reference",
                },
                "VolumeReference": {
                    "anyOf": [{"type": "string"}, {"type": "null"}],
                    "default": None,
                    "description": "indicates the floor level an element is located on",
                    "title": "Volume Reference",
                },
                "TypeMark": {
                    "anyOf": [{"$ref": "#/$defs/TypeMark"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Type Mark",
                },
                "TypeSpecId": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Type Spec Id",
                },
                "Id": {
                    "anyOf": [{"type": "integer"}, {"type": "null"}],
                    "default": None,
                    "description": "",
                    "title": "Id",
                },
            },
            "title": "DistributionBoardItem",
            "type": "object",
        },
        "TypeMark": {
            "enum": ["DB-Type1", "DB-Type2", "DB-Type3"],
            "title": "TypeMark",
            "type": "string",
        },
    },
    "items": {"$ref": "#/$defs/DistributionBoardItem"},
    "title": "DistributionBoard",
    "type": "array",
}


# +

fpth = pathlib.Path("test-schema.py")
model_file = pydantic_model_file_from_json_schema(json_schema, fpth)
model = pydantic_model_from_json_schema(json_schema)
edittsvwdiff = EditTsvWithDiff(model=model, value=(
    {'InstanceReference': 2, 'LevelReference': '1', 'VolumeReference': '1', 'TypeMark': 'DB-Type1', 'TypeSpecId': 2, 'Id': 3},
    {'InstanceReference': 3, 'LevelReference': np.nan, 'VolumeReference': np.nan, 'TypeMark': 'DB-Type1', 'TypeSpecId': 2, 'Id': 4}
    )
)
display(edittsvwdiff)
# -


