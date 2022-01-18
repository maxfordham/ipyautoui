import pathlib
import ipywidgets as widgets
import random
import traitlets
import typing
from pydantic import BaseModel, Field

DIR_TESTS = pathlib.Path(__file__).parent
PATH_TEST_AUI = DIR_TESTS / 'testdata' / 'test.aui.json'
DIR_FILETYPES = DIR_TESTS / 'filetypes'


class AutoUiExample(BaseModel):
    text: str = Field(default="Test", description="This test is important")


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


class TestItem(widgets.HBox, traitlets.HasTraits):
    value = traitlets.Dict()

    def __init__(self, di: typing.Dict = get_di()):
        self.value = di
        self._init_form()
        self._init_controls()

    def _init_form(self):
        self._label = widgets.HTML(f"{list(self.value.keys())[0]}")
        self._bool = widgets.ToggleButton(list(self.value.values())[0])
        super().__init__(children=[self._bool, self._label])  # self._acc,

    def _init_controls(self):
        self._bool.observe(self._set_value, names="value")

    def _set_value(self, change):
        self.value = {self._label.value: self._bool.value}