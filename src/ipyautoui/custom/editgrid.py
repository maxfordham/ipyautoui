# +
"""General widget for editing data"""


# TODO: move editgrid.py to root ?

import traitlets as tr
import typing as ty
import logging
import traceback
import pandas as pd
import ipywidgets as w
from IPython.display import clear_output, display
from pydantic import BaseModel, RootModel, Field
import json

from ipyautoui.autoobject import AutoObjectForm
from ipyautoui.custom.buttonbars import CrudButtonBar
from ipyautoui._utils import frozenmap, traits_in_kwargs
from ipyautoui.constants import BUTTON_WIDTH_MIN
from ipyautoui.custom.autogrid import AutoGrid
from ipyautoui.custom.edittsv import EditTsvWithDiff
from ipyautoui.custom.title_description import TitleDescription

MAP_TRANSPOSED_SELECTION_MODE = frozenmap({True: "column", False: "row"})
logger = logging.getLogger(__name__)
# TODO: rename "add" to "fn_add" so not ambiguous...
# -


class DataHandler(BaseModel):
    """CRUD operations for a for EditGrid.
    Can be used to connect to a database or other data source.
    note - the TypeHints below are hints only. The functions can be any callable.

    Args:
        fn_get_all_data (Callable): Function to get all data.
        fn_post (Callable): Function to post data. is passed a dict of a single row/col to post.
            Following the post, fn_get_all_data is called
        fn_patch (Callable): Function to patch data. is passed a dict of a single row/col to patch.
        fn_delete (callable): Function to delete data. is passed the index of the row/col to delete.
        fn_copy (Callable): Function to copy data. is passed a list of dicts with values of rows/cols to copy.
    """

    # REVIEW... MAYBE SHOULD USE *ARGS AND **KWARGS
    fn_get_all_data: ty.Callable  # TODO: rename to fn_get
    fn_post: ty.Callable[[dict], None] # should return int
    fn_patch: ty.Callable[[ty.Any, dict], None]  # TODO: need to add index
    fn_delete: ty.Callable[[list[int]], None]
    fn_copy: ty.Callable[[list[int]], None]
    fn_io: ty.Optional[ty.Callable] = None


if __name__ == "__main__":
    from ipyautoui.demo_schemas import EditableGrid
    from ipyautoui.demo_schemas.editable_datagrid import DataFrameCols

    ui = AutoObjectForm.from_pydantic_model(DataFrameCols)
    display(ui)

if __name__ == "__main__":
    ui.show_savebuttonbar = True
    display(ui.value)

if __name__ == "__main__":
    ui.value = {"string": "adfs", "integer": 2, "floater": 1.22}


class UiDelete(w.VBox):
    value = tr.Dict(default_value={})
    columns = tr.List(default_value=[])

    @tr.observe("value")
    def observe_value(self, on_change):
        self._update_display()

    @tr.observe("columns")
    def observe_columns(self, on_change):
        if self.columns:
            self.message_columns.value = f"columns shown: {str(self.columns)}"
        else:
            self.message_columns.value = ""
        self._update_display()

    @property
    def value_summary(self):
        if self.columns:
            return {
                k: {k_: v_ for k_, v_ in v.items() if k_ in self.columns}
                for k, v in self.value.items()
            }
        else:
            return self.value

    def _update_display(self):
        with self.out_delete:
            clear_output()
            display(self.value_summary)

    def __init__(self, fn_delete: ty.Callable = lambda: print("delete"), **kwargs):
        super().__init__(**kwargs)
        self.fn_delete = fn_delete
        self.out_delete = w.Output()
        self.bn_delete = w.Button(
            description="DELETE",
            button_style="danger",
            layout=w.Layout(width="100px"),
        )
        self.vbx_messages = w.VBox()
        self.message = w.HTML(
            "⚠️<b>Are you sure you want to delete?</b>⚠️ - <i>Pressing the button will"
            " permanently delete the selected data</i>"
        )
        self.message_columns = w.HTML(f"")
        self.vbx_messages.children = [
            self.message,
            self.message_columns,
            self.out_delete,
        ]
        self.children = [self.bn_delete, self.vbx_messages]
        self._init_controls()

    def _init_controls(self):
        self.bn_delete.on_click(self._bn_delete)

    def _bn_delete(self, onclick):
        self.fn_delete()


if __name__ == "__main__":
    delete = UiDelete()
    display(delete)
# -

if __name__ == "__main__":
    delete.value = {"key": {"col1": "value1", "col2": "value2"}}


# +
# NOTE: UiCopy not in use


class UiCopy(w.HBox):
    index = tr.Integer()  # row index copying from... improve user reporting

    def __init__(
        self,
        fn_copy_beginning: ty.Callable = lambda: print(
            "duplicate selection to beginning"
        ),
        fn_copy_inplace: ty.Callable = lambda: print(
            "duplicate selection to below current"
        ),
        fn_copy_end: ty.Callable = lambda: print("duplicate selection to end"),
        fn_copy_to_selection: ty.Callable = lambda: print(
            "select new row/col to copy to"
        ),
        transposed: bool = False,
    ):
        super().__init__()
        self.fn_copy_beginning = fn_copy_beginning
        self.fn_copy_inplace = fn_copy_inplace
        self.fn_copy_end = fn_copy_end
        self.fn_copy_to_selection = fn_copy_to_selection
        self.map_action = {
            "duplicate selection to beginning": self.fn_copy_beginning,
            "duplicate selection to below current": self.fn_copy_inplace,
            "duplicate selection to end": self.fn_copy_end,
            "select new row/col to copy to": self.fn_copy_to_selection,
        }
        self.ui_copytype = w.RadioButtons(
            options=list(self.map_action.keys()),
            value="duplicate selection to end",
        )
        self.bn_copy = w.Button(
            icon="copy",
            button_style="success",
            layout=w.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.vbx_messages = w.VBox()
        self.message = w.HTML("ℹ️ <b>Note</b> ℹ️ - <i>copy data from selected row")
        self.message_columns = w.HTML(f"---")
        self.vbx_messages.children = [
            self.message,
            self.message_columns,
            self.ui_copytype,
        ]
        self.children = [self.bn_copy, self.vbx_messages]
        self._init_controls()

    def _init_controls(self):
        self.bn_copy.on_click(self._bn_copy)

    def _bn_copy(self, onclick):
        self.map_action[self.ui_copytype.value]()


if __name__ == "__main__":
    display(UiCopy())

# +
# TODO: refactor how the datahandler works...
# TODO: add a test for the datahandler...

# from ipyautoui.watch_validate import WatchValidate
class EditGrid(w.VBox, TitleDescription):
    _value = tr.Tuple()  # using a tuple to guarantee no accidental mutation
    warn_on_delete = tr.Bool()
    show_copy_dialogue = tr.Bool()
    close_crud_dialogue_on_action = tr.Bool()
    show_ui_io = tr.Bool(default_value=False)

    @tr.observe("warn_on_delete")
    def observe_warn_on_delete(self, on_change):
        if self.warn_on_delete:
            self.ui_delete.layout.display = ""
        else:
            self.ui_delete.layout.display = "None"

    @tr.observe("show_copy_dialogue")
    def observe_show_copy_dialogue(self, on_change):
        if self.show_copy_dialogue:
            self.ui_copy.layout.display = ""
        else:
            self.ui_copy.layout.display = "None"
    
    @property
    def json(self):  # HOTFIX: not required if WatchValidate is used
        return json.dumps(self.value, indent=4)

    @property
    def transposed(self):
        return self.grid.transposed

    @transposed.setter
    def transposed(self, value: bool):
        self.grid.transposed = value
        if getattr(self, "ui_io", None) is not None:
            if "transposed" in self.ui_io.traits():
                self.ui_io.transposed = value
            else:
                logger.warning("transposed not found in ui_io")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self.grid.data = self.grid._init_data(pd.DataFrame(value))

        # HOTFIX: Setting data creates bugs out transforms currently so reset transform applied
        _transforms = self.grid._transforms
        self.grid.transform([])  # Set to no transforms
        self.grid.transform(_transforms)  # Set to previous transforms

    @property
    def schema(self):
        return self.grid.schema

    @property
    def row_schema(self):
        return self.grid.schema["items"]

    @property
    def model(self):
        return self.grid.model

    # TODO: this is a bit of a hack... need to refactor when EditGrid inherits WatchValidate
    @classmethod
    def from_pydantic_model(cls, model: ty.Type[BaseModel], **kwargs):
        return cls(model, **kwargs)

    def __init__(
        self,
        schema: ty.Optional[ty.Union[dict, ty.Type[BaseModel]]] = None,
        value: ty.Optional[list[dict[str, ty.Any]]] = None,
        by_alias: bool = False,
        by_title: bool = True,
        datahandler: ty.Optional[DataHandler] = None,
        ui_add: ty.Optional[ty.Callable] = None,
        ui_edit: ty.Optional[ty.Callable] = None,
        ui_delete: ty.Optional[ty.Callable] = None,
        ui_copy: ty.Optional[ty.Callable] = None,
        ui_io: ty.Optional[ty.Callable] = None,
        warn_on_delete: bool = False,
        show_copy_dialogue: bool = False,
        close_crud_dialogue_on_action: bool = False,
        title: str = None,
        description: str = None,
        show_title: bool = True,
        generate_pydantic_model_from_json_schema: bool = False,
        show_ui_io: bool = False,
        **kwargs,
    ):  # TODO: use **kwargs to pass attributes to EditGrid as in AutoObject and AutoArray
        self.vbx_error = w.VBox()
        self.vbx_widget = w.VBox(layout={"width": "100%"})
        # TODO: ^ move common container attributes to WatchValidate
        self.description = description
        self.title = title
        self.show_title = show_title
        self.by_title = by_title
        self.by_alias = by_alias
        self.datahandler = datahandler
        self.generate_pydantic_model_from_json_schema = generate_pydantic_model_from_json_schema

        self.ui_io = None
        self._ui_io_factory = None
        self.show_ui_io = show_ui_io
        self.ui_io_initialised = False

        self.close_crud_dialogue_on_action = close_crud_dialogue_on_action
        self._init_autogrid(schema, value, **kwargs)
        self._init_ui_callables(
            ui_add=ui_add, ui_edit=ui_edit, ui_delete=ui_delete, ui_copy=ui_copy, ui_io=ui_io
        )
        self._init_form()
        self._init_row_controls()
        self._init_controls()
        super().__init__(
            **{
                k: v
                for k, v in kwargs.items()
                if k not in traits_in_kwargs(AutoGrid, kwargs)
            }
        )  # NOTE: Only pass kwargs not in AutoGrid traits
        self.warn_on_delete = warn_on_delete
        # self.show_copy_dialogue = show_copy_dialogue
        self.show_copy_dialogue = False
        # ^ TODO: delete this when that functionality is added
        self._set_children_editgrid()
        self._set_datahandler(datahandler=datahandler)
        self._update_value_from_grid()

    def update_from_schema(
        self,
        schema: ty.Optional[ty.Union[dict, ty.Type[BaseModel]]] = None,
        value: ty.Optional[list[dict[str, ty.Any]]] = None,
        datahandler: ty.Optional[DataHandler] = None,
        ui_add: ty.Optional[ty.Callable] = None,
        ui_edit: ty.Optional[ty.Callable] = None,
        ui_delete: ty.Optional[ty.Callable] = None,
        ui_copy: ty.Optional[ty.Callable] = None,
        ui_io: ty.Optional[ty.Callable] = None,
        **kwargs,
    ):
        getvalue = lambda value: (
            None if value is None or value == [{}] else pd.DataFrame(value)
        )
        self.grid.update_from_schema(
            schema, data=getvalue(value), by_alias=self.by_alias, generate_pydantic_model_from_json_schema=self.generate_pydantic_model_from_json_schema, **kwargs
        )
        self._init_ui_callables(
            ui_add=ui_add, ui_edit=ui_edit, ui_delete=ui_delete, ui_copy=ui_copy, ui_io=ui_io
        )
        self._init_ui_io(ui_io=ui_io)
        self._init_row_controls()
        self._init_controls()
        self._set_children_editgrid()
        self._set_datahandler(datahandler=datahandler)

    def _init_autogrid(
        self,
        schema: ty.Union[dict, ty.Type[BaseModel]],
        value: ty.Optional[list[dict[str, ty.Any]]],
        **kwargs,
    ):
        getvalue = lambda value: (
            None if value is None or value == [{}] else pd.DataFrame(value)
        )
        self.grid = AutoGrid(
            schema, data=getvalue(value), generate_pydantic_model_from_json_schema=self.generate_pydantic_model_from_json_schema, by_alias=self.by_alias, **kwargs
        )

    def _init_ui_callables(
        self,
        ui_add: ty.Optional[ty.Callable] = None,
        ui_edit: ty.Optional[ty.Callable] = None,
        ui_delete: ty.Optional[ty.Callable] = None,
        ui_copy: ty.Optional[ty.Callable] = None,
        ui_io: ty.Optional[ty.Callable] = None,
    ):
        if ui_add is None:
            self.ui_add = AutoObjectForm.from_jsonschema(self.row_schema)
        else:
            self.ui_add = ui_add.from_jsonschema(self.row_schema)
        if ui_edit is None:
            self.ui_edit = AutoObjectForm.from_jsonschema(self.row_schema)
        else:
            self.ui_edit = ui_edit.from_jsonschema(self.row_schema)
        if ui_delete is None:
            self.ui_delete = UiDelete()
        else:
            self.ui_delete = ui_delete()
        self.ui_delete.layout.display = "None"
        if ui_copy is None:
            self.ui_copy = UiCopy()
        else:
            self.ui_copy = ui_copy()
        self.ui_io = None
        self._ui_io_factory = None
        if self.show_ui_io:
            def _missing_model_ui():
                return w.HTML("must instantiate with pydantic model for this feature")

            if ui_io is None:
                def _factory():
                    if self.model is None:
                        return _missing_model_ui()
                    return EditTsvWithDiff(
                        model=self.model, fn_upload=self.fn_upload, transposed=self.transposed
                    )
                self._ui_io_factory = _factory
            else:
                def _factory_custom():
                    if self.model is None:
                        return _missing_model_ui()
                    try:
                        return ui_io(
                            model=self.model, fn_upload=self.fn_upload, transposed=self.transposed
                        )
                    except Exception as e:
                        raise RuntimeError(
                            f"Failed to initialize ui_io '{ui_io.__name__}'."
                            " Required traits are: `model`, `fn_upload`, `transposed`."
                            f" Original error: {e}"
                        ) from e
                self._ui_io_factory = _factory_custom
        self.ui_copy.layout.display = "None"
        self.ui_delete.fn_delete = self._delete_selected

    def _init_ui_io(self, ui_io):
        if ui_io is not None and self.ui_io_initialised:
            self.ui_io = ui_io(
                model=self.model, fn_upload=self.fn_upload, transposed=self.transposed
            )

    def _ensure_ui_io_initialised(self):
        if not self.show_ui_io:
            return None
        if self.ui_io is not None:
            return self.ui_io
        if self._ui_io_factory is None:
            return None
        self.ui_io = self._ui_io_factory()
        if hasattr(self.ui_io, "traits") and "transposed" in self.ui_io.traits():
            self.ui_io.transposed = self.transposed
        self._set_children_editgrid()
        return self.ui_io

    def fn_upload(self, value):
        """This method sets the grid's value to the ui_io value. Override this method to add additional functionality to save changes."""
        self.value=value

    def _init_row_controls(self):
        self.ui_edit.show_savebuttonbar = True
        self.ui_edit.savebuttonbar.fns_onsave = [self._patch, self._save_edit_to_grid]
        self.ui_edit.savebuttonbar.fns_onrevert = [self._set_ui_edit_to_selected_row]
        self.ui_add.show_savebuttonbar = True
        self.ui_add.savebuttonbar.fns_onsave = [self._post, self._save_add_to_grid]
        self.ui_add.savebuttonbar.fns_onrevert = [self._set_ui_add_to_default_row]

    def _init_form(self):
        get_reload = lambda: (
            None if self.datahandler is None else self._reload_datahandler
        )
        self.buttonbar_grid = CrudButtonBar(
            fn_add=self._add,
            fn_edit=self._edit,
            fn_copy=self._copy,
            fn_delete=self._delete,
            fn_reload=get_reload(),
            fn_io=self._io,
            show_io=self.show_ui_io
        )
        self.stk_crud = w.Stack(
            children=[self.ui_add, self.ui_edit, self.ui_copy, self.ui_delete]
        )

    def _init_controls(self):
        self.grid.observe(self._observe_selections, "selections")
        self.grid.observe(self._grid_changed, "count_changes")
        self.buttonbar_grid.observe(self._setview, "active")
        self.grid.observe(self._observe_order, "order")
        self._observe_order(None)  # prompts order if it is set in by grid setter above

    def _update_value_from_grid(self):
        self._value = self.grid.records()

    def _set_datahandler(self, datahandler):
        self.datahandler = datahandler
        if self.datahandler is not None:
            self.buttonbar_grid.fn_reload = self._reload_datahandler

    def _set_children_editgrid(self):
        self.vbx_widget.children = [self.buttonbar_grid, self.stk_crud, self.grid]
    
        # Base CRUD UIs
        children = [self.ui_add, self.ui_edit, self.ui_copy, self.ui_delete]
    
        # Conditionally add ui io
        if self.show_ui_io and self.ui_io is not None:
            children.append(self.ui_io)
    
        self.stk_crud.children = children
        self.children = [self.hbx_title_description, self.vbx_widget]

    def _observe_order(self, on_change):
        if "order" in self.ui_add.traits() and self.grid.order is not None:
            self.ui_add.order = self.grid.order
        if "order" in self.ui_edit.traits() and self.grid.order is not None:
            self.ui_edit.order = self.grid.order

    def _observe_selections(self, onchange):
        if self.grid.selections != []:
            if self.buttonbar_grid.edit.value:
                self._set_ui_edit_to_selected_row()
            if self.buttonbar_grid.delete.value:
                self._set_ui_delete_to_selected_row()

    # @debounce(0.1)  # TODO: make debounce work if too slow...
    def _grid_changed(self, onchange):
        # debouncer used to allow editing whole rows in 1 go
        # without updating the `value` on every cell edit.
        self._update_value_from_grid()

    def _setview(self, onchange):
        if self.buttonbar_grid.active == "io":
            self.ui_io_initialised = True
            self._ensure_ui_io_initialised()
        if self.buttonbar_grid.active is None:
            self.stk_crud.selected_index = None
        elif self.buttonbar_grid.active == "support":
            self.stk_crud.selected_index = None
        else:
            self.stk_crud.selected_index = self.buttonbar_grid.active_index

    def _check_one_row_selected(self):
        if len(self.grid.selected_indexes) > 1:
            raise Exception("👇 <i>Please only select ONLY one row from the table!</i>")

    # edit row
    # --------------------------------------------------------------------------
    def _validate_edit_click(self):
        if len(self.grid.selected_indexes) == 0:
            raise ValueError(
                "you must select an index (row if transposed==True, col if"
                " transposed==True)"
            )
        self._check_one_row_selected()

    def _save_edit_to_grid(self):
        selections = self.grid.selections  # Store current selection
        selected_index = self.grid.selected_index
        self.grid.selections = []
        # ^ HOTFIX: Have to set empty to reselect later on

        if self.datahandler is not None:
            self._reload_all_data()
        else:
            self.grid.set_item_value(selected_index, self.ui_edit.value)

        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.edit.value = False
        else:
            # Reselect previous selection after reload.
            self.grid.selections = selections

    def _set_ui_edit_to_selected_row(self):
        if self.grid.selected is not None:
            self.ui_edit.value = self.grid.selected
        self.ui_edit.savebuttonbar.unsaved_changes = False

    def _patch(self):
        if self.datahandler is not None:
            self.datahandler.fn_patch(self.ui_edit.value)  # TODO: add index

    def _edit(self):
        try:
            self._validate_edit_click()
            self._set_ui_edit_to_selected_row()

        except Exception as e:
            self.buttonbar_grid.edit.value = False
            self.buttonbar_grid.message.value = (
                "👇 <i>Please select one row from the table!</i> "
            )
            traceback.print_exc()

    # --------------------------------------------------------------------------

    # add row
    # --------------------------------------------------------------------------
    def _save_add_to_grid(self):
        if self.datahandler is None:
            if len(self.grid._data["data"]) == 0:  # If no data in grid
                self.value = tuple([self.ui_add.value])
            else:
                # Append new row onto data frame and set to grid's data.
                # Call setter. syntax below required to avoid editing in place.
                self.value = tuple(list(self.value) + [self.ui_add.value])
        else:
            self._reload_all_data()
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.add.value = False

    def _set_ui_add_to_default_row(self):
        if self.ui_add.value == self.grid.default_row:
            self.ui_add.savebuttonbar.unsaved_changes = False
        else:
            self.ui_add.savebuttonbar.unsaved_changes = True

    def _post(self):
        if self.datahandler is not None:
            self.datahandler.fn_post(self.ui_add.value)

    def _add(self):
        self._set_ui_add_to_default_row()

    # --------------------------------------------------------------------------

    # copy
    # --------------------------------------------------------------------------

    def _get_selected_data(self):  # TODO: is this required? is it dupe from DataGrid?
        if self.grid.selected_index is not None:
            li_values_selected = [
                self.value[i] for i in sorted([i for i in self.grid.selected_indexes])
            ]
        else:
            li_values_selected = []
        return li_values_selected

    def _copy_selected_inplace(self):
        pass

    def _copy_selected_to_beginning(self):
        pass

    def _copy_selected_to_end(self):
        self.value = tuple(list(self.value) + self._get_selected_data())
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.copy.value = False

    def _copy(self):
        try:
            if self.grid.selected_indexes == []:
                self.buttonbar_grid.message.value = (
                    "  👇 <i>Please select a row from the table!</i> "
                )
            else:
                if not self.show_copy_dialogue:
                    if self.datahandler is not None:
                        for value in self._get_selected_data():
                            self.datahandler.fn_copy(value)
                        self._reload_all_data()
                    else:
                        self._copy_selected_to_end()
                        # ^ add copied values. note. above syntax required to avoid editing in place.

                    self.buttonbar_grid.message.value = "📝 <i>Copied Data</i> "
                    self.buttonbar_grid.copy.value = False

                else:
                    print("need to implement show copy dialogue")
        except Exception as e:
            self.buttonbar_grid.message.value = (
                "  👇 <i>Please select a row from the table!</i> "
            )
            traceback.print_exc()

    # --------------------------------------------------------------------------

    # delete
    # --------------------------------------------------------------------------
    def _reload_datahandler(self):
        self._reload_all_data()
        self.buttonbar_grid.message.value = "🔄 <i>Reloaded Data</i> "

    def _reload_all_data(self):
        if self.datahandler is not None:
            self.value = self.datahandler.fn_get_all_data()

    def _delete_selected(self):
        if self.datahandler is not None:
            value = [self.value[i] for i in self.grid.selected_indexes]
            for v in value:
                self.datahandler.fn_delete(v)
            self._reload_all_data()
        else:
            self.value = [
                value
                for i, value in enumerate(self.value)
                if i not in self.grid.selected_indexes
            ]
            # ^ Only set for values NOT in self.grid.selected_indexes
        self.buttonbar_grid.message.value = "🗑️ <i>Deleted Data</i> "
        if self.close_crud_dialogue_on_action:
            self.buttonbar_grid.delete.value = False

    def _set_ui_delete_to_selected_row(self):
        logging.info(f"delete: {self.grid.selected_dict}")
        self.ui_delete.value = self.grid.selected_dict

    def _delete(self):
        try:
            if len(self.grid.selected_indexes) > 0:
                if not self.warn_on_delete:
                    self.buttonbar_grid.delete.value = False
                    self._delete_selected()
                else:
                    self.ui_delete.value = self.grid.selected_dict
            else:
                self.buttonbar_grid.delete.value = False
                self.buttonbar_grid.message.value = (
                    "👇 <i>Please select at least one row from the table!</i>"
                )

        except Exception as e:
            print("delete error")
            traceback.print_exc()

    # io
    # --------------------------------------------------------------------------
    def _io(self):
        ui = self._ensure_ui_io_initialised()
        if ui is None:
            self.buttonbar_grid.io.value = False
            self.buttonbar_grid.message.value = (
                "⚠️ <i>Import/Export unavailable for this configuration</i>"
            )
            return
        try:
            ui.value = self.value
        except Exception as exc:
            logger.warning("Unable to sync IO widget value: %s", exc)
        if hasattr(ui, "traits") and "upload_status" in ui.traits():
            ui.upload_status = "None"
        


# -

if __name__ == "__main__":
    from pydantic import RootModel

    # Test: EditGrid instance with multi-indexing.
    AUTO_GRID_DEFAULT_VALUE = [
        {
            "string": "important string",
            "integer": 1,
            "floater": 3.14,
        },
    ]
    AUTO_GRID_DEFAULT_VALUE = AUTO_GRID_DEFAULT_VALUE * 4

    class DataFrameCols(BaseModel):
        string: str = Field(
            "string", json_schema_extra=dict(column_width=400, section="a")
        )
        integer: int = Field(1, json_schema_extra=dict(column_width=80, section="a"))
        floater: float = Field(
            None, json_schema_extra=dict(column_width=70, section="b")
        )

    class TestDataFrame(RootModel):
        """a description of TestDataFrame"""

        root: ty.List[DataFrameCols] = Field(
            default=AUTO_GRID_DEFAULT_VALUE,
            json_schema_extra=dict(
                format="dataframe", datagrid_index_name=("section", "title")
            ),
        )

    title = "The Wonderful Edit Grid Application"
    description = "Useful for all editing purposes whatever they may be 👍"
    editgrid = EditGrid(
        schema=TestDataFrame,
        title=title,
        description=description,
        ui_add=None,
        ui_edit=None,
        warn_on_delete=True,
        show_copy_dialogue=False,
        close_crud_dialogue_on_action=False,
        global_decimal_places=1,
        column_width={"String": 400},
        show_ui_io=True
    )
    editgrid.observe(lambda c: print("_value changed"), "_value")
    display(editgrid)

if __name__ == "__main__":

    class DataFrameCols(BaseModel):
        string: str = Field(
            "string", json_schema_extra=dict(column_width=400, section="a")
        )

    class TestDataFrame(RootModel):
        """a description of TestDataFrame"""

        root: ty.List[DataFrameCols] = Field(
            json_schema_extra=dict(
                format="dataframe", datagrid_index_name=("section", "title")
            ),
        )

    editgrid.update_from_schema(TestDataFrame, value=[{"string": "Test"}] * 10)

if __name__ == "__main__":
    from pydantic import RootModel

    # Test: EditGrid instance with multi-indexing.
    AUTO_GRID_DEFAULT_VALUE = [
        {
            "string": None,
            "integer": 1,
            "floater": 3.14,
        },
    ]
    AUTO_GRID_DEFAULT_VALUE = AUTO_GRID_DEFAULT_VALUE * 4
    AUTO_GRID_DEFAULT_VALUE = AUTO_GRID_DEFAULT_VALUE + [
        {
            "string": None,
            "integer": None,
            "floater": None,
        },
    ]

    class DataFrameCols(BaseModel):
        string: ty.Optional[str] = Field(
            "string",
            json_schema_extra=dict(
                column_width=400,
            ),
        )
        integer: ty.Optional[int] = Field(
            1,
            json_schema_extra=dict(
                column_width=80,
            ),
        )
        floater: ty.Optional[float] = Field(
            None,
            json_schema_extra=dict(
                column_width=70,
            ),
        )

    class TestDataFrame(RootModel):
        """a description of TestDataFrame"""

        root: ty.List[DataFrameCols] = Field(
            default=AUTO_GRID_DEFAULT_VALUE,
            json_schema_extra=dict(
                format="dataframe",
            ),
        )

    title = "The Wonderful Edit Grid Application"
    description = "Useful for all editing purposes whatever they may be 👍"
    editgrid = EditGrid(
        schema=TestDataFrame,
        title=title,
        description=description,
        # transposed=True,
        ui_add=None,
        ui_edit=None,
        warn_on_delete=True,
        show_copy_dialogue=False,
        close_crud_dialogue_on_action=False,
        global_decimal_places=1,
        column_width={"String": 400},
    )
    editgrid.observe(lambda c: print("_value changed"), "_value")
    display(editgrid)

if __name__ == "__main__":
    editgrid.grid.order = ("floater", "string")
    # ^ NOTE: this will result in a value change in the grid


if __name__ == "__main__":
    # list column
    class TestListCol(BaseModel):
        li_col: list[str] = ["a"]
        stringy: str = "as"
        num: int = 1

    class Test(RootModel):
        root: list[TestListCol]

    gr = EditGrid(Test, value=[{"li_col": ["a", "b"], "stringy": "string", "num": 23}])
    display(gr)  # TODO: this needs fixing. not handling the list correctly. 

if __name__ == "__main__":
    import random

    datahandler = DataHandler(
        fn_get_all_data=lambda: AUTO_GRID_DEFAULT_VALUE * random.randint(1, 5),
        fn_post=lambda v: print(v),
        fn_patch=lambda v: v,
        fn_delete=lambda v: print(v),
        fn_copy=lambda v: print(v),
        fn_io = lambda v: print("io")
    )
    title = "The Wonderful Edit Grid Application"
    description = "Useful for all editing purposes whatever they may be 👍"
    editgrid = EditGrid(
        schema=TestDataFrame,
        title=title,
        description=description,
        datahandler=datahandler,
    )
    display(editgrid)

if __name__ == "__main__":

    class DataFrameCols(BaseModel):
        string: str = Field(
            "string", json_schema_extra=dict(column_width=400, section="a")
        )
        integer: int = Field(1, json_schema_extra=dict(column_width=80, section="b"))
        floater: float = Field(
            None, json_schema_extra=dict(column_width=70, section="b")
        )

    class TestDataFrame(RootModel):
        """a description of TestDataFrame"""

        root: ty.List[DataFrameCols] = Field(
            [
                DataFrameCols(
                    string="String",
                    integer=1,
                    floater=2.5,
                ).model_dump()
            ],
            json_schema_extra=dict(
                format="dataframe", datagrid_index_name=("section", "title")
            ),
        )

    description = (
        "<b>The Wonderful Edit Grid Application</b><br>Useful for all editing purposes"
        " whatever they may be 👍"
    )
    editgrid = EditGrid(
        schema=TestDataFrame,
        description=description,
        # transposed=True,
        ui_add=None,
        ui_edit=None,
        warn_on_delete=True,
        by_title=False,
    )
    editgrid.observe(lambda c: print("_value changed"), "_value")
    display(editgrid)

if __name__ == "__main__":
    editgrid.transposed = False


