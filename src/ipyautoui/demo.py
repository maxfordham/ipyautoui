import traitlets as tr
import typing as ty
from traitlets_paths import PurePath
import ipywidgets as w
import inspect
from ipyautoui.demo_schemas import CoreIpywidgets
from ipyautoui._utils import display_python_file
from ipyautoui import AutoUi
from IPython.display import display, clear_output, Markdown
import json

from pydantic import BaseModel

# from ipyautoui.constants import IS_IPYWIDGETS8
from ipyautoui import demo_schemas as demo_schemas


def get_classes(member=demo_schemas):
    return [obj for name, obj in inspect.getmembers(member) if inspect.isclass(obj)]


class Demo(w.Tab, tr.HasTraits):
    pydantic_model = tr.Type(klass=BaseModel)
    python_file: PurePath()

    @tr.observe("pydantic_model")
    def _observe_pydantic_model(self, change):
        # print(change["old"])
        # print(change["new"])
        try:
            self.python_file = inspect.getfile(self.pydantic_model)
        except:
            raise ValueError(
                "for the Demo to work, the `pydantic_model` must"
                " be defined in a separate python file."
            )
        self._update_autoui()
        self._update_pydantic()
        self._update_jsonschema()
        self._update_value()

    def __init__(self, pydantic_model=CoreIpywidgets):
        super().__init__()
        self.vbx_autoui = w.VBox()
        self.vbx_pydantic = w.VBox()
        self.vbx_jsonschema = w.VBox()
        self.vbx_value = w.VBox()
        titles = {0: "AutoUi", 1: "pydantic-model", 2: "jsonschema", 3: "autoui-value"}
        self.children = [
            self.vbx_autoui,
            self.vbx_pydantic,
            self.vbx_jsonschema,
            self.vbx_value,
        ]
        [self.set_title(k, v) for k, v in titles.items()]
        self.out_pydantic = w.Output()
        self.vbx_pydantic.children = [self.out_pydantic]

        self.out_sch = w.Output()
        self.vbx_jsonschema.children = [self.out_sch]

        self.out_value = w.Output()
        self.vbx_value.children = [self.out_value]
        self.pydantic_model = pydantic_model

    def _update_autoui(self):
        self.autoui = AutoUi(self.pydantic_model)
        self.vbx_autoui.children = [self.autoui]

    def _update_pydantic(self):
        with self.out_pydantic:
            clear_output()
            display_python_file(self.python_file)

    def _update_jsonschema(self):
        s_sch = f"""
```json
{json.dumps(self.pydantic_model.schema(), indent=4)}
```
"""
        with self.out_sch:
            clear_output()
            display(Markdown(s_sch))

    def _update_value(self):
        s_value = f"""
```json
{json.dumps(self.autoui.value, indent=4)}
```
"""
        with self.out_value:
            clear_output()
            display(Markdown(s_value))


class DemoReel(w.VBox):
    pydantic_models = tr.List()

    @tr.observe("pydantic_models")
    def _observe_pydantic_models(self, onchange):
        self.map_name_pydantic_model = {d.__name__: d for d in self.pydantic_models}
        self.select.value = None
        self.select.options = list(self.map_name_pydantic_model.keys())
        self.select.value = self.select.options[0]

    def __init__(
        self,
        pydantic_models: ty.List[ty.Type[BaseModel]] = get_classes(member=demo_schemas),
    ):
        super().__init__()

        self.select = w.ToggleButtons(
            options=[],
            disabled=False,
            button_style="",  # 'success', 'info', 'warning', 'danger' or ''
            tooltips=[
                "Description of slow",
                "Description of regular",
                "Description of fast",
            ],
            # style={"button_width": "500px", "button_color": "lightgreen"}
        )

        self.pydantic_models = pydantic_models
        self.demo = Demo()
        self.children = [self.select, self.demo]
        self._init_controls()

    def _init_controls(self):
        self.select.observe(self._update_demo, "value")

    def _update_demo(self, on_change):
        model = self.map_name_pydantic_model[self.select.value]
        if self.demo.pydantic_model != model:
            self.demo.pydantic_model = model


def demo():
    display(DemoReel())
