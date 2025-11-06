# +
from typing import Optional, List, Literal
from datetime import date, datetime, time, timedelta
from enum import Enum
from pydantic import BaseModel, Field, RootModel, ConfigDict, StringConstraints, conint, constr
from ipyautoui.custom.edittsv import EditTsvWithDiff, EditTsvFileUpload
from ipyautoui.custom.fileupload import TempFileUploadProcessor
from typing_extensions import Annotated
import xlsxdatagrid as xdg
import pathlib
import ipywidgets as w


class MyColor(str, Enum):
    red = 'red'
    green = 'green'
    blue = 'blue'

class Test(BaseModel):
    a_constrainedint: Annotated[int, Field(ge=1, le=10)] = Field(
        3,
        title="A Constrainedint",
        json_schema_extra=dict(
            section="numeric",
        ),
    )

    a_int: Optional[int] = Field(
        1,
        title="A Int",
        json_schema_extra=dict(section="numeric"),
    )

    b_calcfloat: Optional[float] = Field(
        None,
        title="B Calcfloat",
        description="calc value",
        frozen=True,
        json_schema_extra=dict(section="numeric", formula="a_int * b_float"),
    )

    b_float: Optional[float] = Field(
        1.5,
        title="B Float",
        json_schema_extra=dict(section="numeric"),
    )

    c_constrainedstr: Annotated[str, StringConstraints(min_length=0, max_length=20)] = Field(
        "string",
        title="C Constrainedstr",
        json_schema_extra=dict(
            section="unicode",
        ),
    )

    c_str: Optional[str] = Field(
        "string",
        title="C Str",
        json_schema_extra=dict(section="unicode"),
    )

    d_enum: MyColor = Field(
        "red",
        title="D Enum",
        json_schema_extra=dict(
            section="unicode",
        ),
    )

    e_bool: Optional[bool] = Field(
        True,
        title="E Bool",
        json_schema_extra=dict(section="boolean"),
    )

    f_date: Optional[date] = Field(
        "2024-06-06",
        title="F Date",
        json_schema_extra=dict(section="datetime"),
    )

    g_datetime: Optional[datetime] = Field(
        "2024-06-06T10:42:54.822063",
        title="G Datetime",
        json_schema_extra=dict(section="datetime"),
    )

    h_time: Optional[time] = Field(
        "10:42:54.822257",
        title="H Time",
        json_schema_extra=dict(section="datetime"),
    )

    i_duration: Optional[timedelta] = Field(
        "PT2H33M3S",
        title="I Duration",
        json_schema_extra=dict(section="datetime"),
    )

    model_config = ConfigDict(
        title="Test",
        json_schema_extra=dict(
            required=["d_enum", "b_calcfloat"],
        ),
    )


class TestArray(RootModel[List[Test]]):
    model_config = ConfigDict(
        title="TestArrayTransposed",
        json_schema_extra=dict(
            datagrid_index_name=("section", "title", "name"),
        ),
    )
    root: List[Test]


# -
edit_tsv_w_diff = EditTsvWithDiff(model=TestArray,
                                    transposed = True,
                                    primary_key_name="a_int",
                                    header_depth=3,
                                    exclude_metadata=True,
                                    )
display(edit_tsv_w_diff)


# +

edit_tsv_w_diff = EditTsvFileUpload(model=TestArray,
                                  transposed = False,
                                  primary_key_name="a_int",
                                  header_depth=3,
                                  exclude_metadata=False,
                                 )
display(edit_tsv_w_diff)


# -

def process_file_callback(path: pathlib.Path):
    value, errors = xdg.read_excel(path, is_transposed=False, header_depth=3,model=TestArray)
    print(value)
upload_widget = TempFileUploadProcessor(fn_process=process_file_callback)
display(upload_widget)


