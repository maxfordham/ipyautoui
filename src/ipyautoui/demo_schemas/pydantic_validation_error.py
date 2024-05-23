from pydantic import BaseModel, field_validator, ValidationInfo, Field


class PydanticValidationError(BaseModel):
    a: int = 1
    b: int = 3
    c: int = Field(0, description=" = A + B")

    @field_validator("c")
    @classmethod
    def _c(cls, v: int, info: ValidationInfo) -> int:
        if v != info.data.get("a") + info.data.get("b"):
            raise ValueError("C must equal A + B")
        return v
