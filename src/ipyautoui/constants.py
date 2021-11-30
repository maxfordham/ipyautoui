import pathlib

DIR_MODULE = pathlib.Path(__file__).parent

BUTTON_WIDTH_MIN = '41px'
BUTTON_WIDTH_MEDIUM = '90px'
BUTTON_HEIGHT_MIN = '25px'
ROW_WIDTH_MEDIUM = '120px'
ROW_WIDTH_MIN = '60px'

# documentinfo ------------------------------
#  update this with WebApp data. TODO: delete this? 
ROLES = ('Design Lead',
'Project Engineer',
'Engineer',
'Project Coordinator',
'Project Administrator',
'Building Performance Modeller')

DI_JSONSCHEMA_WIDGET_MAP = {
    'minimum': 'min',
    'maximum': 'max',
    'enum': 'options',
    'default': 'value',
    'description': 'autoui_description'
}
#  ^ this is how the json-schema names map to ipywidgets.

def load_test_constants():
    """only in use for debugging within the package. not used in production code.

    Returns:
        module: test_constants object
    """
    from importlib.machinery import SourceFileLoader
    path_testing_constants = DIR_MODULE.parents[1] / 'tests' / 'constants.py'
    test_constants = SourceFileLoader("constants", str(path_testing_constants)).load_module()
    return test_constants