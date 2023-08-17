from pydantic import Field, conint, constr, RootModel, confloat, ConfigDict
from ipyautoui.basemodel import BaseModel

RootSimple = RootModel[conint(ge=0, le=3)]
RootSimple.model_config = ConfigDict(default=2)
