"""
An example schema definition that demonstrates the current capability of the AutoUi class
"""
import typing
from enum import Enum
from pydantic import BaseModel, Field, conint, constr, validator
from pydantic.color import Color
from datetime import datetime, date
import pathlib
import pandas as pd
from pathlib import PurePosixPath
from ipyautoui.custom import RunName


class Gender(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    not_given = "not_given"


class NestedObject(BaseModel):
    """description in docstring"""
    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: conint(ge=0, le=3) = 2
    int_text1: int = 1
    
class RecursiveNest(BaseModel):
    """description in RecursiveNest docstring"""
    string1: str = Field(default="adsf", description="a description about my string")
    int_slider1: conint(ge=0, le=3) = 2
    int_text1: int = 1
    nested: NestedObject = Field(default=None) # TODO: note - cannot give a description to nested objects. use object docstring.

# class NestedObjectVjsfStyled(BaseModel):
#     string1: str = Field(default="adsf", description="a description about my string")
#     int_slider1: conint(ge=0, le=3) = 2
#     int_text1: int = 1

class TestAutoLogicSimple(BaseModel):
    """this is a test UI form to demonstrate how pydantic class can be used to generate an ipywidget input form. 
    only simple datatypes used (i.e. not lists/arrays or objects)
    """

    string: str = Field(default="adsf", description="a description about my string")
    int_slider: conint(ge=0, le=3) = 2
    int_text: int = 1
    int_range_slider: tuple[int, int] = Field(default=(0, 3), ge=0, le=4)  # check
    float_slider: float = Field(default=2.2, ge=0, le=3)
    float_text: float = 2.2
    float_range_slider: tuple[float, float] = Field(default=(0, 2.2), ge=0, le=3.5)
    checkbox: bool = True
    dropdown: Gender = None
    dropdown_simple: str = Field(default="asd", enum=["asd", "asdf"])
    combobox: str = Field(
        default="asd",
        enum=["asd", "asdf"],
        autoui="ipyautoui.autowidgets.Combobox",
    )
    # selection_range_slider
    text: constr(min_length=0, max_length=20) = "short text"
    text_area: constr(min_length=0, max_length=800) = Field("long text " * 50,description='long text field')

    #file_chooser: pathlib.Path = pathlib.Path(".") # TODO: serialisation / parsing round trip not working...
    
class TestTypesWithComplexSerialisation(BaseModel):
    """all of these types need to be serialised to json and parsed back to objects upon reading..."""
    file_chooser: pathlib.Path = pathlib.Path(".") # TODO: serialisation / parsing round trip not working...
    date_picker: date = date.today() # TODO: serialisation / parsing round trip not working...
    datetime_picker: datetime = datetime.now() #TODO: update with ipywidgets-v8
    color_picker_ipywidgets: Color = "#f5f595"
    color_picker_vjsf: str = Field(
        default="#f5f595",
        format='hexcolor',
        description='a color. "format" field is required to make vjsf work')
    color_picker_vjsf_swatches: str = Field("#f5f595",
        format='hexcolor',
        description='a color. "format" field is required to make vjsf work',
        x_props={
            "showSwatches": True,
            "hideCanvas": True,
            "hideInputs": True,
            "hideModeSwitch": True
      }
    )
    
class TestAutoLogic(TestAutoLogicSimple):
    """this is a test UI form to demonstrate how pydantic class can be used to generate an ipywidget input form"""
    complex_serialisation: TestTypesWithComplexSerialisation = Field(default=None)
    select_multiple: typing.List[Gender] = Field(
        default=["male", "female"]
    )  # TODO: make this work. requires handling the "anyOf" JSON link
    select_multiple_simple: typing.List[str] = Field(
        default=["male", "female"], enum=["male", "female", "other", "not_given"]
    )
    select_multiple_search: typing.List[str] = Field(
        default=["male", "female"],
        enum=["male", "female", "other", "not_given"],
        autoui="ipyautoui.custom.multiselect_search.MultiSelectSearch",
    )
    array: typing.List[str] = Field(default=[], max_items=5)
    objects_array: typing.List[NestedObject] = Field(default=[], max_items=5)
    objects_array_styled: typing.List[NestedObject] = Field(
        default=[], 
        max_items=5, 
        x_itemTitle="titleProp", 
        x_options={"arrayItemCardProps": {"outlined": True}}
    )
    # file_upload # TODO: how best to implement this? could auto-save to another location...
    run_name: str = Field(
        default="000-lean-description",
        autoui="ipyautoui.custom.modelrun.RunName",
        zfill=3,
    )
    datagrid: str = Field(
        default=pd.DataFrame.from_dict({"test": [0, 1], "df": [1, 2]}).to_json(),
        format="DataFrame",
    )
    nested: NestedObject = Field(default=None)
    recursive_nest: RecursiveNest = Field(default=None)

    # @validator("color_picker")
    # def _color_picker(cls, v):
    #     return v.as_hex()
    # TODO: handle parsing to and from json

    class Config:
        json_encoders = {PurePosixPath: str}
        # arbitrary_types_allowed = True#
        
        
class TestObjects(BaseModel):
    string: str = Field(default="adsf", description="a description about my string")
    nested: NestedObject = Field(default=None)
    recursive_nest: RecursiveNest = Field(default=None)

    
class TestArrays(BaseModel):
    array_strings: typing.List[str] = Field(default=['f','d'], max_items=5, min_items=2)
    array_strings1: typing.List[str] = Field(default=[], max_length=5, min_length=2)
    array_objects: typing.List[NestedObject] = Field(default=[], max_items=5)
    array_mixed: typing.List[typing.Union[NestedObject, str]] = Field(default=[], max_items=5)
    objects_array_styled: typing.List[NestedObject] = Field(
        description='styled array, only works with AutoVuetify',
        default=[], 
        max_items=5, 
        x_itemTitle="titleProp", 
        x_options={"arrayItemCardProps": {"outlined": True}}
    )