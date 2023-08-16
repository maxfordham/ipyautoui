from pydantic import field_validator, Field
import pathlib
import typing as ty
from pydantic_settings import BaseSettings

# https://stackoverflow.com/questions/52119454/how-to-obtain-jupyter-notebooks-path
# ^ impossible to know with clarity the exact filename and directory of a notebook.
#   it can therefore be explicitly defined as an env var. required for getting rel paths


class Env(BaseSettings):
    IPYAUTOUI_ROOTDIR: ty.Optional[pathlib.Path] = Field(
        None,
        description="typically the directory that the Notebook is in."
        " Required for AutoDisplay to find relative paths to: pdfs, vega, ...",
    )

    @field_validator("IPYAUTOUI_ROOTDIR")
    @classmethod
    def _IPYAUTOUI_ROOTDIR(cls, v):
        """Checks for app.db in parent directory and copies from repo if it does not
        exist.
        """
        if v is None:
            v = pathlib.Path(".").absolute()
        return v
