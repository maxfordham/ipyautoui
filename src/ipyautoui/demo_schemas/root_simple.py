from pydantic import conint, RootModel, ConfigDict


class RootSimple(RootModel):
    root: conint(ge=0, le=3) = 2
