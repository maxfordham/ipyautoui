# +


import typing as ty
import ipywidgets as w
from pydantic import BaseModel, Field
from ipyautoui.nullable import nullable
from jsonref import replace_refs
from ipyautoui.constants import MAP_JSONSCHEMA_TO_IPYWIDGET
from ipyautoui._utils import remove_non_present_kwargs, frozenmap, obj_from_importstr
from ipyautoui.custom.markdown_widget import MarkdownWidget
from ipyautoui.custom.filechooser import FileChooser
from ipyautoui.custom.date_string import DatePickerString, NaiveDatetimePickerString
from ipyautoui.autobox import AutoBox
from tempfile import TemporaryDirectory
import pathlib
from datamodel_code_generator import DataModelType, InputFileType, generate
import json
import importlib.util
import sys

import logging

logger = logging.getLogger(__name__)

def pydantic_model_file_from_json_schema(json_schema, fpth):
    return generate(
            json.dumps(json_schema, ensure_ascii=False),
            input_file_type=InputFileType.JsonSchema,
            input_filename="example.json",
            output=fpth,
            output_model_type=DataModelType.PydanticV2BaseModel,
            capitalise_enum_members=True,
        )

def pydantic_model_from_json_schema(json_schema: dict) -> ty.Type[BaseModel]:
    load = json_schema["title"].replace(" ", "") if "title" in json_schema else "Model"

    with TemporaryDirectory() as temporary_directory_name:
        temporary_directory = pathlib.Path(temporary_directory_name)
        file_path = "model.py"
        module_name = file_path.split(".")[0]
        output = pathlib.Path(temporary_directory / file_path)
        
        pydantic_model_file_from_json_schema(json_schema, output)

        #HACK refer to https://github.com/koxudaxi/datamodel-code-generator/issues/2534 for official fix, then remove the PATCH LOGIC once that is resolved
        # --- NEW PATCH LOGIC ---
        if json_schema.get("title") == "Project Building Area":
            text = output.read_text()

            # Replace Enum → IntEnum in TargetYear only
            text = text.replace("class TargetYear(Enum):", "class TargetYear(IntEnum):")

            # Ensure IntEnum is imported
            if "from enum import IntEnum" not in text:
                text = text.replace("from enum import Enum", "from enum import Enum, IntEnum")

            output.write_text(text)
        # --- END PATCH LOGIC ---

        spec = importlib.util.spec_from_file_location(module_name, output)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return getattr(module, load)

def _init_model_schema(
    schema=None, by_alias=False, generate_pydantic_model_from_json_schema = True
) -> tuple[ty.Optional[ty.Type[BaseModel]], dict]:
    if schema is None:
        return None, {
            "format": "dataframe",
            "type": "array",
            "items": {"properties": {}},
        }
    if isinstance(schema, dict):
        if generate_pydantic_model_from_json_schema:
            model = pydantic_model_from_json_schema(schema)
        else:
            model = None
        # IDEA: Possible implementations -@jovyan at 8/24/2022, 12:05:02 PM
        # jsonschema_to_pydantic
        # https://koxudaxi.github.io/datamodel-code-generator/using_as_module/
    else:
        model = schema  # the "model" passed is a pydantic model
        schema = model.model_json_schema(by_alias=by_alias).copy()

    schema = replace_refs(schema, merge_props=True)
    schema = {k: v for k, v in schema.items() if k != "$defs"}
    return model, schema


def pydantic_validate(model, value):
    return model.model_validate(value).model_dump(mode="json")


def is_allowed_type(di: dict) -> bool:
    #  https://json-schema.org/understanding-json-schema/reference/combining.html
    if "anyOf" in di:
        return True
    elif "allOf" in di:  # do something...
        logger.warning(f"allOf not implemented \nGiven : {str(di)}")
        return False
    elif "oneOf" in di:
        logger.warning(f"allOf not implemented \nGiven : {str(di)}")
        return False
    elif "not" in di:
        logger.warning(f"allOf not implemented \nGiven : {str(di)}")
        return False
    else:
        raise ValueError(
            f"of: anyOf, allOf, oneOf or not, only anyOf is supported. \n Given : {str(di)}"
        )


def flatten_allOf(di: dict) -> dict:
    if "allOf" in di.keys():
        for _ in di["allOf"]:
            di = {**di, **_}
        return {k: v for k, v in di.items() if k != "allOf"}
    else:
        return di


def handle_null_or_unknown_types(fn, di: dict) -> tuple[bool, bool]:
    if "anyOf" in di:
        return is_Nullable(fn, di)
    elif "allOf" in di:  # do something...
        logger.debug(
            f"allOf not properly implemented. it is flattened and re-evaluated.\nGiven : {str(di)}"
        )
        return fn(flatten_allOf(di))
    elif "oneOf" in di:
        logger.warning(f"oneOf not implemented \nGiven : {str(di)}")
        return False, False
    elif "not" in di:
        logger.warning(f"not not implemented \nGiven : {str(di)}")
        return False, False
    else:
        raise ValueError(
            f"of: anyOf, allOf, oneOf or not, only anyOf is supported. \n Given : {str(di)}"
        )


def is_anyof_widget(fn):
    return fn.__name__ == "is_AnyOf" or fn.__name__ == "is_Combobox"


def is_Nullable(fn: ty.Callable, di: dict) -> tuple[bool, bool]:
    # if not is_allowed_type(di):
    #     return False, False
    allow_none = "null" in [l.get("type") for l in di["anyOf"]]
    if not allow_none and not is_anyof_widget(fn):
        return False, allow_none
    else:
        non_null = [l for l in di["anyOf"] if l.get("type") != "null"]

        if len(non_null) == 1:
            di = {k: v for k, v in di.items() if k != "anyOf"}
            di = {**di, **non_null[0]}
            return fn(di, allow_none=allow_none, checked_nullable=True)
        else:
            di["anyOf"] = non_null
            if fn.__name__ == "is_AnyOf" or fn.__name__ == "is_Combobox":
                return fn(di, allow_none=allow_none, checked_nullable=True)
            return False, allow_none


def is_AnyOf(di: dict, allow_none=False, checked_nullable=False):
    """
    ```py
    from ipyautoui.automapschema import is_AnyOf

    print(is_AnyOf({'title': 'Int Text', "anyOf": [{'default': 1, 'type': 'integer'}, {"type": "string"}]}))
    #> (True, False)
    ```
    """
    if "anyOf" not in di:
        return False, allow_none
    if is_anyof_combobox(di):
        return False, allow_none
    if not checked_nullable:
        return is_Nullable(is_AnyOf, di)
    else:
        types = [l.get("type") for l in di["anyOf"]]
        if len(set(types)) > 1:
            return True, allow_none
        elif len(set(types)) == 1 and types[0] == "object":
            return True, allow_none
        else:
            logger.warning("anyOf with same types not implemented")
            return False, allow_none


def is_IntText(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_IntText

    is_IntText({'title': 'Int Text', 'default': 1, 'type': 'integer'})
    (True, False)
    is_IntText({'title': 'Int Text', 'default': 1, 'type': 'number'})
    (False, False)
    is_IntText({'title': 'floater', 'default': 1.33, 'type': 'number'})
    (False, False)
    is_IntText({'title': 'floater', 'default':1, 'anyOf': [{'type': 'integer'},{'type': 'null'}]})
    (True, True)
    ```
    """

    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_IntText, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "integer":
        return False, allow_none
    if "minimum" and "maximum" in di.keys():
        return False, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    return True, allow_none


def is_IntSlider(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_IntSlider

    print(is_IntSlider({'title': 'int', 'default': 1, 'type': 'number'}))
    #> (False, False)
    print(is_IntSlider({'title': 'int', 'default': 1, 'type': 'integer'}))
    #> (False, False)
    print(is_IntSlider({'title': 'int', 'default': 1, 'type': 'integer', "minimum": 0, "maximum": 3}))
    #> (True, False)
    print(is_IntSlider({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3}))
    #> (False, False)
    print(is_IntSlider({'title': 'int', 'default': 1, 'anyOf': [{'type': 'integer', "minimum": 0, "maximum": 3}, {'type': 'null'}]}))
    #> (True, True)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_IntSlider, di)
    t = di["type"]

    if "autoui" in di.keys():
        return False, allow_none
    if not t == "integer":
        return False, allow_none
    if "minimum" and "maximum" in di.keys():
        return True, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    return False, allow_none


def is_FloatText(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """

    ```py
    from ipyautoui.automapschema import is_FloatText

    print(is_FloatText({'title': 'floater', 'default': 1.33, 'type': 'number'}))
    #> (True, False)
    print(is_FloatText({'title': 'floater', 'default': 1, 'type': 'integer'}))
    #> (False, False)
    print(is_FloatText({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3}))
    #> (False, False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_FloatText, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "number":
        return False, allow_none
    if "minimum" and "maximum" in di.keys():
        return False, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    return True, allow_none


def is_FloatSlider(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_FloatSlider

    print(is_FloatSlider({'title': 'floater', 'default': 1.33, 'type': 'number'}))
    #> (False, False)
    print(is_FloatSlider({'title': 'floater', 'default': 1, 'type': 'integer'}))
    #> (False, False)
    print(is_FloatSlider({'title': 'floater', 'default': 1, 'type': 'integer', "minimum": 0, "maximum": 3}))
    #> (False, False)
    print(is_FloatSlider({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3}))
    #> (True, False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_FloatSlider, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "number":
        return False, allow_none
    if "minimum" and "maximum" not in di.keys():
        return False, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    return True, allow_none


def is_range(di, is_type="numeric"):
    """finds numeric range within schema properties. a range in json must satisfy these criteria:
    - check1: array length == 2
    - check2: minimum and maximum values must be given
    - check3: check numeric typ given (i.e. integer or number or numeric)
    """

    def get_type(di):
        t = di["prefixItems"][0]["type"]
        t1 = di["prefixItems"][0]["type"]
        if t != t1:
            raise ValueError("items are different types")
        else:
            return t

    if not "prefixItems" in di.keys():
        return False

    elif len(di["prefixItems"]) != 2:
        return False
    for i in di["prefixItems"]:
        if "minimum" not in i and "maximum" not in i:
            return False

    #  check3: check numeric typ given (i.e. integer or number or numeric)
    if is_type == "numeric":
        if not get_type(di) == "integer":
            if not get_type(di) == "number":
                return False
    elif is_type == "number":
        if not get_type(di) == "number":
            return False
    elif is_type == "integer":
        if not get_type(di) == "integer":
            return False
    else:
        raise ValueError('is_type must be one of: "integer", "number", "numeric"')
    return True


def is_IntRangeSlider(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    Example:
    ```py
    from ipyautoui.automapschema import is_IntRangeSlider
    di = {'default': [0, 3],
        'maxItems': 2,
        'minItems': 2,
        'prefixItems': [{'maximum': 4, 'minimum': 0, 'type': 'integer'},
            {'maximum': 4, 'minimum': 0, 'type': 'integer'}],
        'title': 'Int Range Slider',
        'type': 'array'}
    print(is_IntRangeSlider(di))
    #> (True, False)
    di["anyOf"] = [{"type": "array"}, {"type": "null"}]
    del di["type"]
    print(is_IntRangeSlider(di))
    #> (True, True)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_IntRangeSlider, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if t == "array" and is_range(di, is_type="integer"):
        return True, allow_none
    return False, allow_none


def is_FloatRangeSlider(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    Example:
    ```py
    from ipyautoui.automapschema import is_FloatRangeSlider
    di = {'default': [0.5, 3.4],
        'maxItems': 2,
        'minItems': 2,
        'prefixItems': [{'maximum': 4, 'minimum': 0, 'type': 'number'},
            {'maximum': 4, 'minimum': 0, 'type': 'number'}],
        'title': 'Float Range Slider',
        'type': 'array'}
    print(is_FloatRangeSlider(di))
    #> (True, False)
    di["anyOf"] = [{"type": "array"}, {"type": "null"}]
    del di["type"]
    print(is_FloatRangeSlider(di))
    #> (True, True)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_FloatRangeSlider, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if t == "array" and is_range(di, is_type="number"):
        return True, allow_none
    return False, allow_none


def is_Date(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_Date# , is_Text
    di = {"title": "Date Picker", "default": "2022-04-28", "type": "string", "format": "date"}
    is_Date(di)
    #> print(True)
    # is_Text(di)
    # #> print(False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Date, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "string":
        return False, allow_none
    if not "format" in di.keys():
        return False, allow_none
    if "format" in di.keys() and di["format"] != "date":
        return False, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    if di["format"] == "date":
        return True, allow_none  # <--------- TRUE
    else:
        return False, allow_none


def is_Datetime(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_Datetime, is_Date
    di = {"title": "Datetime Picker", "type": "string", "format": "date-time"}
    is_Datetime(di)
    #> print(True)
    is_Date(di)
    #> print(False)
    # is_Text(di)
    #> print(False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Datetime, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "string":
        return False, allow_none
    if not "format" in di.keys():
        return False, allow_none
    if "format" in di.keys() and di["format"] != "date-time":
        return False, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    if di["format"] == "date-time":
        return True, allow_none  # <--------- TRUE
    else:
        return False, allow_none


def is_Color(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]:
    """check if schema object is a color

    Args:
        di (dict): schema object

    Returns:
        bool: is the object a color

    Example:
        ```py
        from ipyautoui.automapschema import is_Color# , is_Text
        di = {"title": "Color Picker Ipywidgets", "default": "#f5f595","type": "string", "format": "hexcolor"}
        print(is_Color(di))
        #> (True, False)
        di = {"title": "Path", "default": ".", "type": "string", "format": "path"}
        print(is_Color(di))
        #> (False, False)
        ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Color, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "string":
        return False, allow_none
    if not "format" in di.keys():
        return False, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    if "format" in di.keys() and "color" in di["format"]:
        return True, allow_none
    else:
        return False, allow_none


def is_Path(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]:
    """check if schema object is a path

    Args:
        di (dict): schema object

    Returns:
        bool: is the object a color

    Example:
        ```py
        from ipyautoui.automapschema import is_Path
        di = {"title": "Path", "default": ".", "type": "string", "format": "path"}
        print(is_Path(di))
        #> (True, False)
        ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Path, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "string":
        return False, allow_none
    if not "format" in di.keys():
        return False, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    if "format" in di.keys() and di["format"] == "path":
        return True, allow_none
    else:
        return False, allow_none


def is_anyof_combobox(di: dict) -> bool:
    def get_enum(t):
        li = [_["enum"] for _ in t if "enum" in _.keys()]
        if len(li) == 0:
            return None
        else:
            return li[0]

    types = di["anyOf"]
    t = [l for l in types if l.get("type")]
    e = get_enum(t)
    if len(t) > 1 and e is not None:
        return True
    else:
        return False


def is_Combobox(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_Combobox
    di = {'anyOf': [{'enum': ['a', 'b'],
        'title': 'TestEnum',
        'type': 'string'},
        {'type': 'string'}],
    'default': 'a'}
    print(is_Combobox(di))
    #> (True, False)
    ```
    """
    if "autoui" in di.keys():
        return False, allow_none
    if "examples" in di.keys():
        return True, allow_none
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Combobox, di)
    if "type" not in di.keys() and checked_nullable:
        return is_anyof_combobox(di), allow_none
    else:
        return False, allow_none


def is_Dropdown(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_Dropdown
    di = {"title": "Dropdown", "enum": [1,2], "type": "integer"}
    print(is_Dropdown(di))
    #> (True, False)
    di = {"title": "Dropdown", "enum": [1,2], "anyOf":[ {"type": "integer"}, {"type": "null"}]}
    print(is_Dropdown(di))
    #> (True, True)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Dropdown, di)
    if "autoui" in di.keys():
        return False, allow_none
    if "enum" in di.keys() and "examples" not in di.keys():
        return True, allow_none
    else:
        return False, allow_none


def is_Markdown(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_Markdown
    di = {'title': 'Markdown', 'type': 'string', 'format': 'markdown'}
    print(is_Markdown(di))
    #> (True, False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Markdown, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "string":
        return False, allow_none
    if not "format" in di.keys():
        return False, allow_none
    if "format" in di.keys() and "markdown" == di["format"]:
        return True, allow_none
    return False, allow_none


def isnot_Text(di: dict) -> bool:
    if is_Date(di)[0]:
        return True
    if is_Datetime(di)[0]:
        return True
    if is_Color(di)[0]:
        return True
    if is_Markdown(di)[0]:
        return True
    if is_Path(di)[0]:
        return True
    return False


def is_Text(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]:
    """check if schema object is a Text

    Args:
        di (dict): schema object

    Returns:
        bool: is the object a Text

    ```py
    from ipyautoui.automapschema import is_Text
    di = {"title": "Text", "default": "default string","type": "string"}
    print(is_Text(di))
    #> (True, False)
    di = {"title": "Text", "default": 210*"s", "type": "string", "maxLength":210}
    print(is_Text(di))
    #> (False, False)
    di = {"title": "Text", "default": 199*"s", "anyOf": [{"type":"string"}, {"type":"null"}]}
    print(is_Text(di))
    #> (True, True)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Text, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "string":
        return False, allow_none
    if "maxLength" in di.keys() and di["maxLength"] >= 200:
        return False, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    if isnot_Text(di):
        return False, allow_none
    else:
        return True, allow_none


def is_Textarea(
    di: dict, max_length=200, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """check if schema object is a is_Textarea

    Args:
        di (dict): schema object

    Returns:
        bool: is the object a is_Textarea

    ```py
    from ipyautoui.automapschema import is_Textarea
    di = {"title": "Text", "default": 210*"s", "type": "string", "maxLength":210}
    print(is_Textarea(di))
    #> (True, False)
    d = 210*"s"
    di = {"title": "Text",  "anyOf": [{"type":"string", "maxLength":210, "default": d}, {"type":"null"}]}
    print(is_Textarea(di))
    #> (True, True)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Textarea, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "string":
        return False, allow_none
    if "enum" in di.keys() or "examples" in di.keys():
        return False, allow_none
    if "maxLength" not in di.keys():
        return False, allow_none
    if "maxLength" in di.keys() and di["maxLength"] >= max_length:  # i.e. == long text
        return True, allow_none
    else:
        return False, allow_none


def is_enum_array(di: dict) -> (bool, int):
    is_enum = lambda di: True if "enum" in di.keys() else False

    if not "items" in di.keys():
        return False, 0
    if is_enum(di["items"]):
        return True, len(di["items"]["enum"])
    else:
        if "allOf" in di["items"]:
            di["items"] = flatten_allOf(di["items"])
            if is_enum(di["items"]):
                return True, len(di["items"]["enum"])
            else:
                return False, 0
        else:
            return False, 0


def is_select_multiple(di: dict) -> (bool, int):
    t = di["type"]
    if "autoui" in di.keys():
        return False, 0
    if t != "array":
        return False, 0
    if not "items" in di.keys():
        return False, 0
    return is_enum_array(di)


SELECT_MULTIPLE_MAX_ITEMS = 10


def is_SelectMultiple(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_SelectMultiple
    di = {"title": "SelectMultiple", "items": {"enum": [1,2]}, "type": "array"}
    print(is_SelectMultiple(di))
    #> (True, False)
    di = {"title": "SelectMultiple", "items": {"allOf":[{"enum": [1,2]}]}, "type": "array"}
    print(is_SelectMultiple(di))
    #> (True, False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_SelectMultiple, di)
    is_enum, enum_len = is_select_multiple(di)
    if not is_enum:
        return False, allow_none
    else:
        if enum_len < SELECT_MULTIPLE_MAX_ITEMS:
            return True, allow_none
        else:
            return False, allow_none


def is_TagsInput(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_TagsInput
    di = {"title": "TagsInput", "items": {"enum": [1,2]}, "type": "array"}
    print(is_TagsInput(di))
    #> (False, False)
    di = {"title": "TagsInput", "items": {"enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]}, "type": "array"}
    print(is_TagsInput(di))
    #> (True, False)
    di = {"title": "TagsInput", "items": {"allOf":[{"enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]}]}, "type": "array"}
    print(is_TagsInput(di))
    #> (True, False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_TagsInput, di)
    is_enum, enum_len = is_select_multiple(di)
    if not is_enum:
        return False, allow_none
    else:
        if enum_len >= SELECT_MULTIPLE_MAX_ITEMS:
            return True, allow_none
        else:
            return False, allow_none


def is_Checkbox(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_Checkbox
    di = {"title": "Checkbox", "type": "boolean"}
    print(is_Checkbox(di))
    #> (True, False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Checkbox, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if t != "boolean":
        return False, allow_none
    return True, allow_none


def is_AutoOveride(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_AutoOveride, di)
    if "autoui" not in di.keys():
        return False, allow_none
    return True, allow_none


def is_Object(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_Object
    di = {"title": "Checkbox", "type": "object"}
    print(is_Object(di))
    #> (True, False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Object, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "object":
        return False, allow_none
    return True, allow_none


def is_DataFrame(
    di: dict, allow_none=False, checked_nullable=False
) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_DataFrame
    di = {"title": "Checkbox", "type": "array", "format": "dataframe"}
    print(is_DataFrame(di))
    #> (True, False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_DataFrame, di)
    t = di["type"]
    if not t == "array":
        return False, allow_none
    if "format" in di.keys():
        if di["format"].lower() == "dataframe":
            return True, allow_none
        else:
            return False, allow_none
    else:
        return False, allow_none


def is_Array(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]:
    """
    ```py
    from ipyautoui.automapschema import is_Array
    di = {"title": "is_Array", "type": "array"}
    print(is_Array(di))
    #> (True, False)
    ```
    """
    if "type" not in di.keys() and not checked_nullable:
        return handle_null_or_unknown_types(is_Array, di)
    t = di["type"]
    if "autoui" in di.keys():
        return False, allow_none
    if not t == "array":
        return False, allow_none
    if is_range(di):
        return False, allow_none
    if is_enum_array(di)[0]:
        return False, allow_none  # as this is picked up from SelectMultiple
    if is_DataFrame(di, checked_nullable=checked_nullable)[0]:
        return False, allow_none
    return True, allow_none


def update_keys(di, map_keys=MAP_JSONSCHEMA_TO_IPYWIDGET):
    update_key = lambda key, map_keys: map_keys[key] if key in map_keys.keys() else key
    return {update_key(k, map_keys): v for k, v in di.items()}


def remove_title_and_description(di):
    return {k: v for k, v in di.items() if k != "description" and k != "title"}


def create_widget_caller(
    schema, calling=None, remove_title=True, map_keys=MAP_JSONSCHEMA_TO_IPYWIDGET
):
    """
    creates a "caller" object from the schema.
    this renames schema keys as follows to match ipywidgets:
        ```
        {
            'minimum': 'min',
            'maximum': 'max',
            'enum': 'options',
            'default': 'value',
            'description': 'autoui_description'
        }
        ```


    Args:
        schema: dict, json schema
        calling, default=None: the class that will be called by the
            returned "caller" object. if not None, args not present in the class
            are removed from "caller"

    Returns:
        caller: dict, object that is passed the "calling" widget
            initialised like ```calling(**caller)```

    """
    caller = update_keys(schema, map_keys=map_keys)
    if remove_title:
        caller = remove_title_and_description(caller)
    if calling is not None:
        caller = remove_non_present_kwargs(calling, caller)
    return caller


def tags_widget_caller(schema, calling=None, remove_title=True):
    map_keys = dict(MAP_JSONSCHEMA_TO_IPYWIDGET) | {"enum": "allowed_tags"}
    return create_widget_caller(
        schema, calling=calling, remove_title=remove_title, map_keys=map_keys
    )


def flatten_items(di: dict, fn=None) -> dict:
    di = {**di, **{k: v for k, v in di["items"].items() if k != "type"}}
    return {k: v for k, v in di.items() if k != "items"}


def flatten_type_and_nullable(di: dict, fn=None) -> dict:
    if "type" in di.keys():
        return {**di, **{"nullable": False}}
    else:
        if "anyOf" in di.keys():
            kw = "anyOf"
        elif "allOf" in di.keys():
            kw = "allOf"
        else:
            raise ValueError("currently must have anyOf or allOf or type in schema")
        types = di[kw]
        is_nullable = "null" in [l.get("type") for l in types]
        types_non_null = [
            l for l in types if l.get("type") != "null"
        ]  # get non-null types

        def get_enum(types_non_null):
            li = [_["enum"] for _ in types_non_null if "enum" in _.keys()]
            if len(li) == 0:
                return None
            else:
                return li[0]

        enum = get_enum(types_non_null)
        if len(types_non_null) > 1 and enum is not None:
            di["examples"] = enum
        for _ in types_non_null:
            di = {**_, **di}
        del di[kw]
        return {**di, **{"nullable": is_nullable}}


def add_schema_key(di: dict, wi=None) -> dict:
    return {"schema": di}


def add_max_layout(di: dict, wi=None) -> dict:
    return di | {"layout": {"width": "100%"}}


class WidgetMapper(BaseModel):
    """defines a filter function and associated widget. the "fn_filt" is used to search the
    json schema to find appropriate objects, the objects are then passed to the "widget" for the ui
    """

    fn_filt: ty.Callable
    li_fn_modify: list[ty.Callable[[dict, ty.Callable], dict]] = [
        flatten_type_and_nullable,
        create_widget_caller,
    ]
    widget: ty.Callable


class WidgetCaller(BaseModel):
    schema_: ty.Dict
    autoui: ty.Callable  # TODO: change name autoui --> widget?
    allow_none: bool = False
    args: ty.List = Field(default_factory=lambda: [])
    kwargs: ty.Dict = Field(default_factory=lambda: {})
    kwargs_box: ty.Dict = Field(default_factory=lambda: {})


def widgetcaller(caller: WidgetCaller, show_errors=True):
    """
    returns widget from widget caller object
    Args:
        caller: WidgetCaller
    Returns:
        widget of some kind
    """
    try:
        # if "nullable" in caller.schema_.keys() and caller.schema_["nullable"]:
        if caller.allow_none:
            fn = nullable(caller.autoui)
        else:
            fn = caller.autoui
        wi = fn(**caller.kwargs)
    except Exception as e:
        if show_errors:
            from ipyautoui.custom.widgetcaller_error import WidgetCallerError
            import traceback

            e = str(e) + "\n" + traceback.format_exc()
            wi = WidgetCallerError(
                widget=str(caller.autoui), schema=caller.schema_, error=str(e)
            )
        else:
            return  # TODO: check this works
    return wi


def update_widgets_map(widgets_map, di_update=None):
    """update the widget mapper frozen object

    Args:
        widgets_map (dict of WidgetMappers): _description_
        di_update (_type_, optional): _description_. Defaults to None.
    """
    if di_update is not None:
        with widgets_map.mutate() as mm:
            for k, v in di_update.items():
                mm.set(k, v)
            _ = mm.finish()
        del widgets_map
    else:
        _ = widgets_map
    return _


def get_range_min_and_max(schema, call=None):
    schema["min"] = schema["prefixItems"][0]["minimum"]
    schema["max"] = schema["prefixItems"][0]["maximum"]
    return schema


def dropdown_drop_null_value(kwargs, call=None):
    if (
        "value" in kwargs.keys()
        and kwargs["value"] is None
        and None not in kwargs["options"]
    ):
        del kwargs["value"]
    return kwargs


class AutoPlaceholder(w.Textarea):
    def __init__(self, **kwargs):
        txt = f"""
PLACEHOLDER WIDGET
schema:
{str(**kwargs)}
"""
        super().__init__(value=txt)


from ipyautoui.autoanyof import AnyOf


def get_containers_map(di_update=None):
    from ipyautoui.custom.iterable import AutoArray
    from ipyautoui.autoobject import AutoObject
    from ipyautoui.custom.editgrid import EditGrid

    CONTAINERS_MAP = frozenmap(
        **{
            "object": WidgetMapper(fn_filt=is_Object, widget=AutoObject),
            "array": WidgetMapper(
                fn_filt=is_Array,
                widget=AutoArray,
                li_fn_modify=[flatten_type_and_nullable],
            ),
            "dataframe": WidgetMapper(
                fn_filt=is_DataFrame,
                widget=EditGrid,
                li_fn_modify=[add_schema_key, add_max_layout],
            ),
        }
    )
    if di_update is None:
        di_update = {}
    return update_widgets_map(CONTAINERS_MAP, di_update=di_update)


def get_widgets_map(di_update=None):
    WIDGETS_MAP = frozenmap(
        **{
            "AutoOveride": WidgetMapper(
                fn_filt=is_AutoOveride,
                widget=AutoPlaceholder,
            ),
            "IntText": WidgetMapper(
                fn_filt=is_IntText,
                widget=w.IntText,
            ),
            "IntSlider": WidgetMapper(
                fn_filt=is_IntSlider,
                widget=w.IntSlider,
            ),
            "FloatText": WidgetMapper(
                fn_filt=is_FloatText,
                widget=w.FloatText,
            ),
            "FloatSlider": WidgetMapper(
                fn_filt=is_FloatSlider,
                widget=w.FloatSlider,
            ),
            "IntRangeSlider": WidgetMapper(
                fn_filt=is_IntRangeSlider,
                widget=w.IntRangeSlider,
                li_fn_modify=[
                    get_range_min_and_max,
                    flatten_type_and_nullable,
                    create_widget_caller,
                ],
            ),
            "FloatRangeSlider": WidgetMapper(
                fn_filt=is_FloatRangeSlider,
                widget=w.FloatRangeSlider,
                li_fn_modify=[
                    get_range_min_and_max,
                    flatten_type_and_nullable,
                    create_widget_caller,
                ],
            ),
            "Text": WidgetMapper(
                fn_filt=is_Text,
                widget=w.Text,
            ),
            "Textarea": WidgetMapper(
                fn_filt=is_Textarea,
                widget=w.Textarea,
            ),
            "Markdown": WidgetMapper(
                fn_filt=is_Markdown,
                widget=MarkdownWidget,
            ),
            "Dropdown": WidgetMapper(
                fn_filt=is_Dropdown,
                widget=w.Dropdown,
                li_fn_modify=[
                    flatten_type_and_nullable,
                    create_widget_caller,
                    dropdown_drop_null_value,
                ],
            ),
            "Combobox": WidgetMapper(
                fn_filt=is_Combobox,
                widget=w.Combobox,
            ),
            "SelectMultiple": WidgetMapper(
                fn_filt=is_SelectMultiple,
                widget=w.SelectMultiple,
                li_fn_modify=[
                    flatten_type_and_nullable,
                    flatten_items,
                    create_widget_caller,
                    dropdown_drop_null_value,
                ],
            ),
            "TagsInput": WidgetMapper(
                fn_filt=is_TagsInput,
                widget=w.TagsInput,
                li_fn_modify=[
                    flatten_type_and_nullable,
                    flatten_items,
                    tags_widget_caller,
                    dropdown_drop_null_value,
                ],
            ),
            "Color": WidgetMapper(
                fn_filt=is_Color,
                widget=w.ColorPicker,
            ),
            "Path": WidgetMapper(
                fn_filt=is_Path,
                widget=FileChooser,
            ),
            "Checkbox": WidgetMapper(
                fn_filt=is_Checkbox,
                widget=w.Checkbox,
            ),
            "Date": WidgetMapper(fn_filt=is_Date, widget=DatePickerString),
            "Datetime": WidgetMapper(
                fn_filt=is_Datetime, widget=NaiveDatetimePickerString
            ),
            "anyOf": WidgetMapper(
                fn_filt=is_AnyOf,
                widget=AnyOf,
                li_fn_modify=[create_widget_caller],
            ),
        }
        | dict(get_containers_map())
    )

    if di_update is None:
        di_update = {}
    return update_widgets_map(WIDGETS_MAP, di_update=di_update)


def get_autooveride(schema):
    aui = schema["autoui"]
    if type(aui) == str:
        cl = obj_from_importstr(aui)
    else:
        cl = aui
    return cl


def map_widget(
    di: dict, widgets_map: frozenmap = None, fail_on_error: bool = False
) -> WidgetCaller:
    """
    map_widget maps a json schema to a widget. it uses the widgets_map to find the correct widget.
    Example:
    ```py
    from ipyautoui.automapschema import is_FloatText
    print(is_FloatText({'title': 'floater', 'default': 1.33, 'type': 'number'}))
    #> (True, False)
    print(is_FloatText({'title': 'floater', 'default': 1, 'type': 'integer'}))
    #> (False, False)
    print(is_FloatText({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3}))
    #> (False, False)
    ```
    """

    if widgets_map is None:
        widgets_map = get_widgets_map()

    def get_widget(di, k, widgets_map):
        if k == "AutoOveride":
            return get_autooveride(di)
        else:
            return widgets_map[k].widget

    mapped = []
    # loop through widgets_map to find a correct mapping...
    for widget_name, v in widgets_map.items():
        check, allow_none = v.fn_filt(di)
        if check:
            mapped.append((widget_name, allow_none))

    if len(mapped) == 0:
        if fail_on_error:
            raise ValueError(f"widget map not found for: {di}")
        else:
            return WidgetCaller(schema_=di, autoui=AutoPlaceholder)
    elif len(mapped) == 1:
        # ONLY THIS ONE SHOULD HAPPEN
        widget_name, allow_none = mapped[0]
        wi = get_widget(di, widget_name, widgets_map)
        kwargs = di
        for x in widgets_map[widget_name].li_fn_modify:
            kwargs = x(kwargs, wi)

        kwargs_box = flatten_type_and_nullable(di)
        # TODO: ^ probs a more efficient way to do this to avoid repetition with above
        #          as `flatten_type_and_nullable` is typically in `li_fn_modify`
        kwargs_box = update_keys(kwargs_box)
        kwargs_box = remove_non_present_kwargs(AutoBox, kwargs_box)
        return WidgetCaller(
            schema_=di,
            autoui=wi,
            allow_none=allow_none,
            kwargs=kwargs,
            kwargs_box=kwargs_box,
        )
    else:
        s = str(mapped)
        e = f"multiple matches found. . using the last one. {di}. \n  {s}"
        if fail_on_error:
            raise ValueError(e)
        else:
            print(e)
            print(mapped)
            widget_name, allow_none = mapped[-1]
            wi = get_widget(di, widget_name, widgets_map)
            return WidgetCaller(schema_=di, autoui=wi, allow_none=allow_none)


def get_widget(di, **kwargs):
    di = di | kwargs
    caller = map_widget(di)
    return widgetcaller(caller)  # TODO: add passing of value


def from_schema_method(
    cls, schema: ty.Union[ty.Type[BaseModel], dict], value: ty.Optional[dict] = None
):
    if "$defs" in schema.keys():
        try:
            schema = replace_refs(schema, merge_props=True)
        except ValueError as e:
            logger.warning(f"replace_refs error: \n{e}")
            pass
    ui = cls(**schema)
    ui.model = None
    return ui


def from_model_method(cls, model: ty.Type[BaseModel], value: ty.Optional[dict] = None):
    schema = replace_refs(model.model_json_schema(), merge_props=True)
    if value is not None:
        schema["value"] = value
    ui = cls(**schema)
    ui.model = model
    return ui


if __name__ == "__main__":
    di = {
        "title": "int",
        "default": 3,
        "anyOf": [{"type": "integer"}, {"type": "null"}],
    }
    caller = map_widget(di)
    assert "IntText" in str(caller.autoui)
    print(caller)
