# +
import ipywidgets as w
import traitlets as tr
from ipyautoui.constants import (
    DELETE_BUTTON_KWARGS,
    ADD_BUTTON_KWARGS,
    LOAD_BUTTON_KWARGS,
)
from IPython.display import display
# from ipyautoui.custom.title_description import TitleDescription
import inspect

# +
# TODO
class FormLayouts:
    @staticmethod
    def default_layout_form(ui):
        ui.layout.display = "flex"
        ui.layout.flex_flow = "row"
        ui.layout.align_items = "stretch"
        ui.children = [ui.html_title, ui.bn, ui.select, ui.hbx_message]

    @staticmethod
    def align_horizontal_left(ui):
        # up-down
        ui.layout.display = "flex"
        ui.layout.flex_flow = "row"
        ui.layout.align_items = "stretch"
        ui.children = [ui.bn, w.VBox([ui.html_title, ui.select]), ui.hbx_message]

    @staticmethod
    def align_horizontal_right(ui):
        # up-down
        ui.layout.display = "flex"
        ui.layout.flex_flow = "row"
        ui.layout.align_items = "stretch"
        ui.children = [
            ui.hbx_message,
            ui.html_title,
            ui.select,
            ui.bn,
        ]

    @staticmethod
    def align_vertical_right(ui):
        # up-down
        ui.layout.display = "flex"
        ui.layout.flex_flow = "column"
        ui.layout.align_items = "stretch"

        ui.children = [
            ui.select,
            ui.hbx_message,
            ui.html_title,
            ui.bn,
        ]

    @staticmethod
    def align_vertical_left(ui):
        # up-down
        ui.layout.display = "flex"
        ui.layout.flex_flow = "column"
        ui.layout.align_items = "stretch"

        ui.children = [
            w.HBox([ui.bn, ui.html_title]),
            ui.select,
            ui.hbx_message,
        ]


SelectAndClickFormLayouts = (
    FormLayouts  # TODO: deprecate name `SelectAndClickFormLayouts`
)


class SelectAndClick(w.Box):
    _value = tr.Any(allow_none=True, default_value=None)
    fn_onclick = tr.Union(
        [
            tr.Callable(),
            tr.List(tr.Callable()),
        ],
        default_value=lambda v, **kwargs: print(f"do something: {str(v)}"),
    )
    fn_get_options = tr.Callable(None, allow_none=True)
    options = tr.Union(
        [tr.List(), tr.Dict(), tr.List(tr.Tuple(tr.Any(), tr.Any()))], default_value=[]
    )  # allow whatever ipywidgets allows (list, list of tuples, dict)
    title = tr.Unicode(default_value="")
    fn_format_value = tr.Callable(
        default_value=lambda self: f"value set to: {self.value}"
    )
    fn_layout_form = tr.Callable()
    # show_loading_svg = tr.Bool(default_value=False)

    @tr.default("fn_layout_form")
    def default_fn_layout_form(self):
        return FormLayouts.default_layout_form

    @tr.observe("fn_layout_form")
    def _fn_layout_form(self, on_change):
        self.fn_layout_form(self)

    @tr.observe("options")
    def _observe_options(self, change):
        self.select.options = change["new"]

    @tr.observe("title")
    def _observe_title(self, change):
        self.html_title.value = change["new"]

    @tr.observe("_value")
    def _observe_value(self, change):
        self.html_value.value = self.fn_format_value(self)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.select.value = value
        self._value = value

    def _init_form(self, selector_widget=w.Dropdown):
        self.select = selector_widget()
        self.bn = w.Button()
        self.out_loading = w.Output()
        self.html_title = w.HTML()
        self.html_value = w.HTML()
        self.html_notify = w.HTML()
        self.hbx_message = w.HBox([self.html_notify, self.html_value, self.html_notify])

    def __init__(self, selector_widget=w.Dropdown, **kwargs):
        self._init_form(selector_widget=selector_widget)
        value = None
        if kwargs.get("value") is not None:
            value = kwargs["value"]
            kwargs.pop("value")
        super().__init__(**kwargs)

        self._init_controls()
        if self.fn_get_options is not None:
            self.update_options()
        if value is not None:
            self.value = value

        self.fn_layout_form(self)
        self._observe_select_value("")

    def _init_controls(self, dynamic_message=False):
        self.bn.on_click(self.onclick)
        self.set_observe_value(self.select, self._observe_select_value)
        self.observe(self._observe_select_value, "_value")

    def set_observe_value(self, widget_to_observe, fn_onchange):
        if "value" in widget_to_observe.traits():
            widget_to_observe.observe(fn_onchange, "value")
        elif "_value" in widget_to_observe.traits():
            widget_to_observe.observe(fn_onchange, "_value")
        else:
            raise ValueError("selector widget must have a `value` or `_value` trait")

    def _observe_select_value(self, on_change):
        if self.value == self.select.value:
            self.html_notify.value = "✔️"
        else:
            self.html_notify.value = "⚠️"

    def update_options(self):
        self.options = self.fn_get_options()

    # def loading(self, is_loading):
    #     with self.out_loading:
    #         if is_loading:
    #             display(SVG(PATH_SVG))
    #         else:
    #             clear_output()

    def runfn(self, fn):
        if "self" in inspect.signature(fn).parameters:
            return fn(self.select.value, self=self)
        else:
            return fn(self.select.value)

    def onclick(self, on_click):
        # if self.show_loading_svg:
        #     self.loading(True)

        if isinstance(self.fn_onclick, list):
            [self.runfn(fn) for fn in self.fn_onclick]
        else:
            self.runfn(self.fn_onclick)
        self._value = self.select.value

        # if self.show_loading_svg:
        #     self.loading(False)


# -

if __name__ == "__main__":

    def fn_onclick(value, self):
        self.select.layout.display = "None"

    ui = SelectAndClick(
        options=[("A", "a"), ("B", "b"), ("C", "c")],
        title="asefd",
        value=("a"),
        selector_widget=w.Dropdown,
        fn_format_value=lambda self: f"value = {', '.join(self.value)}",
        fn_onclick=fn_onclick,
    )
    display(ui)

if __name__ == "__main__":
    get_fruit_dict = lambda: {"apple": "a", "berry": "b"}
    get_fruit_list = lambda: ["apple", "berry"]
    get_fruit_tuples = lambda: [("apple", "a"), ("berry", "b"), ("berry", "c")]

if __name__ == "__main__":
    import functools

    cls = functools.partial(w.Combobox, ensure_options=True)
    ui = SelectAndClick(options=get_fruit_list(), selector_widget=cls)
    display(ui)


# +
class Add(SelectAndClick):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        {setattr(self.bn, k, v) for k, v in ADD_BUTTON_KWARGS.items()}


class Remove(SelectAndClick):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        {setattr(self.bn, k, v) for k, v in DELETE_BUTTON_KWARGS.items()}


if __name__ == "__main__":
    add = Add(fn_get_options=get_fruit_tuples, value="a")
    display(add)
# -

if __name__ == "__main__":
    ui = Add(
        fn_get_options=get_fruit_list,
        fn_onclick=lambda v: print(f"loading project {v}"),
        fn_message_onclick=lambda v: print("aasdf"),
        title="load project:",
        align_horizontal=False,
    )
    display(ui)


class Load(SelectAndClick):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        {setattr(self.bn, k, v) for k, v in LOAD_BUTTON_KWARGS.items()}
        self.bn.layout.display = "None"
        self._init_load_controls()

    def _init_load_controls(self):
        self.set_observe_value(self.select, self._show_hide_button)
        self.observe(self._show_hide_button, "_value")

    def _show_hide_button(self, on_something):
        if self.value == self.select.value:
            self.bn.layout.display = "None"
        else:
            self.bn.layout.display = ""


if __name__ == "__main__":
    from time import sleep
    from ipyautoui.custom.combobox_mapped import ComboboxMapped

    LI = {f"J{l}": str(l) for l in [3870, 4321, 6440]}
    ui = Load(
        loaded="3870",
        value="3870",
        fn_get_options=lambda: LI,
        title="<b> | select project</b>",
        fn_onclick=lambda v: sleep(2),
        selector_widget=ComboboxMapped,
    )
    display(ui)


# +
class SelectMultipleAndClick(SelectAndClick):
    @tr.observe("options")
    def _observe_options(self, change):
        self.select.value = (
            []
        )  # HOTFIX: Bugs out setting options if ALL values selected: https://github.com/jupyter-widgets/ipywidgets/issues/3876
        self.select.options = change["new"]

    def __init__(self, **kwargs):
        kwargs["selector_widget"] = w.SelectMultiple
        super().__init__(**kwargs)


class AddMultiple(SelectMultipleAndClick):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        {setattr(self.bn, k, v) for k, v in ADD_BUTTON_KWARGS.items()}


class RemoveMultiple(SelectMultipleAndClick):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        {setattr(self.bn, k, v) for k, v in DELETE_BUTTON_KWARGS.items()}


# -

if __name__ == "__main__":
    ui = AddMultiple(
        fn_get_options=get_fruit_dict,
        title="<b>asdf |</b>",
    )
    display(ui)

if __name__ == "__main__":
    ui.fn_get_options = get_fruit_dict
