# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# %run __init__.py
# %load_ext lab_black
import typing
from pydantic import BaseModel, Field
from ipywidgets import widgets
import ipywidgets as widgets
import ipyautoui.autowidgets as auiwidgets
from ipyautoui._utils import frozenmap, obj_from_importstr

# +
#  -- ATTACH DEFINITIONS TO PROPERTIES ----------------------
def recursive_search_schema(sch: typing.Dict, li: typing.List) -> typing.Dict:
    """searches down schema tree to retrieve definitions

    Args:
        sch (typing.Dict): json schema made from pydantic
        li (typing.List): list of keys to search down tree

    Returns:
        typing.Dict: definition retrieved from schema
    """
    f = li[0]
    if len(li) > 1:
        li_tmp = li[1:]
        sch_tmp = sch[f]
        return recursive_search_schema(sch_tmp, li_tmp)
    else:
        return sch[f]


def attach_schema_refs(schema, schema_base=None):
    """
    attachs #definitions to $refs within the main schema
    recursive function. schema_base is constant as is used for retrieving definitions.
    schema is recursively edited.

    Args:
        schema (dict): json schema
        schema_base (dict): same as above but isn't recursively searched. leave blank
            and it defaults to schema

    Returns:
        schema (dict): with $refs removed and replaced with #defintions

    """
    if schema_base is None:
        schema_base = schema
    if type(schema) == list:
        for n, s in enumerate(schema):
            schema[n] = attach_schema_refs(s, schema_base=schema_base)
    elif type(schema) == dict:
        for k, v in schema.items():
            if type(v) == dict:
                if "$ref" in v:
                    li_filt = v["$ref"].split("/")[1:]
                    schema[k] = recursive_search_schema(schema_base, li_filt)
                else:
                    schema[k] = attach_schema_refs(v, schema_base=schema_base)
            elif type(v) == list:
                schema[k] = attach_schema_refs(v, schema_base=schema_base)
            else:
                pass
    else:
        pass
    return schema


#  ----------------------------------------------------------
# -


# +
# IntText
# IntSlider
# FloatText
# FloatSlider
# Text
# Textarea
# Dropdown
# SelectMultiple
# Checkbox
# autooveride


def is_IntText(di: dict) -> bool:
    """

    Example:
        >>> is_IntText({'title': 'Int Text', 'default': 1, 'type': 'integer'})
        True
        >>> is_IntText({'title': 'Int Text', 'default': 1, 'type': 'number'})
        False
        >>> is_IntText({'title': 'floater', 'default': 1.33, 'type': 'number'})
        False
    """
    if "autoui" in di.keys():
        return False
    if not di["type"] == "integer":
        return False
    if "minimum" and "maximum" in di.keys():
        return False
    return True


def is_IntSlider(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if not di["type"] == "integer":
        return False
    if "minimum" and "maximum" not in di.keys():
        return False
    return True


def is_FloatText(di: dict) -> bool:
    """
    Example:
        >>> is_FloatText({'title': 'floater', 'default': 1.33, 'type': 'number'})
        True
    """
    if "autoui" in di.keys():
        return False
    if not di["type"] == "number":
        return False
    if "minimum" and "maximum" in di.keys():
        return False
    return True


def is_FloatSlider(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if not di["type"] == "number":
        return False
    if "minimum" and "maximum" not in di.keys():
        return False
    return True


def is_range(di, is_type="numeric"):
    """finds numeric range within schema properties. a range in json must satisfy these criteria:
    - check1: array length == 2
    - check2: minimum and maximum values must be given
    - check3: check numeric typ given (i.e. integer or number or numeric)
    """

    def get_type(di):
        t = di["items"][0]["type"]
        t1 = di["items"][0]["type"]
        if t != t1:
            raise ValueError("items are different types")
        else:
            return t

    if di["type"] != "array":
        return False
    if not "items" in di.keys() and len(di["items"]) != 2:
        return False
    for i in di["items"]:
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


def is_IntRangeSlider(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if not is_range(di, is_type="integer"):
        return False
    return True


def is_FloatRangeSlider(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if not is_range(di, is_type="number"):
        return False
    return True


def is_Date(di: dict) -> bool:
    """
    Example:
        >>> di = {"title": "Date Picker", "default": "2022-04-28", "type": "string", "format": "date"}
        >>> is_Date(di)
        True
        >>> di = {"title": "Date Picker", "default": "2022-04-28", "type": "string", "format": "date"}
        >>> is_Text(di)
        False
    """
    if "autoui" in di.keys():
        return False
    if not di["type"] == "string":
        return False
    if not "format" in di.keys():
        return False
    if "format" in di.keys() and di["format"] != "date":
        return False
    return True


def is_Color(di: dict) -> bool:
    """check if schema object is a color

    Args:
        di (dict): schema object

    Returns:
        bool: is the object a color

    Example:
        >>> di = {"title": "Color Picker Ipywidgets", "default": "#f5f595","type": "string", "format": "hexcolor"}
        >>> is_Color(di)
        True
    """
    if "autoui" in di.keys():
        return False
    if not di["type"] == "string":
        return False
    if not "format" in di.keys():
        return False
    if "format" in di.keys() and "color" not in di["format"]:
        return False
    return True


def is_Text(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if not di["type"] == "string":
        return False
    if "enum" in di.keys():
        return False
    if "maxLength" in di.keys() and di["maxLength"] >= 200:
        return False
    if is_Date(di):
        return False
    if is_Color(di):
        return False
    if is_Markdown(di):
        return False
    return True


def is_Textarea(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if not di["type"] == "string":
        return False
    if "enum" in di.keys():
        return False
    if "maxLength" not in di.keys():
        return False
    if "maxLength" in di.keys() and di["maxLength"] <= 200:  # i.e. == long text
        return False
    if is_Date(di):
        return False
    if is_Color(di):
        return False
    if is_Markdown(di):
        return False
    return True


def is_Markdown(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if not di["type"] == "string":
        return False
    if not "format" in di.keys():
        return False
    if "format" in di.keys() and "markdown" != di["format"]:
        return False
    if is_Date(di):
        return False
    if is_Color(di):
        return False
    return True


def is_Dropdown(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if "enum" not in di.keys():
        return False
    if di["type"] == "array":
        return False
    return True


def is_SelectMultiple(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if "enum" not in di.keys():
        return False
    if di["type"] != "array":
        return False
    return True


def is_Checkbox(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if di["type"] != "boolean":
        return False
    return True


def is_AutoOveride(di: dict) -> bool:
    if "autoui" not in di.keys():
        return False
    return True


def is_Object(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if not di["type"] == "object":
        return False
    return True


def is_Array(di: dict) -> bool:
    if "autoui" in di.keys():
        return False
    if not di["type"] == "array":
        return False
    if is_range(di):
        return False
    if "enum" in di.keys():
        return False  # as this is picked up from SelectMultiple
    if is_DataFrame(di):
        return False
    return True


def is_DataFrame(di: dict) -> bool:
    if "format" in di.keys():
        if di["format"].lower() == "dataframe":
            return True
        else:
            return False
    else:
        return False


class WidgetMapper(BaseModel):
    """defines a filter function and associated widget. the "fn_filt" is used to search the
    json schema to find appropriate objects, the objects are then passed to the "widget" for the ui
    """

    fn_filt: typing.Callable
    widget: typing.Callable


class WidgetCaller(BaseModel):
    schema_: typing.Dict
    autoui: typing.Callable  # TODO: change name autoui --> widget?
    args: typing.List = Field(default_factory=lambda: [])
    kwargs: typing.Dict = Field(default_factory=lambda: {})


def widgetcaller(caller: WidgetCaller, show_errors=True):
    """
    returns widget from widget caller object
    Args:
        caller: WidgetCaller
    Returns:
        widget of some kind
    """
    try:
        # args = inspect.getfullargspec(cl).args
        # kw = {k_: v_ for k_, v_ in v.items() if k_ in args}
        # ^ do this if required (get allowed args from class)

        w = caller.autoui(caller.schema_, *caller.args, **caller.kwargs)

    except:
        if show_errors:
            txt = f"""
ERROR: widgetcaller
-----
widget:
{str(caller.autoui)}

schema: 
{str(caller.schema_)}
"""
            # TODO: add logging
            w = widgets.Textarea(txt)
        else:
            return  # TODO: check this works
    return w


MAP_WIDGETS = frozenmap(
    **{
        "AutoOveride": WidgetMapper(
            fn_filt=is_AutoOveride,
            widget=auiwidgets.AutoPlaceholder,  # auiwidgets.autooveride
        ),
        "IntText": WidgetMapper(fn_filt=is_IntText, widget=auiwidgets.IntText),
        "IntSlider": WidgetMapper(fn_filt=is_IntSlider, widget=auiwidgets.IntSlider),
        "FloatText": WidgetMapper(fn_filt=is_FloatText, widget=auiwidgets.IntText),
        "FloatSlider": WidgetMapper(
            fn_filt=is_FloatSlider, widget=auiwidgets.IntSlider
        ),
        "IntRangeSlider": WidgetMapper(
            fn_filt=is_IntRangeSlider, widget=auiwidgets.IntRangeSlider
        ),
        "FloatRangeSlider": WidgetMapper(
            fn_filt=is_FloatRangeSlider, widget=auiwidgets.FloatRangeSlider
        ),
        "Text": WidgetMapper(fn_filt=is_Text, widget=auiwidgets.Text),
        "Textarea": WidgetMapper(fn_filt=is_Textarea, widget=auiwidgets.Textarea),
        "Markdown": WidgetMapper(fn_filt=is_Markdown, widget=auiwidgets.AutoMarkdown),
        "Dropdown": WidgetMapper(fn_filt=is_Dropdown, widget=auiwidgets.Dropdown),
        "SelectMultiple": WidgetMapper(
            fn_filt=is_SelectMultiple, widget=auiwidgets.SelectMultiple
        ),
        "Checkbox": WidgetMapper(fn_filt=is_Checkbox, widget=auiwidgets.Checkbox),
        "Date": WidgetMapper(fn_filt=is_Date, widget=auiwidgets.DatePickerString),
        "Color": WidgetMapper(fn_filt=is_Color, widget=auiwidgets.ColorPicker),
        "object": WidgetMapper(fn_filt=is_Object, widget=auiwidgets.AutoPlaceholder),
        "array": WidgetMapper(fn_filt=is_Array, widget=auiwidgets.AutoPlaceholder),
        "DataFrame": WidgetMapper(
            fn_filt=is_DataFrame, widget=auiwidgets.AutoPlaceholder
        ),
    }
)


def get_autooveride(schema):
    aui = schema["autoui"]
    if type(aui) == str:
        cl = obj_from_importstr(aui)
    else:
        cl = aui
    return cl


def map_widget(di, widget_map=MAP_WIDGETS, fail_on_error=False):
    def get_widget(di, k, widget_map):
        if k == "AutoOveride":
            return get_autooveride(di)
        else:
            return widget_map[k].widget

    mapped = []
    # loop through widget_map to find a correct mapping...
    for k, v in widget_map.items():
        if v.fn_filt(di):
            mapped.append(k)
    if len(mapped) == 0:
        if fail_on_error:
            # TODO: pass error or not..
            raise ValueError(f"widget map not found for: {di}")
        else:
            return WidgetCaller(schema_=di, autoui=auiwidgets.AutoPlaceholder)
    elif len(mapped) == 1:
        # ONLY THIS ONE SHOULD HAPPEN
        k = mapped[0]
        w = get_widget(di, k, widget_map)
        return WidgetCaller(schema_=di, autoui=w)
    else:
        # TODO: add logging. take last map
        print(f"{di['title']}. multiple matches found. using the last one.")
        print(mapped)
        k = mapped[-1]
        w = get_widget(di, k, widget_map)
        return WidgetCaller(schema_=di, autoui=w)


def automapschema(schema: dict, widget_map: frozenmap = MAP_WIDGETS) -> WidgetCaller:
    # By placing the import in this function we avoid a circular import.
    from ipyautoui.custom.iterable import AutoArray
    from ipyautoui.autoipywidget import AutoIpywidget
    from ipyautoui.custom.edit_grid import EditGrid

    with widget_map.mutate() as mm:
        mm.set("array", WidgetMapper(fn_filt=is_Array, widget=AutoArray))
        mm.set("DataFrame", WidgetMapper(fn_filt=is_DataFrame, widget=EditGrid))
        mm.set("object", WidgetMapper(fn_filt=is_Object, widget=AutoIpywidget))
        _ = mm.finish()
    del widget_map
    widget_map = _

    schema = attach_schema_refs(schema)
    if "type" not in schema.keys():
        raise ValueError('"type" is a required key in schema')
    if schema["type"] == "object":
        # loop through keys
        pr = schema["properties"]
        return {k: map_widget(v, widget_map=widget_map) for k, v in pr.items()}
    elif schema["type"] == "array":
        return map_widget(schema, widget_map=widget_map)  # TODO: check this
    else:
        return map_widget(schema, widget_map=widget_map)


def autowidget(schema, value=None):
    """interprets schema and returns appropriate widget"""
    caller = automapschema(schema)
    if value is not None:
        caller["value"] = value
    if type(caller) == WidgetCaller:
        # print("type(caller) == WidgetCaller")
        return widgetcaller(caller)
    elif type(caller) == dict:
        # print("type(caller) == dict")
        return {k: widgetcaller(v) for k, v in caller.items()}
    else:
        raise ValueError("adsf")


def autowidgetcaller(schema, value=None):
    """interprets schema and returns appropriate widget"""
    from ipyautoui.custom.iterable import AutoArray
    from ipyautoui.autoipywidget import AutoIpywidget

    t = schema["type"]
    if t == "object":
        return AutoIpywidget(schema, value=value)
    elif t == "array":
        return AutoArray(schema, value=value)
    else:
        return autowidget(schema, value=value)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
