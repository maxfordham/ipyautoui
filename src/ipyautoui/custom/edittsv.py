# +
import io
import csv
import json
import logging
import ipywidgets as w
import traitlets as tr
from IPython.display import Javascript
from pydantic import BaseModel
from markdown import markdown
from IPython.display import clear_output
from deepdiff import DeepDiff
from deepdiff.helper import COLORED_COMPACT_VIEW  # COLORED_VIEW,
from ipyautoui.custom.filedownload import MakeFileAndDownload
from ipyautoui.custom.fileupload import TempFileUploadProcessor
from copy import deepcopy
import typing as ty
import xlsxdatagrid as xdg
from pathlib import Path

from ipyautoui.constants import BUTTON_WIDTH_MIN


logger = logging.getLogger(__name__)


def data_to_tsv(data):
    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t")

    if data:
        headers = data[0].keys()
        writer.writerow(headers)
        for row in data:
            writer.writerow([row[key] for key in headers])

    tsv_string = output.getvalue()
    return tsv_string

def data_to_tsv_transposed(tsv_string):
    input_io = io.StringIO(tsv_string)
    reader = csv.reader(input_io, delimiter="\t")
    
    rows = list(reader)
    if not rows:
        return ""

    # Transpose using zip
    transposed = list(zip(*rows))

    output = io.StringIO()
    writer = csv.writer(output, delimiter="\t")
    for row in transposed:
        writer.writerow(row)

    return output.getvalue()

def header_from_tsv(tsv_string):
    tsv_file = io.StringIO(tsv_string)
    reader = csv.reader(tsv_file, delimiter="\t")
    return next(reader)  # Read the header row


def data_from_tsv(tsv_string):  # TODO: validate_headings
    """
    Reads TSV data from a string and returns it as a list of dictionaries.
    Each dictionary represents a row, with column headers as keys.

    Args:
        tsv_string (str): A string containing TSV data.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row
              of data from the TSV string.
    """
    data = []
    # Use io.StringIO to treat the string as a file-like object
    tsv_file = io.StringIO(tsv_string)
    reader = csv.reader(tsv_file, delimiter="\t")
    header = next(reader)  # Read the header row
    for row in reader:
        # Create a dictionary for each row, mapping header to row values
        row_dict = dict(zip(header, row))
        data.append(row_dict)
    return data


def markdown_error(e):
    type, url, loc, input, msg = e["type"], e["url"], e["loc"], e["input"], e["msg"]
    return f"❌ **[{type}]({url}) error**: loc(row,col)={loc} | input={input} | msg=*{msg}*"  # TODO: link in new tab and style


class CopyToClipboard(w.VBox):
    def __init__(self, **kwargs):
        value = kwargs.get("value")
        self.text = w.Textarea(
            layout={"width": "800px", "height": "300px"}
        )  # value=value, # TODO: why is % not working?
        self.bn_copy = w.Button(icon="copy", layout={"width": BUTTON_WIDTH_MIN})
        self.vbx_bns = w.VBox(layout={"width": "48px"})
        self.hbx_main = w.HBox()
        self.output = w.Output(layout=w.Layout(display="none"))
        super().__init__(**kwargs)
    
        self._init_controls_c_to_c()
        self._set_children()

    def _init_controls_c_to_c(self):
        self.bn_copy.on_click(self._bn_copy)
        
    def _set_children(self):
        self.vbx_bns.children = [self.bn_copy]
        self.hbx_main.children = [self.vbx_bns, self.text, self.output]
        self.children = [self.hbx_main]

    def _bn_copy(self, event):
        copy_js = Javascript(
            f"navigator.clipboard.writeText({json.dumps(self.text.value)})"
        )
        self.output.clear_output()
        self.output.append_display_data(copy_js)

if __name__ == "__main__":
    cc = CopyToClipboard()
    display(cc)


def default_fn_upload(value):
    print(value)


class EditTsv(CopyToClipboard):
    _value = tr.List(value=None, trait=tr.Dict, allow_none=True)
    model = tr.Type(klass=BaseModel)
    errors = tr.List(value=[], trait=tr.Dict)
    fn_upload = tr.Callable(default_value=default_fn_upload)
    upload_status = tr.Enum(
        values=["enabled", "disabled", "None"], allow_none=False, default_value="None"
    )
    transposed = tr.Bool(default_value=False)
    allow_download = tr.Bool(default_value=True)
    exclude_metadata = tr.Bool(default_value=True)
    header_depth = tr.Int(default_value=1)
    disable_text_editing = tr.Bool(default_value=False)

    @tr.observe("upload_status")
    def upload_status_onchange(self, on_change):
        if self.upload_status == "disabled":
            self.bn_upload_text.disabled = True
            self.bn_upload_text.button_style = "danger"
        elif self.upload_status == "enabled":
            self.bn_upload_text.disabled = False
            self.bn_upload_text.button_style = "success"
        elif self.upload_status == "None":
            self.bn_upload_text.disabled = True
            self.bn_upload_text.button_style = ""
        else:
            raise ValueError(
                "button style must be in list: ['enabled', 'disabled', 'None']"
            )

    @tr.observe("value")
    def value_onchange(self, on_change):
        self.text.value = self.get_tsv_data()

    @tr.observe("errors")
    def errors_onchange(self, on_change):
        self.vbx_errors.children = [
            w.HTML(markdown(markdown_error(e))) for e in self.errors
        ]
        if self.errors:
            self.upload_status = "disabled"
        else:
            self.upload_status = "enabled"
            
    @tr.observe("transposed")
    def transpose(self, on_change):
        self.text.value = self.get_tsv_data()

    @tr.observe("allow_download")
    def show_hide_download_btn(self, on_change):
        if self.allow_download:
            self.mfdld.layout.display = ""
        else:
            self.mfdld.layout.display = "None"
        
    @tr.observe("disable_text_editing")
    def disable_text_editing_onchange(self, on_change):
        if self.disable_text_editing:
            self.text.disabled = True
        else:
            self.text.disabled = False

    def __init__(self, **kwargs):
        self.vbx_errors = w.VBox()
        self.bn_upload_text = w.Button(
            icon="save", disabled=True, layout={"width": BUTTON_WIDTH_MIN}
        )
        self.mfdld = MakeFileAndDownload(fn_create_file=self.create_file)
        super().__init__(**kwargs)
        self.value = kwargs.get("value")

        self._init_contols()

    def _set_children(self): 
        self.vbx_bns.children = [self.bn_copy, self.bn_upload_text, self.mfdld]
        self.hbx_main.children = [self.vbx_bns, self.text, self.output]
        self.children = [self.hbx_main]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        data = self.model.model_validate(value).model_dump(mode="json", by_alias=True) if value else []
        self._value = data
        self.text.value = self.get_tsv_data()

    def get_tsv_data(self):
        if self.transposed:
            return data_to_tsv_transposed(data_to_tsv(self.value))
        else:
            return data_to_tsv(self.value)

    def _init_contols(self):
        self.text.observe(self._text, "value")
        self.bn_upload_text.on_click(self._bn_upload_text)

    def _bn_upload_text(self, on_click):
        return self.fn_upload(self.value)

    def create_file(self):
        pydantic_obj = self.model(self.value)
        fpth = xdg.xdg_from_pydantic_object(
            pydantic_obj,
            is_transposed=self.transposed,
            exclude_metadata=self.exclude_metadata,
        )[0]
        return fpth

    def _text(self, change):
        value = []
        if self.text.value:
            value, self.errors = xdg.read_csv_string(
                self.text.value,
                is_transposed=self.transposed,
                model=self.model,
                delimiter="\t",
                header_depth=self.header_depth)
        if self.errors:
            self.vbx_errors.children = [
                w.HTML(markdown(markdown_error(e))) for e in self.errors
            ]
        else:
            self._value = value
            self.upload_status = "enabled"

    @property
    def tsv_data(self):  # TODO: ensure header row unchanged
        return xdg.read_csv_string(
            self.text.value,
            is_transposed=self.transposed,
            model=self.model,
            delimiter="\t",
            header_depth=self.header_depth)

    @property
    def pydantic_object(self):
        return self.model(self.value)

if __name__ == "__main__":
    from pydantic import RootModel
    from ipyautoui.demo_schemas import EditableGrid

    # Test: EditGrid instance with multi-indexing.
    AUTO_GRID_DEFAULT_VALUE = [
        {
            "id": 3,
            "string": "apples",
            "integer": 5,
            "floater": 2.0,
        },
        {
            "id": 4,
            "string": "bananas",
            "integer": 2,
            "floater": 3.5,
        },
        {
            "id": 5,
            "string": "oranges",
            "integer": 2,
            "floater": 4.0,
        },
        {
            "id": 6,
            "string": "pineapples",
            "integer": 1,
            "floater": 7.0
        },
    ]
    # AUTO_GRID_DEFAULT_VALUE = AUTO_GRID_DEFAULT_VALUE * 4

    def fn_upload(value):
        print(value[0].keys())

    edit_tsv = EditTsv(
        value=AUTO_GRID_DEFAULT_VALUE, model=EditableGrid, fn_upload=fn_upload, transposed=False, allow_download = True
    )
    display(edit_tsv)
# -


if __name__ == "__main__":
    # edit_tsv.transposed = True
    # edit_tsv.allow_download = False
    print(edit_tsv.pydantic_object.root)
    print(edit_tsv.model.model_json_schema().get("title", edit_tsv.model.__name__))

if __name__ == "__main__":
    # example of how to use DeepDiff
    from deepdiff import DeepDiff
    from deepdiff.helper import COLORED_VIEW, COLORED_COMPACT_VIEW

    t1 = [
        {
            "name": "John",
            "age": 30,
            "scores": [1, 2, 3],
            "address": {"city": "New York", "zip": "10001"},
        },
        {
            "name": "John",
            "age": 30,
            "scores": [1, 2, 3],
            "address": {"city": "New York", "zip": "10001"},
        },
    ]
    t2 = [
        {
            "name": "John",
            "age": 31,
            "scores": [1, 2, 4],
            "address": {"city": "Boston", "zip": "10001"},
            "new": "value",
        },
        {
            "name": "John",
            "age": 30,
            "scores": [1, 2, 3],
            "address": {"city": "New York", "zip": "10001"},
        },
    ]

    diff = DeepDiff(t1, t2, view=COLORED_COMPACT_VIEW)
    print(diff)

if __name__ == "__main__":
    import pandas as pd
    pd.DataFrame.from_dict({"a": [12, 3], "b": ["ad", "daf"]}).set_index("a")


if __name__ == "__main__":
    # NOTE: maybe useful later...
    display(
        w.HBox(
            [
                w.Button(icon="file-import"),
                w.Button(icon="file-export"),
            ]
        )
    )

if __name__ == "__main__":
    from deepdiff import DeepDiff
    d1 = {
        3: {
            "string": "important string 3",
            "integer": 3,
            "floater": 17.5
        },
        5: {
            "string": "str",
            "integer": 6,
            "floater": 7.0
        }
    }

    d2 = {
        3: {
            "string": "important string 3",
            "integer": 3,
            "floater": 18.0
        },
        5: {
            "string": "str",
            "integer": 6,
            "floater": 8.5
        }
    }
    
    ddiff = DeepDiff(d1, d2, ignore_order=True)

    display(ddiff)



class DisplayDeepDiff(w.VBox):
    value = tr.Dict(value=None, trait=tr.Dict, allow_none=True)
    new_value = tr.Dict(value=None, trait=tr.Dict, allow_none=True)
    diff = tr.Instance(value=None, klass=DeepDiff, allow_none=True)

    def __init__(self, **kwargs):
        self.out = w.Output(layout=w.Layout(width="400px")) # Explicit width value NEEDED to render properly on voila. Otherwise, it takes up all the width and nothing besides it is visible on screen.
        super().__init__(**kwargs)
        self.children = [w.HTML('Additions in <span style="color:green;">Green</span>, '
        'Deletions in <span style="color:red;">Red</span>'), self.out]

    @tr.observe("new_value")
    def _update_diff(self, on_change):
        if self.value is not None and self.new_value is not None:
            self.diff = DeepDiff(self.value, self.new_value, view=COLORED_COMPACT_VIEW, threshold_to_diff_deeper=0)

    @tr.observe("diff")
    def _display_diff(self, on_change):
        with self.out:
            clear_output()
            print(self.diff)


class Changes(BaseModel):
    deletions: list[ty.Union[str, int]]
    edits: dict[ty.Union[str, int], dict]
    additions: list[dict]
    edited_rows: dict[ty.Union[str, int], dict]


class EditTsvWithDiff(EditTsv):
    primary_key_name = tr.Unicode()
    prev_value = tr.List(value=None, trait=tr.Dict, allow_none=True)
    changes = Changes(
        deletions=[],
        edits={},
        additions=[],
        edited_rows={}
    )
    # add ui functionality to use deepdiff to view changes between new_value and _value and prompt the user to accept changes before proceeding

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        data = self.model.model_validate(value).model_dump(mode="json", by_alias=True) if value else []
        self._value = data
        """Code added to trigger manual validation if needed (text new value is same as previous text value - In that case,text obsever fn won't be triggered automatically)"""
        trigger_manual_validation = False
        if self.text.value and self.text.value == self.get_tsv_data():
            trigger_manual_validation = True

        self.text.value = self.get_tsv_data()
        ### Trigger manual validation
        if trigger_manual_validation:
            self._text(None)
        self.prev_value = deepcopy(self.value or [])
    
    def __init__(self, **kwargs):
        value = kwargs.get("value")
        if "value" in kwargs:
            kwargs.pop("value")
        self.ddiff = DisplayDeepDiff(layout=w.Layout(display="None"))
        self.bn_confirmation = w.Button(
            icon="check", disabled=True, layout={"width": BUTTON_WIDTH_MIN, "display": "None"}
        )
        self.bn_cross = w.Button(
            icon="ban", disabled=True, layout={"width": BUTTON_WIDTH_MIN, "display": "None"}
        )

        self.ddiff.observe(self._update_changes, "diff")

        self.bn_confirmation.on_click(self._bn_check_upload)
        self.bn_cross.on_click(self._bn_cross_clicked)
        super().__init__(**kwargs)
        self.value = value
        self.upload_status = "None"

    def _update_changes(self, change):
        """Called when self.ddiff.diff changes"""
        if change["new"] is not None:
            self.changes = self.deepdiff_to_crud(change["new"])

    def _set_children(self):
        if self.allow_download:
            self.vbx_bns.children = [self.bn_copy, self.bn_upload_text, self.mfdld, self.bn_confirmation, self.bn_cross]
        else:
            self.vbx_bns.children = [self.bn_copy, self.bn_upload_text, self.bn_confirmation, self.bn_cross]
        self.hbx_main.children = [self.vbx_bns, self.text, self.ddiff, self.output]
        self.children = [self.vbx_errors, self.hbx_main]
    
        
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

        # update deepdiff with original vs edited values
        pk = getattr(self, "primary_key_name", None)

        if not pk:
            # no primary key given → use index
            self.ddiff.value = {
                i: v for i, v in enumerate(self.prev_value)
            }
            self.ddiff.new_value = {
                i: v for i, v in enumerate(self.value)
            }
        else:
            # primary key given → use it, excluding the pk field in the nested dict
            self.ddiff.value = {
                v[pk]: {k: val for k, val in v.items() if k != pk}
                for v in self.prev_value
            }
            self.ddiff.new_value = {
                v[pk]: {k: val for k, val in v.items() if k != pk}
                for v in self.value
            }

    def _bn_check_upload(self, onclick):
        self.prev_value = deepcopy(self.value)
        self.show_upload_button_and_hide_deepdiff()
        
        self.fn_upload(self.value)
        self.reset_deep_diff()

    def _bn_cross_clicked(self, onclick):
        self.show_upload_button_and_hide_deepdiff(upload_disabled=False)

    def show_upload_button_and_hide_deepdiff(self, upload_disabled=True):
        # Hide check button and show upload button as well as text area
        self.bn_upload_text.layout.display = ""
        if upload_disabled:
            self.upload_status = "None"
        self.bn_confirmation.layout.display = "None"
        self.bn_confirmation.disabled = True
        self.bn_cross.layout.display = "None"
        self.bn_cross.disabled = True
        self.text.layout.display = ""
        self.ddiff.layout.display = "None"

    def reset_deep_diff(self):
        self.ddiff.diff = None
        self.changes = Changes(
            deletions=[],
            edits={},
            additions=[],
            edited_rows={}
        )

    def deepdiff_to_crud(self, diff: DeepDiff):
        changes = Changes(
            deletions=[],
            edits={},
            additions=[],
            edited_rows={},
        )
    
        # Additions
        if "dictionary_item_added" in diff:
            for delta in diff["dictionary_item_added"]:
                changes.additions.append(getattr(delta, "t2", None))
    
        # Deletions
        if "dictionary_item_removed" in diff:
            for delta in diff["dictionary_item_removed"]:
                path_list = delta.path(output_format="list")
                primary_key = str(path_list[0])  # first key (primary key)
                changes.deletions.append(primary_key)
    

        if "values_changed" in diff:
            for delta in diff["values_changed"]:
                path_list = delta.path(output_format="list")
                primary_key = str(path_list[0])  # first key (primary key)
                field = path_list[-1]            # last key (field name)
        
                if primary_key not in changes.edits:
                    changes.edits[primary_key] = {}
        
                changes.edits[primary_key][field] = delta.t2
            
        if "type_changes" in diff:
            for delta in diff["type_changes"]:
                path_list = delta.path(output_format="list")
                primary_key = str(path_list[0])  # first key (primary key)
                field = path_list[-1]            # last key (field name)
        
                if primary_key not in changes.edits:
                    changes.edits[primary_key] = {}
        
                changes.edits[primary_key][field] = delta.t2

        #Adding edited_rows (all the fields included for edited rows)
        if len(changes.edits): #TODO: use index instead of pk when pk is none
            pk = getattr(self, "primary_key_name", None)  # Confirm that primary key exists
            if pk:
                for primary_key in changes.edits.keys():
                    for row in self.value:
                        if str(row.get(pk)) == str(primary_key):
                            changes.edited_rows[primary_key] = row
                            break
            else:
                rows_by_index = {str(index): row for index, row in enumerate(self.value)}
                for index in changes.edits.keys():
                    if index in rows_by_index:
                        changes.edited_rows[index] = rows_by_index[index]

        return changes


if __name__ == "__main__":    
    edit_tsv_w_diff = EditTsvWithDiff(value=AUTO_GRID_DEFAULT_VALUE, model=EditableGrid, transposed = False, primary_key_name="id")
    display(edit_tsv_w_diff)

if __name__ == "__main__":
    display(edit_tsv_w_diff.value)
    display(edit_tsv_w_diff.text.value)


class EditTsvFileUpload(EditTsvWithDiff):
    """
    A widget for editing and uploading Excel files (e.g. .xlsx).
    - Inherits full diffing and validation logic from EditTsvWithDiff.
    - Disables manual text editing.
    - Adds an upload button for Excel files.
    """

    def __init__(self, **kwargs):
        # Ensure text editing is disabled by default
        kwargs.setdefault("disable_text_editing", True)

        # Create uploader before parent init so it's available during layout build
        self.file_uploader = TempFileUploadProcessor(
            fn_process=self._process_uploaded_file,
            allowed_file_type=".xlsx",
        )

        # Initialize base class
        super().__init__(**kwargs)
        self.last_upload_metadata = None

    def _set_children(self):
        super()._set_children()
        buttons = list(self.vbx_bns.children)
        if self.file_uploader not in buttons:
            insert_at = 1 if buttons else 0
            buttons.insert(insert_at, self.file_uploader)
            self.vbx_bns.children = tuple(buttons)

    def _text(self, change):
        pass

    def _process_uploaded_file(self, path: Path):
        """Handle Excel file upload and load into the widget."""
        if path is None:
            return

        path = Path(path)
        try:
            data, errors = xdg.read_excel(
                path,
                is_transposed=self.transposed,
                header_depth=self.header_depth,
                model=self.model,
            )
        except Exception:
            logger.exception("Failed to read uploaded Excel file")
            self.upload_status = "disabled"
            return

        self.errors = errors or []
        if self.errors:
            self.upload_status = "disabled"
            return

        self._value = data
        self.upload_status = "enabled"
        self.text.value = self.get_tsv_data()
