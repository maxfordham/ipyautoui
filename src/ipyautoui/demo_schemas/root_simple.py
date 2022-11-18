from pydantic import Field, conint, constr
from ipyautoui.basemodel import BaseModel

class RootSimple(BaseModel):
    """a description about my string"""
    __root__: float = Field(default=2, ge=0, le=3)
