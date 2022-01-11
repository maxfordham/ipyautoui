"""extending default pydantic BaseModel. NOT IN USE."""
import pathlib
from pydantic import BaseModel

class BaseModel(BaseModel):
    def file(self, path: pathlib.Path, **json_kwargs):
        if 'indent' not in json_kwargs.keys():
            json_kwargs.update({'indent':4})
        path.write_text(self.json(**json_kwargs), encoding='utf-8')
        
    class Config:
        json_encoders = {pathlib.PurePosixPath:  str}
        arbitrary_types_allowed = True