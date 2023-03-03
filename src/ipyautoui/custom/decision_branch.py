# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
"""
a UI element that loads a folder for data caching, whilst storing a record of folders in use
"""

# %run _dev_sys_path_append.py
# %run __init__.py
#
# %load_ext lab_black
from pydantic import BaseModel
import ipywidgets as w
import typing as ty
import traitlets as tr


class TreeModel(BaseModel):
    """generic tree model."""

    title: str = None
    description: str = ""
    options: list
    value: ty.Union[str, float, int] = None  # ty.Union[str, float, int]
    children: ty.ForwardRef("TreeModel") = None
    disabled: bool = False
    placeholder: str = ""

    class Config:
        extra = "allow"


TreeModel.update_forward_refs()


# +
def gen_widget(di, widgets=[]):
    wi = w.Combobox(**di, ensure_option=True, layout={"width": "200px"})
    widgets += [wi]
    if di["children"] is not None:
        return gen_widget(di["children"], widgets=widgets)
    else:
        return widgets


class DecisionUi(w.HBox):
    config = tr.Instance(klass=TreeModel)
    _value = tr.List(allow_none=True)

    @tr.validate("config")
    def _valid_config(self, proposal):
        if isinstance(proposal["value"], TreeModel):
            return proposal["value"]
        else:
            return TreeModel(**proposal["value"])

    def __init__(self, config: TreeModel, value=None):
        self.config = config
        super().__init__()
        self._init_form()
        self._init_controls()
        self._update_value("")

    def _init_form(self):
        li = []
        li = gen_widget(self.config.dict(), widgets=li)
        self.children = li

    def _init_controls(self):
        [c.observe(self._update_value, "value") for c in self.children]

    def _update_value(self, change):
        li = [c.value for c in self.children]
        if None not in li:
            self._value = [c.value for c in self.children]
        else:
            self._value = None

    @property
    def disabled(self):
        return [c.disabled for c in self.children]

    @disabled.setter
    def disabled(self, value):
        for c, v in zip(self.children, value):
            c.disabled = v

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        for c, v in zip(self.children, value):
            c.value = v


if __name__ == "__main__":
    PROJECTS = ["J5001", "J5002"]
    t = TreeModel(
        **{
            "options": PROJECTS,
            "children": {
                "options": ["Calcs"],
                "disabled": True,
                "children": {"options": ["WUFI", "PartL"]},
                "value": "Calcs",
            },
            "value": "J5001",
        }
    )
    ui = DecisionUi(t)
    display(ui)
# -

if __name__ == "__main__":
    ui.value = ["J0001", "Calcs", "WUFI"]
    ui.disabled = [False, False, True]
