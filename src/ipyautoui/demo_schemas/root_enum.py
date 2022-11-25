from pydantic import BaseModel, Field
from enum import Enum


class StrEnum(str, Enum):
    pass


DI_TEST = {
    "Pr_15": "Pr_15 - Preparatory products",
    "Pr_15_31": "Pr_15_31 - Formless preparatory products",
    "Pr_15_31_04": "Pr_15_31_04 - Applied cleaning and treatment products",
}

UniclassProducts = StrEnum("Uniclass Product Codes", DI_TEST)
UniclassProducts.__doc__ = "A list of valid Uniclass Product codes"


class RootEnum(BaseModel):
    __root__: UniclassProducts = Field(
        None, autoui="ipyautoui.autowidgets.Combobox", layout={"width": "400px"}
    )

    class Config:
        arbitrary_types_allowed = True
