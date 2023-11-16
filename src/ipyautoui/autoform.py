# %run _dev_maplocal_params.py
"""layout attributes of a form box
"""
# +
import ipywidgets as w
import traitlets as tr
import typing as ty

from IPython.display import display, clear_output
from ipyautoui.constants import BUTTON_WIDTH_MIN
from ipyautoui.custom.buttonbars import SaveButtonBar
from ipyautoui._utils import display_python_string


# +
def show_hide_widget(widget, show: bool):
    try:
        if show:
            widget.layout.display = ""
        else:
            widget.layout.display = "None"
    except:
        ValueError(str(widget) + "failed to change layout.display")


def make_bold(s: str) -> str:
    return f"<big><b>{s}</b></big>"


class AutoObjectFormLayout(tr.HasTraits):  # TODO: extend TitleDescription
    """UI container for autoui form

    Attributes:
        title (str): form title
        description (str): form description
        show_description (bool, optional): show the description. Defaults to True.
        show_title (bool, optional): show the title. Defaults to True.
        show_savebuttonbar (bool, optional): show the savebuttonbar. Defaults to True.
        show_raw (bool, optional): show the raw json. Defaults to False.
        fn_onshowraw (callable): do not edit
        fn_onhideraw (callable): do not edit
        fns_onsave (callable): additional functions to be called on save
        fns_onrevert (callable): additional functions to be called on revert
    """

    title = tr.Unicode(default_value="")
    description = tr.Unicode(default_value="")
    show_description = tr.Bool(default_value=True)
    show_title = tr.Bool(default_value=True)
    show_savebuttonbar = tr.Bool(default_value=False)
    show_raw = tr.Bool(default_value=False)
    fn_onshowraw = tr.Callable(default_value=lambda: "{'test':'json'}")
    fn_onhideraw = tr.Callable(default_value=lambda: None)
    fns_onsave = tr.List(trait=tr.Callable())
    fns_onrevert = tr.List(trait=tr.Callable())

    @tr.observe("title")
    def _observe_title(self, change):
        if not hasattr(self, "html_title"):
            self.html_title = w.HTML()
        self.html_title.value = f"<b>{self.title}</b>"

    @tr.observe("description")
    def _observe_description(self, change):
        if not hasattr(self, "html_description"):
            self.html_description = w.HTML()
        self.html_description.value = self.description

    @tr.observe("show_raw")
    def _observe_show_raw(self, change):
        show_hide_widget(self.bn_showraw, self.show_raw)

    @tr.observe("show_description")
    def _observe_show_description(self, change):
        show_hide_widget(self.html_description, self.show_description)

    @tr.observe("show_title")
    def _observe_show_title(self, change):
        show_hide_widget(self.html_title, self.show_title)

    @tr.observe("show_savebuttonbar")
    def _observe_show_savebuttonbar(self, change):
        show_hide_widget(self.savebuttonbar, self.show_savebuttonbar)

    @tr.observe("fns_onsave")
    def _observe_fns_onsave(self, change):
        """NOTE: this observer will alway append actions.
        to delete actions use
            `self.savebuttonbar.fns_onsave = []`
        then set with
            `self.fns_onsave = [lambda: print('save-funcy')]`"""
        value = change["new"]
        if isinstance(value, list):
            [self.savebuttonbar.fns_onsave_add_action(v) for v in value]
        elif isinstance(value, ty.Callable):
            self.savebuttonbar.fns_onsave_add_action(value)
        else:
            raise ValueError("fns_onsave must be a callable or list of callables")
        return self.savebuttonbar.fns_onsave

    @tr.observe("fns_onrevert")
    def _observe_fns_onrevert(self, change):
        """NOTE: this observer will alway append actions.
        to delete actions use
            `self.savebuttonbar.fns_onsave = []`
        then set with
            `self.fns_onrevert = [lambda: print('revert-funcy')]`"""
        value = change["new"]
        if isinstance(value, list):
            [self.savebuttonbar.fns_onrevert_add_action(v) for v in value]
        elif isinstance(value, ty.Callable):
            self.savebuttonbar.fns_onrevert_add_action(value)
        else:
            raise ValueError("fns_onsave must be a callable or list of callables")
        return self.savebuttonbar.fns_onrevert

    @tr.default("fn_onshowraw")
    def _default_fn_onshowraw(self):
        return self.display_showraw

    @tr.default("fn_onhideraw")
    def _default_fn_onhideraw(self):
        return self.display_ui

    @tr.default("fns_onsave")
    def _default_fns_onsave(self):
        return self.savebuttonbar.fns_onsave

    @tr.default("fns_onrevert")
    def _default_fns_onrevert(self):
        return self.savebuttonbar.fns_onsave

    def __init__(self, **kwargs):
        self._init_autoform(**kwargs)

    def _init_autoform(self, **kwargs):
        self._init_form()
        self._init_bn_showraw_controls()
        super().__init__(**kwargs)

    def _init_form(self):
        self.hbx_title = w.HBox()
        self.savebuttonbar = SaveButtonBar(layout={"display": "None"})  #
        self.html_title = w.HTML()
        self._init_bn_showraw()
        self.hbx_title.children = [self.bn_showraw, self.html_title]
        self.html_description = w.HTML()  #

    def _init_bn_showraw(self):
        self.bn_showraw = w.ToggleButton(
            icon="code",
            layout=w.Layout(width=BUTTON_WIDTH_MIN, display="None"),
            tooltip="show raw data",
            style={"font_weight": "bold", "button_color": None},
        )
        self.vbx_showraw = w.VBox()
        self.out_raw = w.Output()
        self.vbx_showraw.children = [self.out_raw]

    def _init_bn_showraw_controls(self):
        self.bn_showraw.observe(self._bn_showraw, "value")

    def _bn_showraw(self, onchange):
        if self.bn_showraw.value:
            self.bn_showraw.tooltip = "show user interface"
            self.bn_showraw.icon = "user-edit"
            di = self.fn_onshowraw()
            self.vbx_showraw.layout.display = ""

            with self.out_raw:
                clear_output()
                display_python_string(di)

        else:
            self.bn_showraw.tooltip = "show raw data"
            self.bn_showraw.icon = "code"
            self.fn_onhideraw()
            self.vbx_showraw.layout.display = "None"
            
    # functionality below overwritten
    @property
    def json(self):
        return '{"a":"b"}'

    def display_ui(self):  # NOTE: this overwritten this in AutoObjectForm
        self.autowidget.layout.display = ""

    def display_showraw(self):  # NOTE: this overwritten this in AutoObjectForm
        self.autowidget.layout.display = "None"
        return self.json


if __name__ == "__main__":
    ui = AutoObjectFormLayout(description="description", show_savebuttonbar=True)
    display(ui)


# +


class TestForm(AutoObjectFormLayout, w.VBox):
    def __init__(self, **kwargs):
        self.autowidget = w.ToggleButton()
        super().__init__(
            **kwargs,
        )
        
        self.children = [
            self.savebuttonbar,
            self.hbx_title,
            self.html_description,
            self.autowidget,
            self.vbx_showraw,
        ]


def demo_autoobject_form(title="test", description="a description of the title"):
    """for docs and testing only..."""
    from ipyautoui.custom.buttonbars import SaveButtonBar

    form = TestForm()
    form.title = make_bold(title)
    form.description = description
    form.show_raw = True
    form.show_description = True
    form.show_title = True
    form.show_savebuttonbar = True
    form.savebuttonbar.layout = {"border": "solid red 2px"}
    form.hbx_title.layout = {"border": "solid blue 2px"}
    form.autowidget.layout = {"border": "solid green 2px", "height": "200px"}
    form.autowidget.children = [w.ToggleButton(description="PlaceHolder Widget")]
    form.vbx_showraw.layout = {
        "border": "solid orange 2px",
        "height": "200px",
    }
    form.layout = {"border": "solid yellow 2px"}
    form._bn_showraw("d")
    return form


if __name__ == "__main__":
    form = demo_autoobject_form()
    display(form)
# -


if __name__ == "__main__":
    form.show_savebuttonbar = False
    form.show_description = False
    form.show_title = False
    form.show_raw = False

if __name__ == "__main__":
    form.show_savebuttonbar = True
    form.show_description = True
    form.show_title = True
    form.show_raw = True


