# +
from typing import Optional, List, Literal
from datetime import date, datetime, time, timedelta
from enum import Enum
from pydantic import BaseModel, Field, RootModel, ConfigDict,conint, constr
from ipyautoui.custom.edittsv import EditTsvWithDiff


class MyColor(str, Enum):
    red = 'red'
    green = 'green'
    blue = 'blue'


class Test(BaseModel):
    a_int: Optional[int] = Field(
        None,
        alias='a_int',
        description='Simple integer value',
        title='A Int',
        json_schema_extra=dict(section="numeric"),
    )
    a_constrainedint: Optional[conint(ge=0, le=100)] = Field(
        None,
        alias='a_constrainedint',
        description='Integer constrained between 0 and 100',
        title='A Constrained Int',
        json_schema_extra=dict(section="numeric"),
    )
    b_float: Optional[float] = Field(
        None,
        alias='b_float',
        description='Floating point number',
        title='B Float',
        json_schema_extra=dict(section="numeric"),
    )
    c_str: Optional[str] = Field(
        None,
        alias='c_str',
        description='Basic string field',
        title='C Str',
        json_schema_extra=dict(section="unicode"),
    )
    c_constrainedstr: Optional[constr(min_length=1, max_length=50)] = Field(
        None,
        alias='c_constrainedstr',
        description='String constrained to length 1–50',
        title='C Constrained Str',
        json_schema_extra=dict(section="unicode"),
    )
    d_enum: Optional[Literal["red", "green", "blue"]] = Field(
        None,
        alias='d_enum',
        description='String value that must be one of: "red", "green", or "blue"',
        title='D Enum',
        json_schema_extra=dict(section="unicode"),
    )
    e_bool: Optional[bool] = Field(
        None,
        alias='e_bool',
        description='Boolean value (True/False)',
        title='E Bool',
        json_schema_extra=dict(section="boolean"),
    )
    f_date: Optional[date] = Field(
        None,
        alias='f_date',
        description='Date value (YYYY-MM-DD)',
        title='F Date',
        json_schema_extra=dict(section="datetime"),
    )
    g_datetime: Optional[datetime] = Field(
        None,
        alias='g_datetime',
        description='Datetime value (ISO format)',
        title='G Datetime',
        json_schema_extra=dict(section="datetime"),
    )
    h_time: Optional[time] = Field(
        None,
        alias='h_time',
        description='Time of day (HH:MM:SS)',
        title='H Time',
        json_schema_extra=dict(section="datetime"),
    )
    i_duration: Optional[timedelta] = Field(
        None,
        alias='i_duration',
        description='Time duration value',
        title='I Duration',
        json_schema_extra=dict(section="datetime"),
    )


class TestArray(RootModel):
    model_config = ConfigDict(
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"),
        )
    )
    root: List[Test]



# -

if __name__ == "__main__":    
    edit_tsv_w_diff = EditTsvWithDiff(model=TestArray, transposed = False, primary_key_name="a_int", header_depth=3, exclude_metadata=False, exclude_header_lines=False)
    display(edit_tsv_w_diff)


if __name__ == "__main__":
    display(edit_tsv_w_diff.value)
    display(edit_tsv_w_diff.text.value)
    print("DDIFF:")
    display(edit_tsv_w_diff.ddiff)




