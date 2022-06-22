"""extending default pydantic BaseModel. NOT IN USE."""
import pathlib
from pydantic import BaseModel
from typing import Type

def file(self:Type[BaseModel], path: pathlib.Path, **json_kwargs):
    """
    this is a method that is added to the pydantic BaseModel within AutoUi using
    "setattr".
    
    Example:
        ```setattr(model, 'file', file)```
        
    Args:
        self (pydantic.BaseModel): instance
        path (pathlib.Path): to write file to
    """
    if "indent" not in json_kwargs.keys():
        json_kwargs.update({"indent": 4})
    path.write_text(self.json(**json_kwargs), encoding="utf-8")
    

class BaseModel(BaseModel):
        
    class Config:
        json_encoders = {pathlib.PurePosixPath:  str}
        arbitrary_types_allowed = True
        
setattr(BaseModel, 'file', file)