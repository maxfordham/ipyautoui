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
        self.vbx_bns = w.VBox([self.bn_copy])
        self.output = w.Output(layout=w.Layout(display="none"))
        super().__init__(**kwargs)
        self.hbx_main = w.HBox([self.vbx_bns, self.text, self.output])
        self.children = [self.hbx_main]
        self.bn_copy.on_click(self._bn_copy)

    def _bn_copy(self, event):
        copy_js = Javascript(
            f"navigator.clipboard.writeText({json.dumps(self.text.value)})"
        )
        self.output.clear_output()
        self.output.append_display_data(copy_js)


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
        self.text.value = data_to_tsv(self.value)

    @tr.observe("errors")
    def errors_onchange(self, on_change):
        self.vbx_errors.children = [
            w.HTML(markdown(markdown_error(e))) for e in self.errors
        ]
        if self.errors:
            self.upload_status = "disabled"
        else:
            self.upload_status = "enabled"

    def __init__(self, **kwargs):
        self.vbx_errors = w.VBox()
        super().__init__(**kwargs)
        self.value = kwargs.get("value")

        self.children = [self.vbx_errors, self.hbx_main]
        self.bn_upload_text = w.Button(
            icon="upload", disabled=True, layout={"width": BUTTON_WIDTH_MIN}
        )
        self.vbx_bns.children = [self.bn_copy, self.bn_upload_text]

        self._init_contols()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        try:
            value = pydantic_validate(self.model, value)
            self._value = value
            self.text.value = data_to_tsv(self.value)

        except ValidationError as exc:
            logging.info(exc)

    def _init_contols(self):
        self.text.observe(self._text, "value")
        self.bn_upload_text.on_click(self._bn_upload_text)

    def _bn_upload_text(self, on_click):
        return self.fn_upload(self.value)

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
        return data_from_tsv(self.text.value)

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
            "string": "important string",
            "integer": 1,
            "floater": 3.14,
        },
    ]
    AUTO_GRID_DEFAULT_VALUE = AUTO_GRID_DEFAULT_VALUE * 4

    def fn_upload(value):
        print(value[0].keys())

    edit_tsv = EditTsv(
        value=AUTO_GRID_DEFAULT_VALUE, model=EditableGrid, fn_upload=fn_upload
    )
    display(edit_tsv)


# +
# TODO:


class EditTsvWithDiff(EditTsv):
    new_value = tr.List(value=None, trait=tr.Dict, allow_none=True)
    # add ui functionality to use deepdiff to view changes between new_value and _value and prompt the user to accept changes before proceeding
    #

    pass


# +
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


# +
# display DeepDiff with ipywidgets. TODO: integrate into EditTsvWithDiff


class DisplayDeepDiff(w.VBox):
    value = tr.List(value=None, trait=tr.Dict, allow_none=True)
    new_value = tr.List(value=None, trait=tr.Dict, allow_none=True)
    diff = tr.Instance(value=None, klass=DeepDiff, allow_none=True)

    def __init__(self, **kwargs):
        self.out = w.Output()
        super().__init__(**kwargs)
        self.children = [self.out]

    @tr.observe("new_value")
    def _update_diff(self, on_change):
        if self.value is not None and self.new_value is not None:
            self.diff = DeepDiff(self.value, self.new_value, view=COLORED_COMPACT_VIEW)

    @tr.observe("diff")
    def _display_diff(self, on_change):
        with self.out:
            clear_output()
            print(self.diff)


if __name__ == "__main__":
    display_deepdiff = DisplayDeepDiff()
    display(display_deepdiff)
# -

if __name__ == "__main__":
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

    display_deepdiff.value = t1
    display_deepdiff.new_value = t2

if __name__ == "__main__":
    # example extract
    from deepdiff import extract

    obj = {1: [{"2": "b"}, 3], 2: [4, 5]}
    path = "root[1][0]['2']"
    display(extract(obj, path))

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
