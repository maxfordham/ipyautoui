from deepdiff import DeepDiff
from pydantic import RootModel, create_model
from ipyautoui.custom.edittsv import Changes, EditTsvWithDiff
import traitlets as tr
import typing as ty

class EditTsvWithDiffAndKeyMapping(EditTsvWithDiff):
    primary_key_name = tr.List(tr.Unicode(),
        default_value=None,
        allow_none=True,
    )
    exclude_fields_from_model = tr.List(tr.Unicode(), default_value=[])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.exclude_fields_from_model:
            inner_model = self.model.model_fields['root'].annotation.__args__[0]
            # Keep alias names in the new model
            fields = {}
            for name, field in inner_model.model_fields.items():
                converted_name = field.alias or name
                if converted_name not in self.exclude_fields_from_model:
                    alias = field.alias or name
                    fields[alias] = (field.annotation, field.default)

            stripped_inner = create_model(
                inner_model.__name__,
                **fields,
            )
            self.model = type(
                self.model.__name__,
                (RootModel[list[stripped_inner]],),
                {},
            )
    
    def _bn_upload_text(self, on_click):
        # hide grid/errors
        self.text.layout.display = "None"

        # Hide upload button and show check button
        self.bn_upload_text.layout.display = "None"
        self.bn_confirmation.layout.display = ""
        self.bn_confirmation.disabled = False
        self.bn_confirmation.button_style = "success"
        self.bn_cross.layout.display = ""
        self.bn_cross.disabled = False
        self.bn_cross.button_style = "danger"
        
        # Show DeepDiff widget
        self.ddiff.layout.display = ""

        def build_diff_map(records):
            result = {}
            for i, v in enumerate(records or []):
                # --- Determine key ---
                if self.primary_key_name:
                    # Replace None with "" and filter out empty parts
                    parts = [str(v.get(f) or "") for f in self.primary_key_name]
                    non_empty_parts = [p for p in parts if p]  # remove empty strings
                    key = "-".join(non_empty_parts)
                    # --- Normalize None → "" for values ---
                    clean_row = {
                        k: ("" if val is None else val)
                        for k, val in v.items()
                    }
                    result[key] = clean_row
            return result
        
        self.ddiff.value = build_diff_map(self.prev_value or [])
        self.ddiff.new_value = build_diff_map(self.value or [])
        
    def deepdiff_to_crud(self, diff: DeepDiff):
        """Convert DeepDiff result into CRUD Changes."""
        changes = Changes(
            deletions=[],
            edits={},
            additions=[],
            edited_rows={}
        )

        # Helper for consistent key resolution
        def key_from_path(path_list):
            key = path_list[0]
            if isinstance(key, (list, tuple)):
                key = "::".join(map(str, key))
            return str(key)

        # Additions
        if "dictionary_item_added" in diff:
            for delta in diff["dictionary_item_added"]:
                changes.additions.append(getattr(delta, "t2", None))

        # Deletions
        if "dictionary_item_removed" in diff:
            for delta in diff["dictionary_item_removed"]:
                path_list = delta.path(output_format="list")
                primary_key = key_from_path(path_list)
                changes.deletions.append(primary_key)

        # Edits / type changes
        for category in ("values_changed", "type_changes"):
            if category not in diff:
                continue
            for delta in diff[category]:
                path_list = delta.path(output_format="list")
                primary_key = key_from_path(path_list)
                field = path_list[-1]
                if primary_key not in changes.edits:
                    changes.edits[primary_key] = {}
                changes.edits[primary_key][field] = delta.t2
        
        #Adding edited_rows (all the fields included for edited rows)
        if len(changes.edits):
            if self.primary_key_name:
                # Composite key mode
                for comp_key in changes.edits.keys():
                    for row in self.value:
                        row_key = self._composite_key_from_row(row)
                        if row_key and str(row_key) == str(comp_key):
                            changes.edited_rows[comp_key] = row
                            break

        return changes
    
    def _composite_key_from_row(self, row: dict) -> str:
        """Build a composite key string from the configured primary key fields."""
        if not row:
            return ""
        fields = getattr(self, "primary_key_name", None) or []
        parts = []
        for field in fields:
            value = row.get(field)
            if value is None:
                continue
            value_str = str(value)
            if value_str:
                parts.append(value_str)
        return "-".join(parts)
    
    def _composite_key_for_id(self, Id: ty.Union[int, str], key_to_id_map: dict[str, int]) -> str:  # noqa: N803
        try:
            target_id = int(Id)
        except (TypeError, ValueError):
            return ""

        for composite_key, mapped_id in key_to_id_map.items():
            try:
                if int(mapped_id) == target_id:
                    return composite_key
            except (TypeError, ValueError):
                continue
        return ""
    
    def _build_composite_key_to_id_map(
        self, data: ty.Union[list[dict], tuple[dict, ...]]
    ) -> dict[str, int]:
        """Build mapping from composite key to the actual database Id."""
        mapping = {}
        for row in data:
            key = self._composite_key_from_row(row)
            if "Id" in row and key:
                mapping[key] = row["Id"]
        return mapping
    
    def _resolve_composite_to_ids(self, changes: Changes, key_to_id_map: dict[str, int]) -> Changes:
        """Translate composite keys from Changes to actual database Ids."""
        resolved = Changes(
            deletions=[],
            edits={},
            additions=changes.additions,
            edited_rows={}
        )
        
        # Resolve deletions
        for comp_key in changes.deletions:
            id_ = key_to_id_map.get(comp_key)
            if id_ is not None:
                resolved.deletions.append(id_)

        # Resolve edits
        for comp_key, edit in changes.edits.items():
            id_ = key_to_id_map.get(comp_key)
            if id_ is not None:
                resolved.edits[id_] = edit

        # --- Resolve edited_rows ---
        for comp_key, row in changes.edited_rows.items():
            id_ = key_to_id_map.get(comp_key)
            if id_ is not None:
                resolved.edited_rows[id_] = row

        return resolved