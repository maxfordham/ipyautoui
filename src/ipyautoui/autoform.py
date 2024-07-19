"""layout attributes of a form box
"""

# +
import ipywidgets as w
import traitlets as tr
import typing as ty

from IPython.display import display, clear_output
from ipyautoui.nullable import Nullable
from ipyautoui.constants import (
    KWARGS_SHOWNULL,
    KWARGS_SHOWRAW,
    SHOWNULL_ICON_SHOW,
    SHOWNULL_ICON_HIDE,
)
from ipyautoui.custom.buttonbars import SaveButtonBar
from ipyautoui.custom.title_description import TitleDescription
from ipyautoui._utils import display_python_string, show_hide_widget


def make_bold(s: str) -> str:
    return f"<big><b>{s}</b></big>"


# -
class ShowNull(tr.HasTraits):
    display_bn_shownull = tr.Bool(default_value=True)

    @tr.observe("display_bn_shownull")
    def _observe_display_bn_shownull(self, change):
        show_hide_widget(self.bn_shownull, self.display_bn_shownull)

    def _init_bn_shownull(self):
        self.bn_shownull = w.ToggleButton(**KWARGS_SHOWNULL)
        self.bn_shownull.observe(self._observe_bn_shownull, "value")

    def _observe_bn_shownull(self, on_change):
        self.show_null = self.bn_shownull.value
        if self.show_null:
            self.bn_shownull.icon = SHOWNULL_ICON_HIDE
        else:
            self.bn_shownull.icon = SHOWNULL_ICON_SHOW

    @property
    def bn_shownull(self):
        if not hasattr(self, "_bn_shownull"):
            self._init_bn_shownull()
        return self._bn_shownull

    @bn_shownull.setter
    def bn_shownull(self, value):
        self._bn_shownull = value

    def show_hide_bn_nullable(self):
        """Set display of show null button based on if any nullable widgets are found."""
        if hasattr(self, "check_for_nullables"):
            if (
                self.check_for_nullables()
            ):  # check_for_nullables is defined in AutoObject
                self.display_bn_shownull = True
            else:
                self.display_bn_shownull = False
        else:
            self.display_bn_shownull = False


if __name__ == "__main__":
    sn = ShowNull()
    display(sn.bn_shownull)


# +
class ShowRaw(tr.HasTraits):
    show_raw = tr.Bool()
    fn_onshowraw = tr.Callable(default_value=lambda: "{'test':'json'}")
    fn_onhideraw = tr.Callable(default_value=lambda: None)

    @tr.validate("show_raw")
    def _validate_show_raw(self, proposal):
        return proposal["value"]

    @tr.default("show_raw")
    def _default_show_raw(self):
        return False

    @tr.observe("show_raw")
    def _observe_show_raw(self, change):
        show_hide_widget(self.bn_showraw, self.show_raw)

    @tr.default("fn_onshowraw")
    def _default_fn_onshowraw(self):
        return self.display_showraw

    @tr.default("fn_onhideraw")
    def _default_fn_onhideraw(self):
        return self.display_ui

    def _init_bn_showraw(self):
        self._bn_showraw = w.ToggleButton(**KWARGS_SHOWRAW)
        self.vbx_showraw = w.VBox()
        self.out_raw = w.Output()
        self.vbx_showraw.children = [self.out_raw]

        # _init_controls
        self.bn_showraw.observe(self._observe_bn_showraw, "value")

    @property
    def vbx_showraw(self):
        if not hasattr(self, "_vbx_showraw"):
            self._init_bn_showraw()
        return self._vbx_showraw

    @vbx_showraw.setter
    def vbx_showraw(self, value):
        self._vbx_showraw = value

    @property
    def bn_showraw(self):
        if not hasattr(self, "_bn_showraw"):
            self._init_bn_showraw()
        return self._bn_showraw

    def _observe_bn_showraw(self, onchange):
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
    # @property
    # def json(self):
    #     return '{"a":"b"}'

    def display_ui(self):  # NOTE: this overwritten this in AutoObjectForm
        self.vbx_widget.layout.display = ""

    def display_showraw(self):  # NOTE: this overwritten this in AutoObjectForm
        self.vbx_widget.layout.display = "None"
        return self.json


class WrapSaveButtonBar(tr.HasTraits):  # TODO: extend TitleDescription
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

    show_savebuttonbar = tr.Bool(default_value=True)
    fns_onsave = tr.List(trait=tr.Callable())
    fns_onrevert = tr.List(trait=tr.Callable())

    @tr.observe("show_savebuttonbar")
    def _observe_show_savebuttonbar(self, change):
        show_hide_widget(self.savebuttonbar, self.show_savebuttonbar)

    @property
    def savebuttonbar(self):
        if not hasattr(self, "_savebuttonbar"):
            self.savebuttonbar = SaveButtonBar()
        return self._savebuttonbar

    @savebuttonbar.setter
    def savebuttonbar(self, value):
        self._savebuttonbar = value

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

    @tr.default("fns_onsave")
    def _default_fns_onsave(self):
        return self.savebuttonbar.fns_onsave

    @tr.default("fns_onrevert")
    def _default_fns_onrevert(self):
        return self.savebuttonbar.fns_onsave


class AutoObjectFormLayout(ShowRaw, ShowNull, WrapSaveButtonBar):
    pass


if __name__ == "__main__":
    ui = AutoObjectFormLayout(show_savebuttonbar=True)  # description="description",
    display(ui)


# +
def demo_autoobject_form(title="test", description="a description of the title"):
    """for docs and testing only..."""
    from ipyautoui.custom.buttonbars import SaveButtonBar

    li = [AutoObjectFormLayout, TitleDescription, w.VBox, ShowNull]

    class TestForm(*li):
        def __init__(self, **kwargs):
            self.vbx_error = w.VBox()
            self.vbx_widget = w.VBox()

            self.vbx_widget.children = [w.ToggleButton()]
            super().__init__(
                **kwargs,
            )

            self.children = [
                self.savebuttonbar,
                w.HBox([self.bn_showraw, self.bn_shownull, self.html_title]),
                self.html_description,
                self.vbx_widget,
                self.vbx_showraw,
            ]

    form = TestForm()
    form.title = make_bold(title)
    form.description = description
    form.show_raw = True
    form.show_description = True
    form.show_title = True
    form.show_savebuttonbar = True
    form.savebuttonbar.layout = {"border": "solid red 2px"}
    form.hbx_title_description.layout = {"border": "solid blue 2px"}
    form.vbx_widget.layout = {"border": "solid green 2px", "height": "200px"}
    form.vbx_widget.children = [w.ToggleButton(description="PlaceHolder Widget")]
    form.vbx_showraw.layout = {
        "border": "solid orange 2px",
        "height": "200px",
    }
    form.layout = {"border": "solid yellow 2px"}
    form._observe_bn_showraw("d")
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
