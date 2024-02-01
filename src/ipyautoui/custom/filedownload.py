# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.16.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

"""file upload wrapper"""
# %load_ext lab_black
# %run ../_dev_maplocal_params.py

from base64 import b64encode
import ipywidgets as w
from IPython.display import clear_output
import traitlets as tr
import pathlib


# %%
download_output = w.Output()
display(download_output)


def trigger_download(content_b64: str, filename: str, kind: str = "text/json"):
    # see https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs for details
    data_url = f"data:{kind};charset=utf-8;base64,{content_b64}"
    js_code = f"""
        var a = document.createElement('a');
        a.setAttribute('download', '{filename}');
        a.setAttribute('href', '{data_url}');
        a.click()
    """
    with download_output:
        clear_output()
        display(w.HTML(f"<script>{js_code}</script>"))


def load_pdf_to_b64(fpth: pathlib.Path) -> str:
    with open(fpth, "rb") as pdf_file:
        content_b64 = b64encode(pdf_file.read()).decode()
    return content_b64


# %%
def coerce_to_alphanumeric(text: str):
    """This is to ensure file directory is acceptable by the OS."""
    name = text.replace(" ", "")
    name = re.sub(r"[^a-zA-Z0-9]", "", name)
    return name


# +
get_js_code = (
    lambda fname, url: f"""
var a = document.createElement('a');
a.setAttribute('download', '{fname}');
a.setAttribute('href', '{url}');
a.click()
"""
)
download_output = w.Output()


class FileDownload(w.VBox):
    filename = tr.Unicode()
    content_b64 = tr.Unicode()
    type = tr.Unicode(default_value="text/json")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.download_button = w.Button(description="Download")
        self.download_button.on_click(self._on_download_button_clicked)
        self.children = [self.download_button]

    def _on_download_button_clicked(self, _):
        self.trigger_download()

    def trigger_download(self):
        data_url = f"data:{self.type};charset=utf-8;base64,{self.content_b64}"
        js_code = get_js_code(self.filename, data_url)
        # download_output = w.Output()
        with download_output:
            clear_output()
            display(w.HTML(f"<script>{js_code}</script>"))

    def load_file(self, fpth: pathlib.Path):
        with open(fpth, "rb") as file:
            self.content_b64 = b64encode(file.read()).decode()


# +
import tempfile

# Create a temporary file for testing
with tempfile.NamedTemporaryFile(delete=False) as temp:
    temp.write(b"Test content")
    temp_path = pathlib.Path(temp.name)

# Create a FileDownload instance
fd = FileDownload()
fd.filename = "test_file.txt"
fd.load_file(temp_path)

# Display the FileDownload instance
display(fd)

# Simulate a button click to trigger the download
fd.download_button.click()
# -

fd.content_b64

# +
download_output = w.Output()
display(download_output)
from IPython.display import HTML


def load_pdf_to_b64(fpth: pathlib.Path) -> str:
    with open(fpth, "rb") as pdf_file:
        content_b64 = b64encode(pdf_file.read()).decode()
    return content_b64


def trigger_download(content_b64: str, filename: str, kind: str = "text/json"):
    # see https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs for details
    data_url = f"data:{kind};charset=utf-8;base64,{content_b64}"
    js_code = f"""
        var a = document.createElement('a');
        a.setAttribute('download', '{filename}');
        a.setAttribute('href', '{data_url}');
        a.click()
    """
    with download_output:
        clear_output()
        display(HTML(f"<script>{js_code}</script>"))


# +
import pathlib

fpth = pathlib.Path("../../../tests/filetypes/eg_pdf.pdf")
print(f"fpth.is_file() = {fpth.is_file()}")
b_pdf = load_pdf_to_b64(fpth)
trigger_download(b_pdf, "eg_pdf.pdf")
# -






