# +
"""generic iterable object."""
#


# +
import traitlets as tr
import re
import ipywidgets as w
from ipyautoui.constants import BUTTON_WIDTH_MIN


def fn_loadproject(project_number):
    print("load project: ")


LI_PROJECTS = [
    "J0001",
    "J0352",
    "J0354",
    "J0373",
    "J0378",
    "J0385",
    "J0521",
    "J0612",
    "J1074",
    "J1146",
]


class LoadProject(w.HBox, tr.HasTraits):
    value = tr.Unicode()

    @tr.validate("value")
    def _valid_value(self, proposal):
        val = proposal["value"]
        matched = re.match(self.pattern, val)  #
        if not bool(matched):
            print(self.pattern)
            print(val)
            raise tr.TraitError(f"string musts have format: {self.pattern}")  #
        return val

    def __init__(
        self,
        project_number="J5001",
        example_project="J5001",
        example_project_tooltip="load job. NOTE. RED BORDER INDICATES THE ENGINEERING STANDARDS EXAMPLE JOB IS SELECTED",
        pattern="J[0-9][0-9][0-9][0-9]",
        li_projects=LI_PROJECTS,
        fn_loadproject=lambda project_number: print(f"load project: {project_number}"),
    ):
        super().__init__(layout=dict(flex="1 0 auto"))
        self.pattern = pattern
        self.value = project_number
        self.example_project = example_project
        self.example_project_tooltip = example_project_tooltip
        self.li_projects = li_projects
        self.fn_loadproject = fn_loadproject
        self._init_form()
        self._init_controls()
        self._highlight_example_job()

    def _init_form(self):
        self.project_active = w.Text(
            value=self.value,
            layout=w.Layout(width="150px"),
            disabled=True,
            description="active project:",
        )
        self.project_select = w.Combobox(
            value=self.value,
            options=self.li_projects,
            layout=w.Layout(width="70px"),
        )
        self.project_load = w.Button(
            # description='add run',
            tooltip="load job",
            button_style="success",
            icon="upload",
            style={"font_weight": "bold"},
            layout=dict(width=BUTTON_WIDTH_MIN),
        )
        self.children = [self.project_active, self.project_select, self.project_load]

    def _init_controls(self):
        self.project_load.on_click(self._project_load)

    def _project_load(self, on_click):
        self.value = self.project_select.value
        self.fn_loadproject(self.value)
        self.project_active.value = self.value
        self._highlight_example_job()

    def _highlight_example_job(self):
        if self.value == self.example_project:
            self.layout = w.Layout(border="3px solid red")
            self.project_load.tooltip = self.example_project_tooltip
        else:
            self.layout = w.Layout(border="")
            self.project_load.tooltip = "load project"


if __name__ == "__main__":
    from IPython.display import display

    load_project = LoadProject()
    display(load_project)
