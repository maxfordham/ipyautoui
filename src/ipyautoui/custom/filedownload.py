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

"""file download widget"""
# %load_ext lab_black

import ipywidgets as w
import traitlets as tr
import pathlib
from base64 import b64encode
from IPython.display import clear_output, HTML
from ipyautoui.constants import FILEDNLD_BUTTON_KWARGS


# +
def coerce_to_alphanumeric(text: str, remove_spaces=False):
    """NOT IN USE!

    This is to ensure file directory is acceptable by the OS."""
    import re

    text = re.sub(r"[^a-zA-Z0-9]", "", text)
    if remove_spaces:
        text = text.replace(" ", "")
    return text


def load_file_to_b64(fpth: pathlib.Path) -> str:  # bytes ?
    with open(fpth, "rb") as file:
        content_b64 = b64encode(file.read()).decode()
    return content_b64


def trigger_download(content_b64: str, fname: str, output, kind: str = "text/json"):
    # see https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs for details
    # QUESTION: should kind be set to file type?
    data_url = f"data:{kind};charset=utf-8;base64,{content_b64}"
    js_code = f"""
        var a = document.createElement('a');
        a.setAttribute('download', '{fname}');
        a.setAttribute('href', '{data_url}');
        a.click()
    """
    with output:
        print("---")
        clear_output()
        display(HTML(f"<script>{js_code}</script>"))


class FileDownload(w.VBox):
    """
    downloads files into client Downloads folder
    
    Attributes:
    value = tr.Instance(klass=pathlib.Path)
    content_b64 = tr.Unicode() # updates on change to `value`
    """

    value = tr.Instance(klass=pathlib.Path)
    content_b64 = tr.Unicode()

    @tr.observe("value")
    def obs_fpth(self, on_change):
        if self.value.is_file():
            self.content_b64 = load_file_to_b64(self.value)
        self.bn_download.tooltip = f"download file: {self.value.name}"

    def __init__(self, **kwargs):
        self.output = w.Output()
        self.bn_download = w.Button(**FILEDNLD_BUTTON_KWARGS)
        super().__init__(**kwargs)
        self.bn_download.on_click(self._on_bn_download_clicked)
        self.children = [self.bn_download, self.output]

    def _on_bn_download_clicked(self, on_click):
        self.trigger_download()

    def trigger_download(self):
        trigger_download(self.content_b64, self.value.name, self.output)


if __name__ == "__main__":
    fpth = pathlib.Path("../../../tests/filetypes/eg_pdf.pdf")
    b64 = load_file_to_b64(fpth)
    fd = FileDownload(value=fpth)
    display(fd)
