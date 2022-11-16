import ipywidgets as w
import random
import traitlets as tr
import typing as ty
from pydantic import BaseModel, Field


class ExampleRoot(BaseModel):
    __root__: str = Field(default="Test", description="This test is important")


class ExampleSchema(BaseModel):
    text: str = Field(default="Test", description="This test is important")


class ExampleDataFrameCols(BaseModel):
    string: str = Field(aui_column_width=100)
    floater: float = Field(aui_column_width=70, aui_sig_fig=3)


class ExampleDataFrameCols1(BaseModel):
    string: str = Field("string", aui_column_width=100)
    floater: float = Field(3.14, aui_column_width=70, aui_sig_fig=3)


class ExampleDataFrameSchema(BaseModel):
    """no default"""

    __root__: ty.List[ExampleDataFrameCols] = Field(format="dataframe")


class ExampleDataFrameSchema1(BaseModel):
    """default."""

    __root__: ty.List[ExampleDataFrameCols] = Field(
        [ExampleDataFrameCols1(string="test", floater=1.5)], format="dataframe"
    )


class ExampleDataFrameSchema2(BaseModel):
    """no default. but properties have default"""

    __root__: ty.List[ExampleDataFrameCols1] = Field(format="dataframe")


def get_di():
    words = [
        "a",
        "AAA",
        "AAAS",
        "aardvark",
        "Aarhus",
        "Aaron",
        "ABA",
        "Ababa",
        "aback",
        "abacus",
        "abalone",
        "abandon",
        "abase",
    ]
    n = random.randint(0, len(words) - 1)
    m = random.randint(0, 1)
    _bool = {0: False, 1: True}
    return {words[n]: _bool[m]}


def fn_add():
    return TestItem(di=get_di())


class TestItem(w.HBox, tr.HasTraits):
    value = tr.Dict()

    def __init__(self, di: ty.Dict = get_di()):
        self.value = di
        self._init_form()
        self._init_controls()

    def _init_form(self):
        self._label = w.HTML(f"{list(self.value.keys())[0]}")
        self._bool = w.ToggleButton(list(self.value.values())[0])
        super().__init__(children=[self._bool, self._label])  # self._acc,

    def _init_controls(self):
        self._bool.observe(self._set_value, names="value")

    def _set_value(self, change):
        self.value = {self._label.value: self._bool.value}


def get_descriptions():
    words = """
    a
    AAA
    AAAS
    aardvark
    """
    words = set([word.lower() for word in words.splitlines()])
    descriptions = list(words)[:10]
    return descriptions
