from datamodel_code_generator import DataModelType, InputFileType, generate
import json
import pathlib
import importlib.util

model_json_schema = {
  "title": "ExampleModel",
  "type": "object",
  "properties": {
    "targetYear": {
      "type": "integer",
      "enum": [2025, 2030, 2050]
    }
  },
  "required": ["targetYear"]
}

fpth = pathlib.Path("generated_model.py")

generate(
    input_=json.dumps(model_json_schema),
    input_file_type=InputFileType.JsonSchema,
    output=fpth,
    output_model_type=DataModelType.PydanticV2BaseModel,
    capitalise_enum_members=True,
)

# ------ load the generated file ------
spec = importlib.util.spec_from_file_location("generated_model", fpth)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

ExampleModel = module.ExampleModel
TargetYear = module.TargetYear

ExampleModel.model_rebuild(_types_namespace={"TargetYear": TargetYear})

print(ExampleModel.model_validate({"targetYear": 2025}))   # ✅ works
print(ExampleModel.model_validate({"targetYear": "2025"})) # ❌ fails


