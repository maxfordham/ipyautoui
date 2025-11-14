"""file download widget"""


import ipywidgets as w
import traitlets as tr
import pathlib
from base64 import b64encode
from IPython.display import clear_output, HTML, display
from datetime import datetime
from ipyautoui.constants import FILEDNLD_BUTTON_KWARGS
from ipyautoui._utils import zip_files_to_string, calc_select_multiple_size
from ipyautoui.custom.selectandclick import SelectMultipleAndClick, FormLayouts


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
        clear_output()


class _Base(w.VBox):
    filename = tr.Unicode(allow_none=True, default_value=None)

    def __init__(self, **kwargs):
        self._init_form()
        super().__init__(**kwargs)
        self.children = [self.bn_download, self.output]

    def _init_form(self):
        self.output = w.Output()
        self.bn_download = w.Button(**FILEDNLD_BUTTON_KWARGS)
        self.bn_download.on_click(self._on_bn_download_clicked)

    def _on_bn_download_clicked(self, on_click):
        self.trigger_download()


class FileDownload(_Base):
    """
    downloads files into client Downloads folder

    Attributes:
    value = tr.Instance(klass=pathlib.Path)
    content_b64 = tr.Unicode() # updates on change to `value`
    """

    value = tr.Instance(klass=pathlib.Path, allow_none=True, default_value=None)
    content_b64 = tr.Unicode()

    @tr.observe("value")
    def obs_value_update_filename(self, on_change):
        self.filename = self.value.name

    @tr.observe("value")
    def obs_fpth(self, on_change):
        self.reload()

    def reload(self):
        if self.value is not None and self.value.is_file():
            self.content_b64 = load_file_to_b64(self.value)
            self.bn_download.disabled = False
        else:
            self.bn_download.disabled = False
        if self.value is None:
            name = "None"
        else: 
            name = self.value.name
        self.bn_download.tooltip = f"download file: {name}"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reload()

    def trigger_download(self):
        self.reload()
        trigger_download(self.content_b64, self.filename, self.output)


if __name__ == "__main__":
    fpth = pathlib.Path("../../../tests/filetypes/eg_pdf.pdf")
    fd = FileDownload(value =fpth)
    display(fd)


# +
class MakeFileAndDownload(FileDownload):
    fn_create_file = tr.Callable()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _on_bn_download_clicked(self, on_click):
        p = self.fn_create_file()
        self.value = p
        self.trigger_download()

def create_file():
    p = pathlib.Path("test.txt")
    p.write_text("asdfsadfas")
    return p
if __name__ == "__main__":   
    mfdld = MakeFileAndDownload(fn_create_file=create_file)
    display(mfdld)


# +
def get_filename():
    return datetime.now().strftime("%Y-%m-%dT%H%M") + "-file-dump.zip"


class _FilesDownload(tr.HasTraits):
    value = tr.List(
        trait=tr.Instance(klass=pathlib.Path, allow_none=True, default_value=None),
        default_value=[],
    )
    as_zip = tr.Bool(default_value=True)

    def valid_files(self):
        _ = True
        for v in self.value:
            if not v.is_file():
                with self.out:
                    print(f"{v}: is not a valid file")
                _ = False

        return _

    def trigger_download(self):
        if self.valid_files:
            if not self.as_zip:
                for v in self.value:
                    self.content_b64 = load_file_to_b64(v)
                    trigger_download(self.content_b64, v.name, self.output)
            else:
                if len(self.value) == 1:
                    v = self.value[0]
                    self.content_b64 = load_file_to_b64(v)
                    trigger_download(self.content_b64, v.name, self.output)
                else:
                    self.content_b64 = zip_files_to_string(self.value)
                    if self.filename is None:
                        self.filename = get_filename()
                    trigger_download(self.content_b64, self.filename, self.output)


class FilesDownload(_Base, _FilesDownload):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


if __name__ == "__main__":
    fpths = [
        pathlib.Path("../../../tests/filetypes/eg_pdf.pdf"),
        pathlib.Path("../../../tests/filetypes/eg_png.png"),
    ]
    fsd = FilesDownload(value=fpths)
    display(fsd)


# +
class SelectAndDownload(SelectMultipleAndClick, _FilesDownload):
    filename = tr.Unicode(allow_none=True, default_value=None)

    def __init__(self, **kwargs):
        super().__init__(
            **(dict(fn_layout_form=FormLayouts.align_vertical_left) | kwargs)
        )
        {setattr(self.bn, k, v) for k, v in FILEDNLD_BUTTON_KWARGS.items()}
        self.output = w.Output()
        self.children = list(self.children) + [self.output]
        self.fn_onclick = self.download_on_click
        self.hbx_message.layout.display = "None"
        self._update_controls()

    def _update_controls(self):
        self.select.observe(self._calc_select_multiple_size, "value")

    def _calc_select_multiple_size(self, on_change):
        self.select.layout.height = (
            f"{calc_select_multiple_size(len(self.select.options))}px"
        )

    def download_on_click(self, on_click):
        self.value = self.select.value
        self.trigger_download()


if __name__ == "__main__":
    paths = [
        pathlib.Path("../../../tests/filetypes/eg_pdf.pdf"),
        pathlib.Path("../../../tests/filetypes/eg_png.png"),
    ]
    fn_get_options = lambda: {p.name: p for p in paths}

    sd = SelectAndDownload(
        fn_get_options=fn_get_options,
        fn_layout_form=FormLayouts.align_vertical_left,
        title="Download Files",
    )
    display(sd)
