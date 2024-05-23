import traitlets as tr
import typing as ty
import ipywidgets as w
import inspect
from pydantic import BaseModel
from IPython.display import display, clear_output, Markdown
import json
import pathlib

from ipyautoui import demo_schemas as demo_schemas
from ipyautoui.demo_schemas import CoreIpywidgets
from ipyautoui._utils import display_python_file, display_python_string
from ipyautoui import AutoUi

# TODO: add AutoRenderer functionality to demo


def get_classes(member=demo_schemas) -> ty.List[ty.Type[BaseModel]]:
    return [obj for name, obj in inspect.getmembers(member) if inspect.isclass(obj)]


def get_order():
    """Get the order of the classes imported into demo_schemas."""
    p = pathlib.Path(__file__).parent / "demo_schemas" / "__init__.py"
    lines = p.read_text().split("\n")
    li = []
    current_line = ""
    for line in lines:
        stripped = line.strip().strip(",")
        if stripped == "" or stripped[0] == "#":
            continue
        if "(" in stripped:  # start of multiline import
            current_line += stripped.strip("(")
            continue
        if ")" in stripped:  # end of multiline import
            current_line += stripped.strip(")")
            li.append(current_line)
            current_line = ""
            continue
        if current_line:  # middle of multiline import
            current_line += stripped
            continue
        # single line import
        li.append(stripped)
    li = [l.split("import ")[1] for l in li if "import " in l]
    return li


pycall = """# copy the code below into your notebook to try the demo

from ipyautoui import AutoUi
from ipyautoui.demo_schemas import {name}
ui = AutoUi({name})
ui
"""


class Demo(w.Tab, tr.HasTraits):
    pydantic_model = tr.Type(klass=BaseModel)
    python_file = tr.Instance(klass=pathlib.PurePath)

    @tr.observe("pydantic_model")
    def _observe_pydantic_model(self, change):
        try:
            self.python_file = pathlib.Path(inspect.getfile(self.pydantic_model))
        except:
            raise ValueError(
                "for the Demo to work, the `pydantic_model` must"
                " be defined in a separate python file."
            )
        self._update_autoui()
        self._update_pydantic()
        self._update_jsonschema()
        self._update_jsonschema_caller()
        self._update_value()

    @tr.observe("selected_index")
    def _observe_selected_index(self, change):
        if change["new"] == 4:
            self._update_value()

    def __init__(self, pydantic_model=CoreIpywidgets):
        super().__init__()
        self.vbx_autoui = w.VBox()
        self.vbx_pydantic = w.VBox()
        self.vbx_jsonschema = w.VBox()
        self.vbx_jsonschema_caller = w.VBox()
        self.vbx_value = w.VBox()
        titles = {
            0: "AutoUi",
            1: "pydantic-model",
            2: "jsonschema",
            3: "jsonschema-caller",
            4: "autoui-value",
        }
        self.children = [
            self.vbx_autoui,
            self.vbx_pydantic,
            self.vbx_jsonschema,
            self.vbx_jsonschema_caller,
            self.vbx_value,
        ]
        [self.set_title(k, v) for k, v in titles.items()]
        self.out_pycall = w.Output()
        self.vbx_pycall = w.VBox([self.out_pycall])
        self.out_pydantic = w.Output()
        self.vbx_pydantic.children = [self.out_pydantic]

        self.out_sch = w.Output()
        self.vbx_jsonschema.children = [self.out_sch]

        self.out_caller = w.Output()
        self.vbx_jsonschema_caller.children = [self.out_caller]

        self.out_value = w.Output()
        self.vbx_value.children = [self.out_value]
        self.pydantic_model = pydantic_model

    def _update_pycall(self):
        with self.out_pycall:
            clear_output()
            display_python_string(pycall.format(name=self.pydantic_model.__name__))

    def _update_autoui(self):
        self.autoui = AutoUi(self.pydantic_model)
        self._update_pycall()
        self.vbx_autoui.children = [self.vbx_pycall, self.autoui]

    def _update_pydantic(self):
        with self.out_pydantic:
            clear_output()
            display_python_file(self.python_file)

    def _update_jsonschema(self):
        s_sch = f"""
```json
{json.dumps(self.pydantic_model.model_json_schema(), indent=4)}
```
"""
        with self.out_sch:
            clear_output()
            display(Markdown(s_sch))

    def _update_jsonschema_caller(self):
        try:
            s_sch = f"""
```json
{json.dumps(self.autoui.jsonschema_caller, indent=4)}
```
"""
            with self.out_caller:
                clear_output()
                display(Markdown(s_sch))
        except:
            with self.out_caller:
                s_sch = self.autoui.jsonschema_caller
                from pprint import pprint

                clear_output()
                display(pprint(s_sch))

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
        order = get_order()
        if set(self.map_name_pydantic_model.keys()) != set(order):
            raise ValueError("set(self.map_name_pydantic_model.keys()) != set(order):")
        else:
            self.map_name_pydantic_model = {
                o: self.map_name_pydantic_model[o] for o in order
            }
        self.select.value = None
        self.select.options = list(self.map_name_pydantic_model.keys())
        self.select.value = self.select.options[0]

    def __init__(
        self,
        pydantic_models: ty.List[ty.Type[BaseModel]] = get_classes(member=demo_schemas),
    ):
        super().__init__(layout={"border": "solid 2px PowderBlue"})

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
        self.vbx_select = w.VBox(
            layout={
                "border": "solid 2px LemonChiffon",
                "padding": "0px 0px 10px 0px",
                "align_items": "center",
            }
        )
        self.select_title = w.HTML(
            "⬇️ -- <b>Select demo pydantic model / generated AutoUi</b> -- ⬇️"
        )
        self.vbx_select.children = [self.select_title, self.select]
        # self.vbx_select.layout

        self.pydantic_models = pydantic_models
        self.demo = Demo()
        self.children = [self.vbx_select, self.demo]
        self._init_controls()

    def _init_controls(self):
        self.select.observe(self._update_demo, "value")

    def _update_demo(self, on_change):
        model = self.map_name_pydantic_model[self.select.value]
        if self.demo.pydantic_model != model:
            self.demo.pydantic_model = model


def demo():
    display(DemoReel())
