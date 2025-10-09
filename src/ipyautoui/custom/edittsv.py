# +
import io
import csv
import json
import logging
import ipywidgets as w
import traitlets as tr
from IPython.display import Javascript
from pydantic import BaseModel, ValidationError
from markdown import markdown
from IPython.display import clear_output
from deepdiff import DeepDiff
from deepdiff.helper import COLORED_COMPACT_VIEW  # COLORED_VIEW,
from ipyautoui.custom.filedownload import MakeFileAndDownload
import pathlib
from copy import deepcopy
import typing as ty

from ipyautoui.constants import BUTTON_WIDTH_MIN
from ipyautoui.watch_validate import pydantic_validate


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


# +
# cc.vbx_bns
# cc.hbx_main

# +
# value, _value # list of dicts
# tsv_data # load text as tsv
# text_data
# pydantic_object

# +
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

    def __init__(self, **kwargs):
        self.vbx_errors = w.VBox()
        self.bn_upload_text = w.Button(
            icon="upload", disabled=True, layout={"width": BUTTON_WIDTH_MIN}
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
        try:
            value = pydantic_validate(self.model, value)
            self._value = value
            self.text.value = self.get_tsv_data()

        except ValidationError as exc:
            logging.info(exc)

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

    def generate_csv_file_from_tsv(self):
        tsv_str = self.text.value  

        # parse the current TSV string
        reader = csv.reader(io.StringIO(tsv_str), delimiter="\t")
        rows = list(reader)
    
        # write to CSV
        schema_name = self.model.model_json_schema().get("title", self.model.__name__)
        fpth = pathlib.Path(f"{schema_name}.csv")
        with fpth.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
            return fpth
    
    def create_file(self):
        # obj = self.pydantic_object
        # fpth = xdg.from_pydantic_object(obj)
        # return fpth
        fpth = self.generate_csv_file_from_tsv()
        return fpth

    def _text(self, change):
        value, self.errors = self.validate_text_value()
        if self.errors:
            self.vbx_errors.children = [
                w.HTML(markdown(markdown_error(e))) for e in self.errors
            ]
        else:
            self._value = value
            self.upload_status = "enabled"

    @property
    def tsv_data(self):  # TODO: ensure header row unchanged
        tsv_text = self.text.value
        if self.transposed:
            # Transpose again == untranspose back to original orientation
            tsv_text = data_to_tsv_transposed(tsv_text)
        return data_from_tsv(tsv_text)

    @property
    def pydantic_object(self):
        return self.model(self.value)

    def validate_text_value(self):  # > value, errors
        try:
            value = pydantic_validate(self.model, self.tsv_data)
            errors = []
        except ValidationError as exc:
            value = self.value
            errors = exc.errors()
        return value, errors


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


# +
# if __name__ == "__main__":
#     t1 = [
#         {
#             "name": "John",
#             "age": 30,
#             "scores": [1, 2, 3],
#             "address": {"city": "New York", "zip": "10001"},
#         },
#         {
#             "name": "John",
#             "age": 30,
#             "scores": [1, 2, 3],
#             "address": {"city": "New York", "zip": "10001"},
#         },
#     ]
#     t2 = [
#         {
#             "name": "John",
#             "age": 31,
#             "scores": [1, 2, 4],
#             "address": {"city": "Boston", "zip": "10001"},
#             "new": "value",
#         },
#         {
#             "name": "John",
#             "age": 30,
#             "scores": [1, 2, 3],
#             "address": {"city": "New York", "zip": "10001"},
#         },
#     ]

#     display_deepdiff.value = t1
#     display_deepdiff.new_value = t2
# -

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


class EditTsvWithDiff(EditTsv):
    primary_key_name = tr.Unicode(default="id")
    prev_value = tr.List(value=None, trait=tr.Dict, allow_none=True)
    changes = Changes(
        deletions=[],
        edits={},
        additions=[]
    )
    # add ui functionality to use deepdiff to view changes between new_value and _value and prompt the user to accept changes before proceeding

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        
        try:
            value = pydantic_validate(self.model, value)
            self._value = value
            self.text.value = self.get_tsv_data()
            self.prev_value = deepcopy(self.value)

        except ValidationError as exc:
            logging.info(exc)
    
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
        self.children = [self.hbx_main]
    
        
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
        pk = getattr(self, "primary_key_name", "id") or "id"

        self.ddiff.value = {
            v[pk]: {k: val for k, val in v.items() if k != pk}
            for v in self.prev_value
        } #original
        
        self.ddiff.new_value = {
            v[pk]: {k: val for k, val in v.items() if k != pk}
            for v in self.value
        } #edited

    def _bn_check_upload(self, onclick):
        self.prev_value = deepcopy(self.value)
        self.show_upload_button_and_hide_deepdiff()
        
        self.fn_upload(self.value)
        self.reset_deep_diff()

    def _bn_cross_clicked(self, onclick):
        self.value = self.prev_value
        self.show_upload_button_and_hide_deepdiff()
        self.reset_deep_diff()

    def show_upload_button_and_hide_deepdiff(self):
        # Hide check button and show upload button as well as text area
        self.bn_upload_text.layout.display = ""
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
            additions=[]
        )

    def deepdiff_to_crud(self, diff: DeepDiff):
        changes = Changes(
            deletions=[],
            edits={},
            additions=[]
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

        return changes


if __name__ == "__main__":    
    edit_tsv_w_diff = EditTsvWithDiff(value=AUTO_GRID_DEFAULT_VALUE, model=EditableGrid, transposed = False, primary_key_name="string")    
    display(edit_tsv_w_diff)

# edit_tsv_w_diff.changes
if __name__ == "__main__":
    # print(edit_tsv_w_diff.ddiff.diff["values_changed"])
    print(edit_tsv_w_diff.ddiff.diff.affected_paths)
    print(edit_tsv_w_diff.ddiff.diff.affected_root_keys)
    print(edit_tsv_w_diff.changes)

# +
# dlevel = diff['dictionary_item_removed'][0]
# type(dlevel)
# dlevel

# +
# from deepdiff.model import DiffLevel
# import typing as ty

# +
# diff = edit_tsv_w_diff.ddiff.diff
# pkey = "id"


    
# deletions = [x.t1[pkey] for x in diff['dictionary_item_removed']]
# deletions
# -

if __name__ == "__main__":
    print(edit_tsv_w_diff.changes)
    print('\n\n\n')
    print(edit_tsv_w_diff.ddiff.diff.to_dict())


