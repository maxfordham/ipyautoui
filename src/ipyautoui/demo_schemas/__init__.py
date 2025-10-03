# do not add anything but demo pydantic schemas here
# the order they appear below will be read and used to update the order in the `DemoReel`

from ipyautoui.demo_schemas.core_ipywidgets import CoreIpywidgets
from ipyautoui.demo_schemas.override_ipywidgets import OverrideIpywidgets
from ipyautoui.demo_schemas.complex_serialization import ComplexSerialisation
from ipyautoui.demo_schemas.nested import Nested
from ipyautoui.demo_schemas.null_and_required import NullAndRequired
from ipyautoui.demo_schemas.editable_datagrid import EditableGrid
from ipyautoui.demo_schemas.editable_datagrid_transposed import EditableGridTransposed
from ipyautoui.demo_schemas.editable_datagrid_with_nullable import (
    EditableGridWithNullable,
)
from ipyautoui.demo_schemas.multiindex_editable_grid import MultiIndexEditableGrid
from ipyautoui.demo_schemas.nested_editable_datagrid import NestedEditableGrid
from ipyautoui.demo_schemas.root_array import RootArray
from ipyautoui.demo_schemas.root_simple import RootSimple
from ipyautoui.demo_schemas.root_enum import RootEnum
from ipyautoui.demo_schemas.root_array_enum import RootArrayEnum
from ipyautoui.demo_schemas.array_object_dataframe import ArrayObjectDataframe
from ipyautoui.demo_schemas.array_examples import ArrayWithUnionType
from ipyautoui.demo_schemas.recursive_array import RecursiveArray
from ipyautoui.demo_schemas.recursive_object import RecursiveObject
from ipyautoui.demo_schemas.ruleset import ScheduleRuleSet
from ipyautoui.demo_schemas.pydantic_validation import PydanticValidation
from ipyautoui.demo_schemas.pydantic_validation_list import PydanticValidationList
from ipyautoui.demo_schemas.pydantic_validation_error import PydanticValidationError
