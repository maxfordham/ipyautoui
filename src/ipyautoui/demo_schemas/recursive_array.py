import typing as ty
from pydantic import RootModel, Field, BaseModel

RecursiveArray = ty.ForwardRef("RecursiveArray")


class MyObject(BaseModel):
    stringy: str = Field("stringy", description="asdfsadf")
    inty: int = 1
    floaty: float = 1.5


class RecursiveArray(RootModel):
    """a recursive array"""

    root: list[ty.Union[RecursiveArray, MyObject]]
