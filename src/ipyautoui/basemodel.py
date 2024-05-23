"""extending default pydantic BaseModel. NOT IN USE."""

import pathlib
from pydantic import ConfigDict, BaseModel
from typing import Type


def file(self: Type[BaseModel], path: pathlib.Path, **json_kwargs):
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
    path.write_text(self.model_dump_json(**json_kwargs), encoding="utf-8")


setattr(BaseModel, "file", file)
