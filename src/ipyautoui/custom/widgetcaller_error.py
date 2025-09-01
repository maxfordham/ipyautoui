# +
"""widget caller error"""


# +
import ipywidgets as w
import traitlets as tr
from IPython.display import clear_output, JSON, display
from ipyautoui._utils import display_python_string


# +
class WidgetCallerError(w.VBox):
    widget = tr.Unicode(default_value="")
    error = tr.Unicode(default_value="")
    schema = tr.Dict(default_value={})
    value = tr.Unicode(default_value="error")

    @tr.observe("widget")
    def _observe_widget(self, change):
        with self.out_widget:
            clear_output()
            display_python_string(change["new"])
        return change["new"]

    @tr.observe("error")
    def _observe_error(self, change):
        with self.out_error:
            clear_output()
            display_python_string(change["new"])
        return change["new"]

    @tr.observe("schema")
    def _observe_schema(self, change):
        with self.out_schema:
            clear_output()
            display(JSON(change["new"]))

        return change["new"]

    def __init__(self, **kwargs):
        self.html_widget_title = w.HTML("<b>Widget Name:</b>")
        self.html_error_title = w.HTML("<b>Error:</b>")
        self.html_schema_title = w.HTML("<b>JsonSchema that generates UI:</b>")
        self.out_widget = w.Output()
        self.out_error = w.Output()
        self.out_schema = w.Output()
        super().__init__(**kwargs)
        self.children = [
            self.html_widget_title,
            self.out_widget,
            self.html_error_title,
            self.out_error,
            self.html_schema_title,
            self.out_schema,
        ]


# +
if __name__ == "__main__":
    widget = "<class 'ipyautoui.autoobject.AutoObject'>"

    schema = {
        "title": "ScheduleRuleSet",
        "description": 'A set of rules that defines what equipment specifications will appear in a given schedule.<br>\nRules must evaluate to True for the item to be included in a schedule.\nThis is analogous to how \n<font color="blue"><a href="https://help.autodesk.com/view/RVT/2023/ENU/?guid=GUID-400FD74B-00E0-4573-B3AC-3965E65CBBDB" target="blank" >filter rules work in Revit.</a></font><br>As such, rules defined are imported into Revit and are used to create Revit Schedules.<br><hr>',
        "type": "object",
        "properties": {
            "set_type": {
                "title": "RuleSetType",
                "description": "An enumeration.",
                "enum": ["AND", "OR"],
                "type": "string",
                "default": "AND",
                "disabled": True,
            },
            "rules": {
                "title": "Rules",
                "description": '\neach rule returns a boolean for the logical evaluation for every TypeSpecification item from the requested categories within a project.<br>\nA common pattern is to:\n\n<ul>\n    <li>leave "Categories" blank, thus applying the rule to all items in all categories</li>\n    <li>select <font color="blue"><a href="https://uniclass.thenbs.com/taxon/pr" target="blank" >Uniclass Product codes 🔗</a></font> / <font color="blue"><a href="https://uniclass.thenbs.com/taxon/ss" target="blank" >Uniclass System codes 🔗</a></font> as the "Parameter"</li>\n    <li>select "begins with" as the operator</li>\n    <li>select the required code and subcode for "Value"</li>\n</ul>\n',
                "type": "array",
                "items": {
                    "title": "Rule",
                    "type": "object",
                    "properties": {
                        "categories": {
                            "title": "Categories",
                            "description": "Revit MEP categories to filter by (i.e. revit object must belong to categories defined here). If empty, all categories are included.",
                            "type": "array",
                            "items": {"$ref": "#/$defs/RevitCategoriesEnum"},
                        },
                        "parameter": {
                            "title": "Parameter",
                            "description": "name of schedule parameter against which to apply filter rule",
                            "autoui": "ipywidgets.Combobox",
                            "type": "string",
                        },
                        "operator": {
                            "description": "logical operator used to evaluate parameter value against value below",
                            "allOf": [{"$ref": "#/$defs/RevitOperatorsEnum"}],
                        },
                        "value": {
                            "title": "Value",
                            "description": "Value to filter by. Evaluates to the appropriate type. Leave empty if none required (e.g. has value operator)",
                            "default": "",
                            "autoui": "ipywidgets.Combobox",
                            "type": "string",
                        },
                    },
                    "required": ["categories", "parameter", "operator"],
                    "align_horizontal": False,
                    "autoui": "__main__.RuleUi",
                },
            },
        },
        "required": ["rules"],
    }

    error = "big eror message"

    error_widget = WidgetCallerError(widget=widget, schema=schema, error=error)
    display(error_widget)

# +
