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
    {'InstanceReference': 3, 'LevelReference': None, 'VolumeReference': None, 'TypeMark': 'DB-Type1', 'TypeSpecId': 2, 'Id': 4}
    )
)
display(edittsvwdiff)
# -
type_spec_json_schema = {'datagrid_index_name': ['section', 'title', 'unit'],
 'format': 'DataFrame',
 'hide_nan': True,
 'items': {'classification': 'Pr_60_70_22_22',
           'description': 'A standardised distribution board divides an '
                          'electrical power feed into subsidiary circuits, '
                          'while providing a protective fuse or circuit '
                          'breaker for each circuit, in a common enclosure.',
           'id': 3,
           'override_units': True,
           'parameter_type': 'T',
           'properties': {'Abbreviation': {'category': 'Specifications',
                                           'default': 'DB',
                                           'description': 'equipment type '
                                                          'abbreviation, '
                                                          'alphabetic '
                                                          'characters only, '
                                                          'variable length, '
                                                          'between 2 and 6 '
                                                          'characters',
                                           'enum': ['DB'],
                                           'guid': '4ec7e9b3-b1f0-4b76-b0d4-9dd1338b8c2f',
                                           'guid_source': 'MXF',
                                           'id': 7,
                                           'ifc_data_type': 'IfcText',
                                           'name': 'Abbreviation',
                                           'namespace_uri': None,
                                           'parameter_type': 'T',
                                           'property_value_kind': 'Single',
                                           'pset': 'Pset_IdentityExtra',
                                           'revit_data_type': 'TEXT',
                                           'section': 'Identity Data',
                                           'title': 'Abbreviation',
                                           'tooltip': 'asset abbreviation is '
                                                      'defined by the '
                                                      '[BDNS](https://github.com/theodi/BDNS). '
                                                      'Abbreviations must be '
                                                      'from those defined in '
                                                      'the '
                                                      '[BDNS_Abbreviations_Register.csv](https://github.com/theodi/BDNS/blob/master/BDNS_Abbreviations_Register.csv)',
                                           'type': 'string',
                                           'unit': '',
                                           'unit_code': ''},
                          'ClassificationUniclassProductNumber': {'autoui': 'aectemplater_ui.widgets.uniclass.UniclassPr',
                                                                  'category': 'Specifications',
                                                                  'default': 'Pr_60_70_22_22',
                                                                  'description': 'Product '
                                                                                 'Code '
                                                                                 'that '
                                                                                 'matches '
                                                                                 'a '
                                                                                 'code '
                                                                                 'within '
                                                                                 'the '
                                                                                 'Uniclass '
                                                                                 'Pr '
                                                                                 'tables. '
                                                                                 'https://uniclass.thenbs.com/taxon/pr',
                                                                  'guid': '8212e2e8-d020-4127-bada-a9cc7f5f4dcc',
                                                                  'guid_source': 'MXF',
                                                                  'id': 4,
                                                                  'ifc_data_type': 'IfcText',
                                                                  'name': 'ClassificationUniclassProductNumber',
                                                                  'namespace_uri': None,
                                                                  'parameter_type': 'T',
                                                                  'property_value_kind': 'Single',
                                                                  'pset': 'Pset_IdentityExtra',
                                                                  'revit_data_type': 'TEXT',
                                                                  'section': 'Identity '
                                                                             'Data',
                                                                  'title': 'Classification '
                                                                           'Uniclass '
                                                                           'Product '
                                                                           'Number',
                                                                  'tooltip': 'Created '
                                                                             'and '
                                                                             'used '
                                                                             'by '
                                                                             'the '
                                                                             'Autodesk '
                                                                             'Classification '
                                                                             'Manager '
                                                                             'for '
                                                                             'Revit',
                                                                  'type': 'string',
                                                                  'unit': '',
                                                                  'unit_code': ''},
                          'ClassificationUniclassSystemNumber': {'autoui': 'aectemplater_ui.widgets.uniclass.UniclassSs',
                                                                 'category': 'Specifications',
                                                                 'default': '',
                                                                 'description': 'System '
                                                                                'Code '
                                                                                'that '
                                                                                'matches '
                                                                                'a '
                                                                                'code '
                                                                                'within '
                                                                                'the '
                                                                                'Uniclass '
                                                                                'Ss '
                                                                                'tables. '
                                                                                'https://uniclass.thenbs.com/taxon/ss',
                                                                 'guid': 'f16eb500-0976-4c80-b5d1-082470821ef8',
                                                                 'guid_source': 'MXF',
                                                                 'id': 5,
                                                                 'ifc_data_type': 'IfcText',
                                                                 'name': 'ClassificationUniclassSystemNumber',
                                                                 'namespace_uri': None,
                                                                 'parameter_type': 'T',
                                                                 'property_value_kind': 'Single',
                                                                 'pset': 'Pset_IdentityExtra',
                                                                 'revit_data_type': 'TEXT',
                                                                 'section': 'Identity '
                                                                            'Data',
                                                                 'title': 'Classification '
                                                                          'Uniclass '
                                                                          'System '
                                                                          'Number',
                                                                 'tooltip': 'Created '
                                                                            'and '
                                                                            'used '
                                                                            'by '
                                                                            'the '
                                                                            'Autodesk '
                                                                            'Classification '
                                                                            'Manager '
                                                                            'for '
                                                                            'Revit',
                                                                 'type': 'string',
                                                                 'unit': '',
                                                                 'unit_code': ''},
                          'FunctionReference': {'category': 'Specifications',
                                                'description': 'indicates the '
                                                               'functional use '
                                                               'of an element',
                                                'guid': 'af5e6360-50bd-4b57-90c7-2a4afea96937',
                                                'guid_source': 'MXF',
                                                'id': 1,
                                                'ifc_data_type': 'IfcText',
                                                'name': 'FunctionReference',
                                                'namespace_uri': None,
                                                'parameter_type': 'T',
                                                'property_value_kind': 'Single',
                                                'pset': 'Pset_IdentityExtra',
                                                'revit_data_type': 'TEXT',
                                                'section': 'Identity Data',
                                                'title': 'Function Reference',
                                                'tooltip': None,
                                                'type': 'string',
                                                'unit': '',
                                                'unit_code': ''},
                          'Id': {'anyOf': [{'type': 'integer'},
                                           {'type': 'null'}],
                                 'category': 'Undefined',
                                 'description': '',
                                 'format': 'default',
                                 'guid': '958e6995-9f04-49d3-ba03-738b6bd66fd0',
                                 'guid_source': 'MXF',
                                 'id': 0,
                                 'ifc_data_type': 'IfcInteger',
                                 'name': 'Id',
                                 'namespace_uri': None,
                                 'parameter_type': 'T',
                                 'property_value_kind': 'Single',
                                 'pset': '',
                                 'revit_data_type': 'INTEGER',
                                 'section': 'Identity Data',
                                 'title': 'Id',
                                 'tooltip': None,
                                 'unit': '',
                                 'unit_code': ''},
                          'ManufacturerWebsite': {'anyOf': [{'type': 'string'},
                                                            {'type': 'null'}],
                                                  'category': 'Specifications',
                                                  'description': '',
                                                  'guid': '2e28aa00-71ac-4225-85be-b9fc09e4484e',
                                                  'guid_source': 'BSDD',
                                                  'id': 16,
                                                  'ifc_data_type': 'IfcText',
                                                  'name': 'ManufacturerWebsite',
                                                  'namespace_uri': None,
                                                  'parameter_type': 'T',
                                                  'property_value_kind': 'Single',
                                                  'pset': 'Pset_DistributionBoard',
                                                  'revit_data_type': 'URL',
                                                  'section': 'Manufacturer',
                                                  'title': 'Manufacturer '
                                                           'Website',
                                                  'tooltip': 'Website...',
                                                  'unit': '',
                                                  'unit_code': ''},
                          'Notes': {'anyOf': [{'type': 'string'},
                                              {'type': 'null'}],
                                    'autoui': 'aectemplater_ui.widgets.notes.MarkdownWidget',
                                    'category': 'Specifications',
                                    'description': 'free flowing notes section',
                                    'guid': '9faa8b0b-ab25-4dce-bb4d-3f8320522146',
                                    'guid_source': 'MXF',
                                    'id': 12,
                                    'ifc_data_type': 'IfcText',
                                    'name': 'Notes',
                                    'namespace_uri': None,
                                    'parameter_type': 'T',
                                    'property_value_kind': 'Single',
                                    'pset': 'Pset_DistributionBoard',
                                    'revit_data_type': 'TEXT',
                                    'section': 'Application',
                                    'title': 'Notes',
                                    'tooltip': '...',
                                    'unit': '',
                                    'unit_code': ''},
                          'OverallLength': {'anyOf': [{'type': 'number'},
                                                      {'type': 'null'}],
                                            'category': 'Specifications',
                                            'description': '',
                                            'guid': '2c27007d-549f-4664-8232-5efdb8d7c1dc',
                                            'guid_source': 'MXF',
                                            'id': 13,
                                            'ifc_data_type': 'IfcLengthMeasure',
                                            'name': 'OverallLength',
                                            'namespace_uri': None,
                                            'parameter_type': 'T',
                                            'property_value_kind': 'Single',
                                            'pset': 'Pset_DistributionBoard',
                                            'revit_data_type': 'LENGTH',
                                            'section': 'Manufacturer',
                                            'title': 'Overall Length',
                                            'tooltip': None,
                                            'unit': 'mm',
                                            'unit_code': 'mm'},
                          'Symbol': {'category': 'Specifications',
                                     'default': '',
                                     'description': 'equipment type symbol. '
                                                    'Filename of PNG image',
                                     'guid': 'e30c1dbe-9dd5-4b20-b102-8cbbd07faa70',
                                     'guid_source': 'MXF',
                                     'id': 10,
                                     'ifc_data_type': 'IfcText',
                                     'name': 'Symbol',
                                     'namespace_uri': None,
                                     'parameter_type': 'T',
                                     'property_value_kind': 'Single',
                                     'pset': 'Pset_IdentityExtra',
                                     'revit_data_type': 'TEXT',
                                     'section': 'Identity Data',
                                     'title': 'Symbol',
                                     'tooltip': 'this is the same name as the '
                                                'symbol imported in Revit for '
                                                'schematics',
                                     'type': 'string',
                                     'unit': '',
                                     'unit_code': ''},
                          'TypeReference': {'category': 'Specifications',
                                            'default': 1,
                                            'description': 'equipment type '
                                                           'reference, integer '
                                                           'only. Refers to '
                                                           'equipment type, '
                                                           'there may be '
                                                           'multiple instances '
                                                           'of the same type',
                                            'guid': 'f2cb3fad-ff04-4e62-bffa-80d6d3fd2862',
                                            'guid_source': 'MXF',
                                            'id': 8,
                                            'ifc_data_type': 'IfcInteger',
                                            'name': 'TypeReference',
                                            'namespace_uri': None,
                                            'parameter_type': 'T',
                                            'property_value_kind': 'Single',
                                            'pset': 'Pset_IdentityExtra',
                                            'revit_data_type': 'INTEGER',
                                            'section': 'Identity Data',
                                            'title': 'Type Reference',
                                            'tooltip': '',
                                            'type': 'integer',
                                            'unit': '',
                                            'unit_code': ''},
                          'Voltage': {'anyOf': [{'type': 'number'},
                                                {'type': 'null'}],
                                      'category': 'Specifications',
                                      'description': '',
                                      'guid': '10044af7-e223-443c-a89d-10b20f2b766e',
                                      'guid_source': 'BSDD',
                                      'id': 11,
                                      'ifc_data_type': 'IfcElectricVoltageMeasure',
                                      'name': 'Voltage',
                                      'namespace_uri': 'https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/prop/Voltage',
                                      'parameter_type': 'T',
                                      'property_value_kind': 'Single',
                                      'pset': 'Pset_DistributionBoard',
                                      'revit_data_type': 'ELECTRICAL_POTENTIAL',
                                      'section': 'Electrical',
                                      'title': 'Voltage',
                                      'tooltip': 'Voltage...',
                                      'unit': 'V',
                                      'unit_code': 'V'}},
           'title': 'Distribution Board',
           'type': 'object'},
 'title': 'Distribution Board',
 'type': 'array'}




fpth = pathlib.Path("type-spec-test-schema.py")
model_file = pydantic_model_file_from_json_schema(type_spec_json_schema, fpth)
model = pydantic_model_from_json_schema(type_spec_json_schema)
tsedittsvwdiff = EditTsvWithDiff(transposed=True,model=model, value=[{'Abbreviation': 'DB',
  'TypeReference': 1,
  'Symbol': '',
  'ClassificationUniclassProductNumber': 'Pr_60_70_22_22',
  'ClassificationUniclassSystemNumber': '',
  'FunctionReference': '',
  'Notes': '',
  'OverallLength': 1.0,
  'ManufacturerWebsite': 'https://maxfordham.com/',
  'Voltage': 1.0,
  'Id': 2}]
)
display(tsedittsvwdiff)

print(model)

# +

# Imports and schema
from typing import Optional, List, Literal
from datetime import date, datetime, time, timedelta
from enum import Enum
from pydantic import BaseModel, Field, RootModel, ConfigDict, StringConstraints, conint, constr
from ipyautoui.custom.edittsv import EditTsvWithDiff, EditTsvFileUpload
from ipyautoui.custom.edittsv_with_diff_and_key_mapping import EditTsvWithDiffAndKeyMapping
from ipyautoui.custom.fileupload import TempFileUploadProcessor
from typing_extensions import Annotated
import xlsxdatagrid as xdg
import pathlib
import ipywidgets as w
from IPython.display import display

class Test(BaseModel):
    a_string: str = Field(
        "empty",
        title="A String",
    )

    a_list: str = Field(
        "[]",
        title="A List",
    )

class TestArray(RootModel[List[Test]]):
    model_config = ConfigDict(
        title="TestArrayString",
    )
    root: List[Test]



# -

edit_tsv_w_diff = EditTsvWithDiff(
    model=TestArray,
    transposed=False,
    primary_key_name="a_string",
    header_depth=1,
    exclude_metadata=True,
    value=[{"a_string": "hm", "a_list": "['Hello', 'Hey']"}]
)
display(edit_tsv_w_diff)

display(edit_tsv_w_diff.value)

eval(edit_tsv_w_diff.value[0]["a_list"])


