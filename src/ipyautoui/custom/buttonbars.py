# +
import ipywidgets as w
import traitlets as tr
import typing as ty
from ipyautoui.constants import (
    BUTTON_WIDTH_MIN,
    TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT,
    ADD_BUTTON_KWARGS,
    EDIT_BUTTON_KWARGS,
    COPY_BUTTON_KWARGS,
    DELETE_BUTTON_KWARGS,
    RELOAD_BUTTON_KWARGS,
    HELP_BUTTON_KWARGS,
)
from IPython.display import display, clear_output
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


# +
def merge_callables(callables: ty.Union[ty.Callable, ty.List[ty.Callable]]):
    if isinstance(callables, ty.Callable):
        return callables
    elif isinstance(callables, ty.List):
        return lambda: [c() for c in callables if isinstance(c, ty.Callable)]
    else:
        raise ValueError("callables must be a callable or list of callables")


class SaveActions(tr.HasTraits):
    unsaved_changes = tr.Bool(default_value=False)
    fns_onsave = tr.List(trait=tr.Callable())
    fns_onrevert = tr.List(trait=tr.Callable())

    @tr.default("fns_onsave")
    def _default_fns_onsave(self):
        s = f"fns_onsave - action called @ {datetime.now().strftime('%H:%M:%S')}"
        log_fns_onsave = lambda: logging.info(s)
        log_fns_onsave.__name__ = "log_fns_onsave"
        return [log_fns_onsave]  # , print_fns_onsave

    @tr.default("fns_onrevert")
    def _default_fn_revert(self):
        s = f"log_fns_onrevert - action called @ {datetime.now().strftime('%H:%M:%S')}"
        log_fns_onrevert = lambda: logging.info(s)
        log_fns_onrevert.__name__ = "log_fns_onrevert"
        return [log_fns_onrevert]  # , print_fns_onrevert

    def fn_save(self):
        """do not edit"""
        return merge_callables(self.fns_onsave)()

    def fn_revert(self):
        return merge_callables(self.fns_onrevert)()

    def _add_action(
        self,
        action_name,
        fn_add,
        avoid_dupes=True,
        overwrite_dupes=True,
        to_beginning=False,
    ):
        fns = getattr(self, action_name)
        if not hasattr(fn_add, "__name__"):
            logging.warning(
                "an annonymous function (i.e. functools.partial) has been passed"
                " to SaveActions._add_action. it has been given the name `<partial>`."
                " Note. this will cause problems if multiple partial are passed and"
                " avoid_dupes == True. ONLY 1 NO UNNAMED PARTIAL ALLOWED."
                " you can simply assign a name like this:"
                " fn_add.__name__ = 'myname'"
            )
            fn_add.__name__ = "<partial>"
        elif fn_add.__name__ == "<lambda>":
            logging.warning(
                "a lambda function has been passed to SaveActions._add_action."
                " Note. this will cause problems if multiple partial are passed and"
                " avoid_dupes == True. ONLY 1 NO UNNAMED LAMBDA ALLOWED."
                " you can simply assign a name like this:"
                " fn_add.__name__ = 'myname'"
            )
        else:
            pass
        if avoid_dupes:
            names = [f.__name__ for f in getattr(self, action_name)]
            if fn_add.__name__ in names:
                if not overwrite_dupes:
                    raise ValueError(
                        f"ERROR: appending to {action_name}: {fn_add.__name__ } already exists in function names: {str(names)}"
                    )
                else:
                    fns = [f for f in fns if f.__name__ != fn_add.__name__]
        if to_beginning:
            fns = [fn_add] + fns
        else:
            fns = fns + [fn_add]
        setattr(self, action_name, fns)

    def fns_onsave_add_action(
        self,
        fn: ty.Callable,
        avoid_dupes: bool = True,
        overwrite_dupes: bool = True,
        to_beginning=False,
    ):
        self._add_action(
            "fns_onsave",
            fn,
            avoid_dupes=avoid_dupes,
            overwrite_dupes=overwrite_dupes,
            to_beginning=to_beginning,
        )

    def fns_onrevert_add_action(
        self,
        fn: ty.Callable,
        avoid_dupes: bool = True,
        overwrite_dupes: bool = True,
        to_beginning=False,
    ):
        self._add_action(
            "fns_onrevert",
            fn,
            avoid_dupes=avoid_dupes,
            overwrite_dupes=overwrite_dupes,
            to_beginning=to_beginning,
        )


# -

if __name__ == "__main__":
    actions = SaveActions()
    f = lambda: print("test")
    f.__name__ = "f"
    f1 = lambda: print("test1")
    f1.__name__ = "f1"
    print("f")
    print("-----")
    actions.fns_onsave_add_action(f)
    actions.fns_onsave_add_action(f1)
    actions.fn_save()
    print("")
    print("f1")
    print("-----")
    actions.fns_onrevert_add_action(f)
    actions.fns_onrevert_add_action(f1)
    actions.fn_revert()


# +
class SaveButtonBar(SaveActions, w.HBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_form()
        self._init_controls()

    def _init_form(self):
        self.tgl_unsaved_changes = w.ToggleButton(
            disabled=True, layout=w.Layout(width=BUTTON_WIDTH_MIN)
        )
        self.bn_save = w.Button(
            icon="save",
            tooltip="save changes",
            button_style="success",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.bn_revert = w.Button(
            icon="undo",
            tooltip="revert to last save",
            button_style="warning",
            style={"font_weight": "bold"},
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.message = w.HTML("")
        self.children = [
            self.tgl_unsaved_changes,
            self.bn_revert,
            self.bn_save,
            self.message,
        ]
        self._observe_tgl_unsaved_changes("change")

    def _init_controls(self):
        self.bn_save.on_click(self._save)
        self.bn_revert.on_click(self._revert)
        self.observe(self._observe_unsaved_changes, "unsaved_changes")
        self.tgl_unsaved_changes.observe(self._observe_tgl_unsaved_changes, "value")

    def _save(self, click):
        self.fn_save()
        self.message.value = (
            f'<i>changes saved: {datetime.now().strftime("%H:%M:%S")}</i>'
        )
        self.unsaved_changes = False

    def _revert(self, click):
        self.fn_revert()
        self.message.value = f"<i>UI reverted to last save</i>"
        self.unsaved_changes = False

    def _observe_unsaved_changes(self, onchange):
        self.tgl_unsaved_changes.value = self.unsaved_changes

    def _observe_tgl_unsaved_changes(self, onchange):
        if self.tgl_unsaved_changes.value:
            self.tgl_unsaved_changes.button_style = "danger"
            self.tgl_unsaved_changes.icon = "circle"
            self.tgl_unsaved_changes.tooltip = (
                "DANGER: changes have been made since the last save"
            )
        else:
            self.tgl_unsaved_changes.button_style = "success"
            self.tgl_unsaved_changes.icon = "check"
            self.tgl_unsaved_changes.tooltip = (
                "SAFE: no changes have been made since the last save"
            )


if __name__ == "__main__":
    sb = SaveButtonBar()
    display(sb)
# -

if __name__ == "__main__":
    f = lambda: print("test")
    f.__name__ = "f"
    f1 = lambda: print("test1")
    f1.__name__ = "f1"
    sb.fns_onsave_add_action(f)
    sb.fns_onsave_add_action(f1)

    sb.fns_onrevert_add_action(f)
    sb.fns_onrevert_add_action(f1)

if __name__ == "__main__":
    sb.unsaved_changes = True

IO_BUTTON_KWARGS = {'tooltip': 'import/export', 'style': {}, 'layout': {'width': '44px'}, 'icon': 'arrows-alt-v'}


# +
class CrudOptions(ty.TypedDict):
    tooltip: str
    tooltip_clicked: str
    button_style: str
    message: str


class CrudView(ty.TypedDict):
    add: CrudOptions
    edit: CrudOptions
    copy: CrudOptions
    delete: CrudOptions
    io: CrudOptions
    reload: CrudOptions
    support: CrudOptions


DEFAULT_BUTTONBAR_CONFIG = CrudView(
    add=CrudOptions(
        **dict(ADD_BUTTON_KWARGS)
        | dict(
            tooltip="Add item",
            tooltip_clicked="Go back to table",
            button_style="success",
            message="➕ <i>Adding Value</i>",
        )
    ),
    edit=CrudOptions(
        **dict(EDIT_BUTTON_KWARGS)
        | dict(
            tooltip="Edit item",
            tooltip_clicked="Go back to table",
            button_style="warning",
            message="✏️ <i>Editing Value</i>",
        )
    ),
    copy=CrudOptions(
        **dict(COPY_BUTTON_KWARGS)
        | dict(
            tooltip="Copy item",
            tooltip_clicked="Go back to table",
            button_style="primary",
            message="📝 <i>Copying Value</i>",
        )
    ),
    delete=CrudOptions(
        **dict(DELETE_BUTTON_KWARGS)
        | dict(
            tooltip="Delete item",
            tooltip_clicked="Go back to table",
            button_style="danger",
            message="🗑️ <i>Deleting Value</i>",
        )
    ),
    io=CrudOptions(
        **dict(IO_BUTTON_KWARGS)
        | dict(
            tooltip="import/export",
            tooltip_clicked="Go back to table",
            message="🔄 <i>Import / Export</i>",
        )
    ),
    reload=CrudOptions(
        **dict(RELOAD_BUTTON_KWARGS)
        | dict(
            tooltip="reload data",
            tooltip_clicked="",
            button_style="info",
            message="♻ <i>reloading data|</i>",
        )
    ),
    support=CrudOptions(
        **dict(HELP_BUTTON_KWARGS)
        | dict(
            tooltip="help - click to show description of all buttons in the toolbar",
            tooltip_clicked="hide help dialogue",
            message="❔ <i>Help Selected</i>",
        )
    ),
)


# +
def display_ui_tooltips(uiobj: w.DOMWidget) -> w.VBox:
    """Pass a UI object and display all widgets within it with their tooltips."""
    li = []
    for _, v in uiobj.__dict__.items():
        try:
            if "tooltip" in v.__dict__["_trait_values"]:
                if v.tooltip is not None:
                    li.append(v)
        except Exception as err:
            logging.info(err)
    replace_newlines = lambda x: x.replace("\n", "<br>")
    return w.VBox(
        [w.HBox([l, w.HTML(f"<i>{replace_newlines(l.tooltip)}</i>")]) for l in li]
    )


class CrudButtonBar(w.VBox):
    active = tr.Unicode(default_value=None, allow_none=True)
    crud_view = tr.Dict(default_value=DEFAULT_BUTTONBAR_CONFIG)
    fn_add = tr.Callable(default_value=lambda: print("add"))
    fn_edit = tr.Callable(default_value=lambda: print("edit"))
    fn_copy = tr.Callable(default_value=lambda: print("copy"))
    fn_delete = tr.Callable(default_value=lambda: print("delete"))
    fn_backward = tr.Callable(default_value=lambda: print("backward"))
    fn_support = tr.Callable(default_value=lambda: print("support"))
    fn_io = tr.Callable(default_value=lambda: print("io"))
    fn_reload = tr.Callable(default_value=None, allow_none=True)
    show_io = tr.Bool(default_value=False)
    show_support = tr.Bool(default_value=True)

    @tr.observe("show_io")
    def _observe_show_io(self, change):
        if change["new"]:
            self.io.layout.display = ""
        else:
            self.io.layout.display = "None"

    @tr.observe("show_support")
    def _observe_show_support(self, change):
        if change["new"]:
            self.support.layout.display = ""
        else:
            self.support.layout.display = "None"

    @tr.observe("fn_reload")
    def _observe_fn_reload(self, change):
        if change["new"] is None:
            self.reload.layout.display = "None"
        else:
            self.reload.layout.display = ""

    @tr.observe("crud_view")
    def _observe_crud_view(self, change):
        self._set_crud_view_options()

    @property
    def active_index(self):
        if self.active is None:
            return None
        else:
            return list(self.crud_view.keys()).index(self.active)

    def _fn_support(self):
        with self.out:
            clear_output()
            display(display_ui_tooltips(self))

    def __init__(
        self,
        **kwargs,
    ):
        self._init_form()
        super().__init__(**kwargs)  # main container
        self.fn_support = self._fn_support
        self.out = w.Output()
        self.hbx_bbar = w.HBox(
            [
                self.add,
                self.edit,
                self.copy,
                self.delete,
                self.io,
                self.reload,
                self.support,
                self.message,
            ]
        )
        self.children = [self.hbx_bbar, self.out]
        self._init_controls()

    def _init_form(self):
        self.add = w.ToggleButton()
        self.edit = w.ToggleButton()
        self.copy = w.ToggleButton()
        self.delete = w.ToggleButton()
        self.io = w.ToggleButton()
        self.reload = w.Button()
        self.support = w.ToggleButton()
        # ^ KWARGS for the buttons are set by CrudView
        self.message = w.HTML()
        self._set_crud_view_options()
        self.io.layout.display = "" if self.show_io else "None"

    def _init_controls(self):
        self.add.observe(self._add, "value")
        self.edit.observe(self._edit, "value")
        self.copy.observe(self._copy, "value")
        self.delete.observe(self._delete, "value")
        self.io.observe(self._io, "value")
        self.support.observe(self._support, "value")
        self.reload.on_click(self._reload)

    def _onclick(self, button_name):
        wi = getattr(self, button_name)
        fn = getattr(self, ("fn_" + button_name))
        if wi.value:
            self.reset_toggles_except(button_name)
            self.active = button_name
            wi.tooltip = self.crud_view[button_name]["tooltip_clicked"]
            wi.layout.border = TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT
            self.message.value = self.crud_view[button_name]["message"]
            fn()
        else:
            self.active = None
            wi.tooltip = self.crud_view[button_name]["tooltip"]
            wi.layout.border = None
            self.message.value = ""
            self.fn_backward()
            with self.out:
                clear_output()

    def _add(self, onchange):
        self._onclick("add")

    def _edit(self, onchange):
        self._onclick("edit")

    def _copy(self, onchange):
        self._onclick("copy")

    def _delete(self, onchange):
        self._onclick("delete")

    def _support(self, onchange):
        self._onclick("support")

    def _io(self, onchange):
        self._onclick("io")

    def _reload(self, on_click):
        logger.info("Reloading all data")
        self.fn_reload()

    def _set_crud_view_options(self):
        for button_name in self.crud_view.keys():
            w = getattr(self, button_name)
            for k, v in self.crud_view[button_name].items():
                if k in dir(w):
                    setattr(w, k, self.crud_view[button_name][k])

    def reset_toggles_except(self, name=None):
        names = self.crud_view.keys()
        if name is None:
            names = names
        elif name not in names:
            raise ValueError(f"`name` must be in {str(names)}. {name} given")
        names = [n for n in names if n != name]
        for n in names:
            setattr(getattr(self, n), "value", False)


# +
# len(DEFAULT_BUTTONBAR_CONFIG)
# -

if __name__ == "__main__":

    def add():
        print("ADD")

    def edit():
        print("EDIT")

    def copy():
        print("COPY")

    def delete():
        print("DELETE")

    def backward():
        print("BACK")

    def io():
        print("IO")

    buttonbar = CrudButtonBar(
        fn_add=add,
        fn_edit=edit,
        fn_copy=copy,
        fn_delete=delete,
        fn_backward=backward,
        fn_io=io,
        fn_reload=lambda: print("fn_reload"),
    )
    display(buttonbar)
