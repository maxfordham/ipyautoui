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
import typing as ty
from pydantic import BaseModel, Field
import ipywidgets as w
import ipyautoui.autowidgets as auiwidgets
from ipyautoui._utils import frozenmap, obj_from_importstr

# +
#  -- ATTACH DEFINITIONS TO PROPERTIES ----------------------
def recursive_search_schema(schema: ty.Dict, li: ty.List) -> ty.Dict:
    """searches down schema tree to retrieve definitions

    Args:
        schema (ty.Dict): json schema made from pydantic
        li (ty.List): list of keys to search down tree

    Returns:
        ty.Dict: definition retrieved from schema
    """
    f = li[0]
    if len(li) > 1:
        li_tmp = li[1:]
        sch_tmp = schema[f]
        return recursive_search_schema(sch_tmp, li_tmp)
    else:
        return schema[f]


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
        schema_base = schema.copy()
    try:
        schema = schema.copy()
    except:
        pass
    # ^ copying to avoid pydantic schema being modified "in-place"
    if type(schema) == list:
        for n, s in enumerate(schema):
            schema[n] = attach_schema_refs(s, schema_base=schema_base)
    elif type(schema) == dict:
        for k, v in schema.items():
            if type(v) == dict:
                if "$ref" in v:
                    # FIXME: Needing refactor or cleanup -@jovyan at 8/31/2022, 12:24:09 AM
                    # refs are only attached to schema values, meaning that root definitions
                    # are ignored.
                    li_filt = v["$ref"].split("/")[1:]
                    schema[k] = recursive_search_schema(schema_base, li_filt)
                elif (
                    "allOf" in v
                    and len(v["allOf"]) == 1
                    and "$ref" in v["allOf"][0].keys()
                ):
                    # ^ this is an edge case for setting enums with Field values
                    #   (probs unique to how pydantic does it)
                    li_filt = v["allOf"][0]["$ref"].split("/")[1:]
                    ref = recursive_search_schema(schema_base, li_filt)
                    schema[k] = {
                        k_: v_
                        for k_, v_ in ref.items()
                        if k_ not in list(schema[k].keys())
                    } | schema[k]
                    del schema[k]["allOf"]
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
    """
    Example:
        >>> is_IntSlider({'title': 'int', 'default': 1, 'type': 'number'})
        False
        >>> is_IntSlider({'title': 'int', 'default': 1, 'type': 'integer'})
        False
        >>> is_IntSlider({'title': 'int', 'default': 1, 'type': 'integer', "minimum": 0, "maximum": 3})
        True
        >>> is_IntSlider({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3})
        False
    """
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
        >>> is_FloatText({'title': 'floater', 'default': 1, 'type': 'integer'})
        False
        >>> is_FloatText({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3})
        False
    """
    if "autoui" in di.keys():
        return False
    if not di["type"] == "number":
        return False
    if "minimum" and "maximum" in di.keys():
        return False
    return True


def is_FloatSlider(di: dict) -> bool:
    """
    Example:
        >>> is_FloatSlider({'title': 'floater', 'default': 1.33, 'type': 'number'})
        False
        >>> is_FloatSlider({'title': 'floater', 'default': 1, 'type': 'integer'})
        False
        >>> is_FloatSlider({'title': 'floater', 'default': 1, 'type': 'integer', "minimum": 0, "maximum": 3})
        False
        >>> is_FloatSlider({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3})
        True
    """
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
    """check if schema object is a Text

    Args:
        di (dict): schema object

    Returns:
        bool: is the object a Text

    Example:
        >>> di = {"title": "Text", "default": "default string","type": "string"}
        >>> is_Text(di)
        True

        >>> di = {"title": "Text", "default": 210*"s", "type": "string", "maxLength":210}
        >>> is_Text(di)
        False
    """
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


def is_Textarea(di: dict, max_length=200) -> bool:
    """check if schema object is a is_Textarea

    Args:
        di (dict): schema object

    Returns:
        bool: is the object a is_Textarea

    Example:
        >>> di = {"title": "Text", "default": 210*"s", "type": "string", "maxLength":210}
        >>> is_Textarea(di)
        True
    """
    if "autoui" in di.keys():
        return False
    if not di["type"] == "string":
        return False
    if "enum" in di.keys():
        return False
    if "maxLength" not in di.keys():
        return False
    if "maxLength" in di.keys() and di["maxLength"] <= max_length:  # i.e. == long text
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

    fn_filt: ty.Callable
    widget: ty.Callable


class WidgetCaller(BaseModel):
    schema_: ty.Dict
    autoui: ty.Callable  # TODO: change name autoui --> widget?
    args: ty.List = Field(default_factory=lambda: [])
    kwargs: ty.Dict = Field(default_factory=lambda: {})


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
            w = w.Textarea(txt)
        else:
            return  # TODO: check this works
    return w


def update_widgets_map(widgets_map, di_update=None):
    """update the widget mapper frozen object

    Args:
        widgets_map (dict of WidgetMappers): _description_
        di_update (_type_, optional): _description_. Defaults to None.
    """

    with widgets_map.mutate() as mm:
        for k, v in di_update.items():
            mm.set(k, v)
        _ = mm.finish()
    del widgets_map
    return _


def widgets_map(di_update=None):

    WIDGETS_MAP = frozenmap(
        **{
            "AutoOveride": WidgetMapper(
                fn_filt=is_AutoOveride,
                widget=auiwidgets.AutoPlaceholder,
            ),
            "IntText": WidgetMapper(fn_filt=is_IntText, widget=auiwidgets.IntText),
            "IntSlider": WidgetMapper(
                fn_filt=is_IntSlider, widget=auiwidgets.IntSlider
            ),
            "FloatText": WidgetMapper(
                fn_filt=is_FloatText, widget=auiwidgets.FloatText
            ),
            "FloatSlider": WidgetMapper(
                fn_filt=is_FloatSlider, widget=auiwidgets.FloatSlider
            ),
            "IntRangeSlider": WidgetMapper(
                fn_filt=is_IntRangeSlider, widget=auiwidgets.IntRangeSlider
            ),
            "FloatRangeSlider": WidgetMapper(
                fn_filt=is_FloatRangeSlider, widget=auiwidgets.FloatRangeSlider
            ),
            "Text": WidgetMapper(fn_filt=is_Text, widget=auiwidgets.Text),
            "Textarea": WidgetMapper(fn_filt=is_Textarea, widget=auiwidgets.Textarea),
            "Markdown": WidgetMapper(
                fn_filt=is_Markdown, widget=auiwidgets.AutoMarkdown
            ),
            "Dropdown": WidgetMapper(fn_filt=is_Dropdown, widget=auiwidgets.Dropdown),
            "SelectMultiple": WidgetMapper(
                fn_filt=is_SelectMultiple, widget=auiwidgets.SelectMultiple
            ),
            "Checkbox": WidgetMapper(fn_filt=is_Checkbox, widget=auiwidgets.Checkbox),
            "Date": WidgetMapper(fn_filt=is_Date, widget=auiwidgets.DatePickerString),
            "Color": WidgetMapper(fn_filt=is_Color, widget=auiwidgets.ColorPicker),
            "object": WidgetMapper(
                fn_filt=is_Object, widget=auiwidgets.AutoPlaceholder
            ),
            "array": WidgetMapper(fn_filt=is_Array, widget=auiwidgets.AutoPlaceholder),
            "DataFrame": WidgetMapper(
                fn_filt=is_DataFrame, widget=auiwidgets.AutoPlaceholder
            ),
        }
    )
    from ipyautoui.custom.iterable import AutoArray
    from ipyautoui.autoipywidget import AutoObject  # Ipywidget
    from ipyautoui.custom.editgrid import EditGrid

    di_update_ = {
        "array": WidgetMapper(fn_filt=is_Array, widget=AutoArray),
        "DataFrame": WidgetMapper(fn_filt=is_DataFrame, widget=EditGrid),
        "object": WidgetMapper(fn_filt=is_Object, widget=AutoObject),
    }
    if di_update is not None:
        di_update = {**di_update_, **di_update}
    else:
        di_update = di_update_
    return update_widgets_map(WIDGETS_MAP, di_update=di_update)


def get_autooveride(schema):
    aui = schema["autoui"]
    if type(aui) == str:
        cl = obj_from_importstr(aui)
    else:
        cl = aui
    return cl


def map_widget(di, widgets_map=None, fail_on_error=False) -> WidgetCaller:
    if widgets_map is None:
        widgets_map = widgets_map()

    def get_widget(di, k, widgets_map):
        if k == "AutoOveride":
            return get_autooveride(di)
        else:
            return widgets_map[k].widget

    mapped = []
    # loop through widgets_map to find a correct mapping...
    for k, v in widgets_map.items():
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
        w = get_widget(di, k, widgets_map)
        return WidgetCaller(schema_=di, autoui=w)
    else:
        # TODO: add logging. take last map
        print(f"{di['title']}. multiple matches found. using the last one.")
        print(mapped)
        k = mapped[-1]
        w = get_widget(di, k, widgets_map)
        return WidgetCaller(schema_=di, autoui=w)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
