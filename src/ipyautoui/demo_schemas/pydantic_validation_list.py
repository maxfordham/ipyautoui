from pydantic import BaseModel, field_validator, Field


class PydanticValidationList(BaseModel):
    a: list[str] = Field(
        description="a list of strings that must contain 'asdf' as the first item.\n If not, it will be added by pydantic validation"
    )
    b: str

    @field_validator("a")
    @classmethod
    def add_val(cls, v: list) -> list:
        if len(v) == 0:
            v = ["asdf"] + v
        if v[0] != "asdf":
            v[0] = "asdf"
        return v
