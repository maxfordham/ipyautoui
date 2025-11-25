from ipyautoui._utils import pydantic_model_from_json_schema
from ipyautoui._utils import pydantic_model_file_from_json_schema
from ipyautoui.custom.edittsv import EditTsvWithDiff
import pathlib
import numpy as np

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
tsedittsvwdiff = EditTsvWithDiff(transposed=True, model=model, primary_key_name = "Id", value=[{'Abbreviation': 'DB',
  'TypeReference': 1,
  'Symbol': '',
  'ClassificationUniclassProductNumber': 'Pr_60_70_22_22',
  'ClassificationUniclassSystemNumber': '',
  'FunctionReference': None,
  'Notes': None,
  'OverallLength': None,
  'ManufacturerWebsite': 'https://maxfordham.com/',
  'Voltage': None,
  'Id': 2}]
)
display(tsedittsvwdiff)

if __name__ == "__main__":
    display(tsedittsvwdiff.text.value)
    display(tsedittsvwdiff.value)

# if __name__ == "__main__":
#     display(tsedittsvwdiff.value)
    # display(tsedittsvwdiff.text.value)
    # cleaned_val = xdg.read_records(tsedittsvwdiff.value, model, only_for=["FunctionReference", "Notes", "Voltage", "OverallLength"])
    # display(cleaned_val)

# if __name__ == "__main__":
#     display(tsedittsvwdiff.value)
#     cleaned_val = xdg.read_records(tsedittsvwdiff.value, model, only_for=["FunctionReference", "Notes"])
#     display(cleaned_val)
#     tsedittsvwdiff.value = xdg.read_records(tsedittsvwdiff.value, model, only_for=["FunctionReference", "Notes"])
#     display(tsedittsvwdiff.value)
    # display(tsedittsvwdiff.ddiff.diff)


