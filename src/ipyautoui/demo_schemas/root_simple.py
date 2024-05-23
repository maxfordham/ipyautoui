from pydantic import conint, RootModel, ConfigDict, Field


class RootSimple(RootModel):
    """a simple slider"""

    root: conint(ge=0, le=3) = 2
