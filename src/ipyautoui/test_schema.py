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
    male = 'male'
    female = 'female'
    other = 'other'
    not_given = 'not_given'
    
class NestedObject(BaseModel):
    string1: str = Field(default='adsf', description='a description about my string')
    int_slider1: conint(ge=0,le=3) =2
    int_text1: int = 1

class TestAutoLogic(BaseModel):
    """this is a test UI form to demonstrate how pydantic class can be used to generate an ipywidget input form"""
    string: str = Field(default='adsf', description='a description about my string')
    int_slider: conint(ge=0,le=3) =2
    int_text: int = 1
    int_range_slider: tuple[int,int] = Field(default=(0,3),ge=0,le=4)   # check
    float_slider: float = Field(default=2.2, ge=0,le=3) 
    float_text: float =2.2
    float_range_slider: tuple[float,float] = Field(default=(0,2.2), ge=0,le=3.5)
    checkbox: bool = True
    dropdown: Gender = None
    dropdown_simple: str = Field(default ='asd', enum=['asd','asdf'])
    combobox: str = Field(default ='asd', enum=['asd','asdf'], autoui="<class 'ipywidgets.widgets.widget_string.Combobox'>")
    # selection_range_slider
    select_multiple: typing.List[Gender] = Field(default =['male','female']) # TODO: make this work. requires handling the "anyOf" JSON link
    select_multiple_simple: typing.List[str] = Field(default =['male','female'], enum=['male','female', 'other', 'not_given'])
    text: constr(min_length=0, max_length=20) = 'short text'
    text_area: constr(min_length=0, max_length=800)  = 'long text ' * 50
    date_picker: date = date.today()
    datetime_picker: datetime = datetime.now()
    color_picker: Color = '#f5f595'
    file_chooser: pathlib.Path = pathlib.Path('.')
    array: typing.List[str] = Field(default=[], max_items=5)
    # file_upload # TODO: how best to implement this? could auto-save to another location...
    run_name: str = Field(default='000-lean-description', autoui="<class 'ipyautoui.custom.modelrun.RunName'>", zfill=3) 
    datagrid: str = Field(default=pd.DataFrame.from_dict({'test':[0,1],'df':[1,2]}).to_json(), format="DataFrame")
    nested: NestedObject = Field(default=None)
    
    @validator('color_picker')
    def _color_picker(cls, v):
        return v.as_hex()
    
    class Config:
        json_encoders = {PurePosixPath:  str}
        #arbitrary_types_allowed = True