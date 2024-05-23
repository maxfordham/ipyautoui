from pydantic import BaseModel, field_validator, ValidationInfo, Field


class PydanticValidation(BaseModel):
    a: int = 1
    b: int = 3
    c: int = Field(0, description=" = A + B", json_schema_extra=dict(disabled=True))

    @field_validator("c")
    @classmethod
    def _c(cls, v: int, info: ValidationInfo) -> int:
        v = info.data.get("a") + info.data.get("b")
        return v
