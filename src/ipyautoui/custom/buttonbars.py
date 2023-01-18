# ---
# jupyter:
#   jupytext:
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
# %run __init__.py
# %load_ext lab_black

import ipywidgets as w
import traitlets as tr
import typing as ty
from ipyautoui.constants import (
    BUTTON_WIDTH_MIN,
    TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT,
)

from IPython.display import display
from datetime import datetime
from markdown import markdown
import logging
from enum import Enum

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
        print_fns_onsave = lambda: print(s)
        print_fns_onsave.__name__ = "print_fns_onsave"
        return [log_fns_onsave, print_fns_onsave]

    @tr.default("fns_onrevert")
    def _default_fn_revert(self):
        s = f"log_fns_onrevert - action called @ {datetime.now().strftime('%H:%M:%S')}"
        log_fns_onrevert = lambda: logging.info(s)
        log_fns_onrevert.__name__ = "log_fns_onrevert"
        print_fns_onrevert = lambda: print(s)
        print_fns_onrevert.__name__ = "print_fns_onrevert"
        return [log_fns_onrevert, print_fns_onrevert]

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
        setattr(self, action_name, fns + [fn_add])

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


if __name__ == "__main__":
    actions = SaveActions()
    f = lambda: print("test")
    f.__name__ = "asdf"
    f1 = lambda: print("test1")
    f1.__name__ = "asdf"

    actions.fns_onsave_add_action(f)
    actions.fns_onsave_add_action(f1)
    actions.fn_save()

    actions.fns_onrevert_add_action(f)
    actions.fns_onrevert_add_action(f1)
    actions.fn_revert()


# +
class SaveButtonBar(w.HBox, SaveActions):
    def __init__(self, **kwargs):
        super().__init__()
        self._init_form()
        self._init_controls()
        [setattr(self, k, v) for k, v in kwargs.items()]

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
        self.message.value = markdown(
            f'_changes saved: {datetime.now().strftime("%H:%M:%S")}_'
        )
        self.unsaved_changes = False

    def _revert(self, click):
        self.fn_revert()
        self.message.value = markdown(f"_UI reverted to last save_")
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
    sb.unsaved_changes = True

# TODO: move into editgrid_buttonbar.py


# +
BUTTONBAR_CONFIG = {
    "add": {
        "tooltip": "add item",
        "tooltip_clicked": "Go back to table",
        "button_style": "success",
        "message": "  ➕ _Adding Value_ ",
    },
    "edit": {
        "tooltip": "edit item",
        "tooltip_clicked": "Go back to table",
        "button_style": "success",
        "message": "  ✏️ _Editing Value_ ",
    },
    "copy": {
        "tooltip": "copy item",
        "tooltip_clicked": "Go back to table",
        "button_style": "success",
        "message": "  📝 _Copying Value_ ",
    },
    "delete": {
        "tooltip": "delete item",
        "tooltip_clicked": "Go back to table",
        "button_style": "success",
        "message": "  🗑️ _Deleting Value_ ",
    },
}


class StrEnum(str, Enum):
    pass


CrudView = StrEnum(
    "CrudView", {l: n for n, l in enumerate(list(BUTTONBAR_CONFIG.keys()))}
)


# -


class CrudButtonBar(w.HBox):
    active = tr.UseEnum(CrudView, allow_none=True, default_value=None)

    @tr.observe("active")
    def _observe_active(self, change):
        if change["new"] is None:
            self.message.value = ""
        print(change["new"])
        print(self.message.value)

    def __init__(
        self,
        # transpose: # TODO: add transpose datagrid button
        add: ty.Callable = lambda: print("add"),
        edit: ty.Callable = lambda: print("edit"),
        copy: ty.Callable = lambda: print("copy"),
        delete: ty.Callable = lambda: print("delete"),
        backward: ty.Callable = lambda: print("backward"),
        show_message: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)  # main container
        self.show_message = show_message
        self.fn_add = add
        self.fn_edit = edit
        self.fn_copy = copy
        self.fn_delete = delete
        self.fn_backward = backward
        self.out = w.Output()
        self._init_form()
        self._init_controls()

    def _init_form(self):
        # self.transpose w.ToggleButton(icon="arrow-right")
        self.add = w.ToggleButton(
            icon="plus",
            button_style="success",
            style={"font_weight": "bold"},
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.edit = w.ToggleButton(
            icon="edit",
            button_style="warning",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.copy = w.ToggleButton(
            icon="copy",
            button_style="primary",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.delete = w.ToggleButton(
            icon="trash-alt",
            button_style="danger",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.message = w.HTML()
        self.children = [self.add, self.edit, self.copy, self.delete, self.message]

    def _init_controls(self):
        self.add.observe(self._add, "value")
        self.edit.observe(self._edit, "value")
        self.copy.observe(self._copy, "value")
        self.delete.observe(self._delete, "value")

    def _onclick(self, button_name):
        w = getattr(self, button_name)
        fn = getattr(self, ("fn_" + button_name))
        if w.value:
            self.reset_toggles_except(button_name)
            self.active = button_name
            w.tooltip = BUTTONBAR_CONFIG[button_name]["tooltip_clicked"]
            w.layout.border = TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT
            self.message.value = markdown(BUTTONBAR_CONFIG[button_name]["message"])
            fn()
        else:
            self.active = None
            # self.message.value = ""
            w.tooltip = BUTTONBAR_CONFIG[button_name]["tooltip"]
            w.layout.border = None
            self.fn_backward()
        print(self.message.value)

    def _add(self, onchange):
        self._onclick("add")

    def _edit(self, onchange):
        self._onclick("edit")

    def _copy(self, onchange):
        self._onclick("copy")

    def _delete(self, onchange):
        self._onclick("delete")

    def reset_toggles_except(self, name):
        names = ["add", "edit", "delete", "copy"]
        if name not in names:
            raise ValueError(f"`name` must be in {str(names)}. {name} given")
        names = [n for n in names if n != name]
        for n in names:
            setattr(getattr(self, n), "value", False)


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

    buttonbar = CrudButtonBar(
        add=add,
        edit=edit,
        copy=copy,
        delete=delete,
        backward=backward,
    )

    display(buttonbar)