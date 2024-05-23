from pydantic import BaseModel
import typing as ty
from enum import Enum


class RuleSetType(str, Enum):
    """how the rules logically multiply. Must be `AND` for schedules"""

    AND: str = "AND"
    OR: str = "OR"


class Obj(BaseModel):
    a: int
    b: str


RecursiveObject = ty.ForwardRef("RecursiveObject")


class RecursiveObject(BaseModel):
    op_type: RuleSetType
    obj_set: list[ty.Union[Obj, RecursiveObject]]
