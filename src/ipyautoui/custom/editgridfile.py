from ipyautoui.custom.editgrid import (
    EditGrid,
    DataHandler,
)
from ipyautoui.custom.edittsv import Changes
import pathlib
import traitlets as tr
import json
from pydantic import BaseModel, RootModel, Field
import typing as ty
import ipywidgets as w
import functools


# +
# --- LOAD & SAVE HELPERS ---
def load_json(fpth: pathlib.Path = pathlib.Path("text.json")) -> list[dict]:
    """Load JSON list data safely."""
    with fpth.open("r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Expected list of dicts in JSON file.")
        return data


def save_json(data: list[dict], fpth: pathlib.Path) -> pathlib.Path:
    """Save JSON list data safely."""
    with fpth.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return fpth


# --- DELETE ---
def delete_rows(primary_keys_list: list[str | int], primary_key_name, fpth: pathlib.Path) -> list[dict]:
    """Delete rows from JSON based on keys in 'primary_keys' (list of strings or ints)."""
    data = load_json(fpth)

    # Normalize all keys to strings for consistent comparison
    delete_keys = [str(k) for k in primary_keys_list]

    # Keep only rows whose 'primary_key_name' is NOT in delete_ids
    updated_data = [row for row in data if str(row.get(primary_key_name)) not in delete_keys]

    save_json(updated_data, fpth)
    print(f"🗑️ Deleted rows with IDs: {delete_keys}")
    return updated_data


# --- ADD ---
def add_rows(additions: list[dict], primary_key_name = "id", fpth: pathlib.Path = pathlib.Path("text.json")) -> list[dict]:
    """Add new rows from 'insert' (dict-of-dicts form)."""
    data = load_json(fpth)
    maxId = max(data, key=lambda x:x[primary_key_name])[primary_key_name]

    for addition in additions:
        new_addition = {}
        new_addition[primary_key_name] = maxId + 1
        addition.pop(primary_key_name, None)
        new_addition.update(addition)
        data.append(new_addition)

    save_json(data, fpth)
    print(f"➕ Added {len(additions)} new row(s)")
    return data


# --- EDIT ---
def edit_rows(edits: dict[str | int, dict], primary_key_name, fpth: pathlib.Path) -> list[dict]:
    """Update existing rows based on 'update' section."""
    data = load_json(fpth)

    for key, update_fields_dict in edits.items():
        for record in data:
            if str(record.get(primary_key_name)) == str(key):
                record.update(update_fields_dict)

    save_json(data, fpth)
    print(f"✏️ Updated {len(edits)} row(s)")
    return data


# --- COMBINED HANDLER ---
def handle_crud(primary_key_name, changes: Changes, fpth: pathlib.Path):
    """Apply delete → insert → update in order."""
    if changes.deletions:
        delete_rows(changes.deletions, primary_key_name, fpth)
    if changes.additions:
        add_rows(changes.additions, primary_key_name, fpth)
    if changes.edits:
        edit_rows(changes.edits, primary_key_name, fpth)
# --- COMBINED HANDLER ---

def delete_row(value: dict, primary_key_name = "id", fpth: pathlib.Path = pathlib.Path("text.json")) -> list[dict]:
    data = load_json(fpth)
    deleted_id = value[primary_key_name]
    # Keep only rows whose 'primary_key_name' is NOT delete_id
    updated_data = [row for row in data if str(row.get(primary_key_name)) != str(deleted_id)]
    save_json(updated_data, fpth)
    return updated_data

def edit_row(value: dict, primary_key_name = "id", fpth: pathlib.Path = pathlib.Path("text.json")) -> list[dict]:
    data = load_json(fpth)
    row_id = value[primary_key_name]

    # Update matching record
    for record in data:
        if str(record.get(primary_key_name)) == str(row_id):
            # update all keys except 'primary_key_name'
            record.update({k: v for k, v in value.items() if k != primary_key_name})
            break

    save_json(data, fpth)
    return data

def add_row(addition: dict, primary_key_name = "id", fpth: pathlib.Path = pathlib.Path("text.json")) -> list[dict]:
    data = load_json(fpth)
    maxId = max(data, key=lambda x:x[primary_key_name])[primary_key_name]
    new_addition = {}
    new_addition[primary_key_name] = maxId + 1
    addition.pop(primary_key_name, None)
    new_addition.update(addition)
    data.append(new_addition)
    save_json(data, fpth)
    print(f"➕ Added new row")
    return data

class EditGridFile(EditGrid):
    primary_key_name = tr.Unicode(default_value="id")
    fpth = tr.Instance(klass=pathlib.Path, allow_none=False)

    @tr.observe("fpth")
    def update_handler(self, change):       
        self.datahandler.fn_get_all_data = functools.partial(load_json, fpth=self.fpth)
        self.datahandler.fn_post = functools.partial(add_row, primary_key_name=self.primary_key_name, fpth=self.fpth)
        self.datahandler.fn_patch = functools.partial(edit_row, primary_key_name=self.primary_key_name, fpth=self.fpth)
        self.datahandler.fn_delete = functools.partial(delete_row, primary_key_name=self.primary_key_name, fpth=self.fpth)
        self.datahandler.fn_copy = functools.partial(add_row, primary_key_name=self.primary_key_name, fpth=self.fpth)
        self.datahandler.fn_io = functools.partial(self.handle_crud)

        self._set_datahandler(self.datahandler)
        
    def __init__(
        self,
        **kwargs,
    ):
        
        datahandler = DataHandler(
            fn_get_all_data=lambda v: print(v),
            fn_post=lambda v: print(v),
            fn_patch=lambda v: v,
            fn_delete=lambda v: print(v),
            fn_copy=lambda v: print(v),
            fn_io = lambda v: print("io")
        )        
        super().__init__(
            datahandler=datahandler,
            warn_on_delete=True,
            layout=w.Layout(height="800px"),
            **kwargs,
        )

        if hasattr(self, "ui_io") and hasattr(self.ui_io, "primary_key_name"):
            self.ui_io.primary_key_name = self.primary_key_name

        self.update_handler("")

    def fn_upload(self, value):
        self.value=value
        if self.ui_io is not None:
            self.datahandler.fn_io(self.ui_io.changes)

    # --- HANDLERS ---
    def handle_crud(self, changes: Changes):
        handle_crud(self.ui_io.primary_key_name, changes, self.fpth)


if __name__ == "__main__":
    json_path = pathlib.Path("../../..") / "tests" / "test_data" / "edit-grid-file-data.json"
    with json_path.open('r', encoding='utf-8') as file:
        data = json.load(file)
                     
    # Test: EditGrid instance with multi-indexing.
    AUTO_GRID_DEFAULT_VALUE = data

    class DataFrameCols(BaseModel):
        id: int = Field(1, json_schema_extra=dict(column_width=80, section="a"))
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

    title = "Testing Crud Info Grid"
    description = "Useful for all editing purposes whatever they may be 👍"
    edit_grid_file = EditGridFile(
        schema=TestDataFrame,
        title=title,
        description=description,
        ui_add=None,
        ui_edit=None,
        show_copy_dialogue=False,
        close_crud_dialogue_on_action=False,
        global_decimal_places=1,
        column_width={"String": 400},
        fpth=json_path,
        show_ui_io=True
    )
    display(edit_grid_file)




# -


