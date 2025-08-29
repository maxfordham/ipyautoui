import re
import ipywidgets as w
from dataclasses import dataclass
import traitlets as tr
import typing as ty


# +


@dataclass
class RunNameInputs:
    index: int = 1
    disabled_index: bool = False
    zfill: int = 2
    enum: ty.List = None
    delimiter: str = "-"
    description_length: int = None
    allow_spaces: bool = False
    order: tuple = ("index", "enum", "description")
    pattern: str = None

    def __post_init__(self):
        li = list(self.order)
        if self.index is None:
            li = [l for l in li if l != "index"]
        if self.enum is None:
            li = [l for l in li if l != "enum"]
        if self.description_length is None:
            li = [l for l in li if l != "description"]
        self.order = tuple(li)
        if len(self.order) < 1:
            raise ValueError("you must include 1 of index, enum or description")

        di = {}
        di["index"] = "[0-9]" * self.zfill + f"[{self.delimiter}]"
        di["enum"] = f"[a-z,A-Z,0-9]*[{self.delimiter}]"
        di["description"] = f".+[{self.delimiter}]"
        p = ""
        for l in self.order:
            try:
                p += di[l]
            except:
                pass
        self.pattern = p[:-3]


# -


class RunName(w.HBox):
    """widget for creating an modelling iteration name to a defined format from component parts

    Example:
        value = '000-lean-short_description_of_model-run'
        enum = ['lean', 'clean', 'green']
        zfill = 2
    """

    _value = tr.Unicode()

    @tr.validate("_value")
    def _valid_value(self, proposal):
        val = proposal["value"]
        matched = re.match(self.inputs.pattern, val)
        if not bool(matched):
            print(self.inputs.pattern)
            print(val)
            raise tr.TraitError(f"string musts have format: {self.inputs.pattern}")
        return val

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: tr.Unicode):
        """The setter allows a user to pass a new value field to the class. This also updates the
        `selected` argument used by RunName"""
        if value is not None:
            self._value = value
        self._set_value()

    def __init__(
        self,
        value=None,
        index: int = 1,
        disabled_index: bool = True,
        zfill: int = 2,
        enum: ty.List = ["lean", "clean", "green"],
        delimiter: str = "-",
        description_length: int = 30,
        allow_spaces: bool = False,
        order=("index", "enum", "description"),
    ):
        di = {
            k: v
            for k, v in locals().items()
            if k != "value" and k != "self" and k != "__class__"
        }
        di["index"] = index
        super().__init__()
        self.inputs = RunNameInputs(**di)
        self._init_form()
        self.value = value
        self._init_controls()
        self.update_name("change")

    @property
    def get_options(self):
        if self.inputs.enum is None:
            return []
        else:
            return self.inputs.enum

    def _init_form(self):
        self.index = w.IntText(
            layout={"width": "50px"}, disabled=self.inputs.disabled_index
        )
        self.enum = w.Dropdown(options=self.get_options, layout={"width": "100px"})
        self.description = w.Text()
        self.name = w.Text(disabled=True)
        di = {}
        di["index"] = self.index
        di["enum"] = self.enum
        di["description"] = self.description
        children = []
        for l in self.inputs.order:
            try:
                children.append(di[l])
            except:
                pass
        self.children = children + [self.name]

    def _init_controls(self):
        self.index.observe(self.update_name, names="value")
        self.enum.observe(self.update_name, names="value")
        self.description.observe(self.update_name, names="value")

    def update_name(self, on_change):
        di = {}
        di["enum"] = str(self.enum.value) + self.inputs.delimiter
        di["index"] = (
            str(self.index.value).zfill(self.inputs.zfill) + self.inputs.delimiter
        )
        di["description"] = (
            self.description.value.replace(self.inputs.delimiter, "_")
            + self.inputs.delimiter
        )
        if not self.inputs.allow_spaces:
            di["description"] = di["description"].replace(" ", "_")
        if self.inputs.description_length is not None:
            di["description"] = di["description"][0 : self.inputs.description_length]
        v = ""
        for l in self.inputs.order:
            try:
                v += di[l]
            except:
                pass
        self.name.value = v[:-1]
        self.value = self.name.value

    def _set_value(self):
        try:
            (
                self.index.value,
                self.enum.value,
                self.description.value,
            ) = self.value.split(self.inputs.delimiter, len(self.inputs.order))
        except:
            self.index.value, self.enum.value, self.description.value = (
                self.inputs.index,
                None,
                "description",
            )


# +

if __name__ == "__main__":
    from IPython.display import display

    run = RunName(value="03-lean-description", index=3)
    display(run)
