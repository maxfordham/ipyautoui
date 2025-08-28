"""
displayfile is used to display certain types of files.
The module lets us preview a data retrieved from: file, request or callable (< TODO)
"""


# +
import os
import pathlib
import requests
import pandas as pd
from IPython.display import display, Markdown, IFrame, clear_output, HTML, SVG
import json
import ipydatagrid as ipg
import ipywidgets as w
import traitlets as tr
import typing as ty
from io import StringIO, BytesIO
from pydantic import HttpUrl


#  local imports
from ipyautoui.mydocstring_display import display_module_docstring
from ipyautoui._utils import (
    del_matching,
    display_python_file,
    frozenmap,
    check_installed,
    get_ext,
)
from ipyautoui.constants import BUTTON_WIDTH_MIN
from ipyautoui.custom.showhide import ShowHide
from ipyautoui.env import Env

ENV = Env()

# if check_installed('xlsxtemplater'):
#     from xlsxtemplater import from_excel

if check_installed("plotly"):
    import plotly.io as pio


# -


# + tags=[]


def getbytes(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable]) -> ty.ByteString:
    """common function for read bytes from: a request, file or callable
    NOTE: if a callable the data must be returned as bytes
    """

    def is_url(p):
        try:
            HttpUrl(p)
            return True
        except:
            return False

    if isinstance(path, pathlib.Path):
        return path.read_bytes()
    elif is_url(path):
        return requests.get(path).content
    elif isinstance(path, ty.Callable):
        return path()
    else:
        raise ValueError(
            "path must be either a pathlib.Path, pydantic.HttpUrl or typing.Callable object\n"
            "to create an HttpUrl object:\n"
            "`from pydantic import parse_obj_as, HttpUrl`\n"
            "`url = parse_obj_as(HttpUrl, 'https://jupyter.org/')`"
        )


class PreviewPython:
    """
    pass the class either a filepath or an imported
    module and get a display output of the modules
    docstring with a toggle option to view the code
    """

    def __init__(self, module, preview_script=True, docstring_priority=True):
        self.input = module
        self.preview_script = preview_script
        self.docstring_priority = docstring_priority
        self.out = w.Output()
        self.fpth = self._handle_input()
        self._init_form()
        self._init_controls()
        if self.docstring_priority:
            self._show_docstring()
        else:
            self.show_me_the_code.value = True

    def _handle_input(self):
        if str(type(self.input)) == "<class 'module'>":
            fpth = self.input.__file__
        else:
            fpth = self.input
        if os.path.splitext(fpth)[1] != ".py":
            print("{0}: not a python file".format(fpth))
        return fpth

    def _init_form(self):
        self.title = w.HTML("")
        self.show_me_the_code = w.ToggleButton(layout=w.Layout(width=BUTTON_WIDTH_MIN))
        self.headerbox = w.VBox([w.HBox([self.show_me_the_code, self.title])])

        if self.preview_script:
            display(self.headerbox)

    def _init_controls(self):
        self.show_me_the_code.observe(self._show_me_the_code, "value")

    def _update_title(self):
        self.title.value = "👆 {}".format(self.description)

    def _show_docstring(self):
        self.show_me_the_code.icon = "scroll"
        self.show_me_the_code.tooltip = "show the raw python code"
        self.show_me_the_code.button_style = "warning"
        self.description = "show python code"
        self._update_title()
        with self.out:
            clear_output()
            display_module_docstring(self.fpth)

    def _show_me_the_code(self, sender):
        self.show_me_the_code.icon = "book"
        self.show_me_the_code.tooltip = "show the python script documentation"
        self.show_me_the_code.button_style = "info"
        self.description = "show documentation"
        self._update_title()
        with self.out:
            clear_output()
            if self.show_me_the_code.value:
                display_python_file(self.fpth)
            else:
                self._show_docstring()

    def display(self):
        display(self.out)

    def _ipython_display_(self):
        self.display()


# +
def default_grid(df, **kwargs):
    """
    thin wrapper for ipy.DataGrid

    Code:
        _kwargs = {
            'layout':{'width':'100%', 'height':'400px'}
        }
        _kwargs.update(kwargs)  # user overides
        g = ipg.DataGrid(df, **_kwargs)
        return g

    """

    _kwargs = {"layout": {"width": "100%", "height": "400px"}, "auto_fit_columns": True}
    _kwargs.update(kwargs)  # user overides
    g = ipg.DataGrid(df, **_kwargs)
    return g


def preview_csv(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable]):
    byts = getbytes(path)
    df = pd.read_csv(StringIO(byts.decode()))
    df = del_matching(pd.read_csv(path), "Unnamed")
    return default_grid(df)


class PreviewExcel(w.VBox):
    path = tr.Instance(klass=pathlib.PurePath)
    xl = tr.Instance(klass="pandas.ExcelFile")

    def __init__(self, path: ty.Union[pathlib.Path, HttpUrl, ty.Callable]):
        super().__init__()

        self.path = path

    @tr.observe("path")
    def _observe_path(self, change):
        byts = getbytes(self.path)
        self.xl = pd.ExcelFile(BytesIO(byts)) # NOTE: requires openpyxl

    @tr.observe("xl")
    def _observe_xl(self, change):
        self.children = [
            ShowHide(title=name, fn_display=lambda: default_grid(self.xl.parse(name)))
            for name in self.xl.sheet_names
        ]


def mdboldstr(string, di):
    """return bold __key__: value from dict"""
    return "__{}__: {}".format(string, di[string])


def mdnorms(di):
    return (
        mdboldstr("ProjectNo", di)
        + " ........ "
        + mdboldstr("Date", di)
        + " ........ "
        + mdboldstr("Author", di)
    )


def mdwildcars(di):
    exclude = [
        "sheet_name",
        "xlsx_params",
        "xlsx_exporter",
        "ProjectNo",
        "Date",
        "Author",
        "df",
        "grid",
    ]
    others = {k: v for k, v in di.items() if k not in exclude}
    mdstr = ""
    for k, v in others.items():
        mdstr = mdstr + "__{}__: {}<br>".format(k, v)
    return mdstr


def mdheader(di):
    return "### {} \n {} <br> {}".format(di["sheet_name"], mdnorms(di), mdwildcars(di))


def xlsxtemplated_display(li):
    """
    displays xlsxtemplated (written using xlsxtemplater) using ipydatagrid
    """
    for l in li:
        l["grid"] = default_grid(l["df"])
        display(Markdown(mdheader(l)))
        display(l["grid"])


def preview_json_string(json_str):
    return Markdown(
        f"""
```json
{json.dumps(json_str, indent=4)}
```
"""
    )


def preview_json(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable]):
    js = json.loads(getbytes(path).decode())
    return preview_json_string(js)


def preview_yaml_string(yaml_str):
    return Markdown(
        f"""
```yaml
{yaml_str}
```
"""
    )


def preview_yaml(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable]):
    byts = getbytes(path)
    return preview_yaml_string(byts.decode())


def preview_plotly_json(plotly_str):
    package_name = "plotly"
    if check_installed(package_name):
        return pio.from_json(plotly_str)
    else:
        return w.HTML(package_name + " is not installed")


def preview_plotly(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable]):
    byts = getbytes(path)
    return preview_plotly_json(byts.decode())


def Vega(spec):
    """
    render Vega in jupyterlab
    https://github.com/jupyterlab/jupyterlab/blob/master/examples/vega/vega-extension.ipynb
    """
    bundle = {}
    bundle["application/vnd.vega.v5+json"] = spec
    display(bundle, raw=True)
    # return bundle


def VegaLite(spec):
    """
    render VegaLite in jupyterlab
    https://github.com/jupyterlab/jupyterlab/blob/master/examples/vega/vega-extension.ipynb
    """
    bundle = {}
    bundle["application/vnd.vegalite.v4+json"] = spec
    display(bundle, raw=True)
    # return bundle


def update_vega_data_url(data: dict, path: pathlib.Path) -> dict:
    """for relative urls, the path is normally given relative to the json file,
    but when viewed in Voila it needs to be relative to the notebook file. This
    updates the relative path

    Args:
        data (dict): vega data
        path (Path): path of vg.json

    Returns:
        dict : dict with updated data url
    """
    if "url" in data.keys():
        url = data["url"]
        if "http" in url:
            pass
        else:
            p = pathlib.Path(path.parent).absolute() / url
            url = os.path.relpath(p, start=ENV.IPYAUTOUI_ROOTDIR)
            data["url"] = url
    return data


def get_vega_data(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable]):
    byts = getbytes(path)
    data = json.loads(byts.decode())
    if isinstance(path, pathlib.Path):
        if isinstance(data["data"], list):
            data["data"] = [update_vega_data_url(d, path) for d in data["data"]]
        elif isinstance(data["data"], dict):
            data["data"] = update_vega_data_url(data["data"], path)
        else:
            raise ValueError("vega data must be list or dict")
    return data


def preview_vega_json(vega_json):
    return Vega(vega_json)


def preview_vega(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable]):
    data = get_vega_data(path)
    return preview_vega_json(data)


def preview_vegalite_json(vegalite_json):
    return VegaLite(vegalite_json)


def preview_vegalite(path):
    data = get_vega_data(path)
    return VegaLite(data)


def preview_image(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable], *args, **kwargs):
    byts = getbytes(path)
    return w.Image(value=byts, *args, **kwargs)


def preview_svg(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable], *args, **kwargs):
    byts = getbytes(path)
    return SVG(byts, *args, **kwargs)


def preview_video(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable], *args, **kwargs):
    byts = getbytes(path)
    return w.Video(value=byts, *args, **kwargs)


def preview_audio(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable], *args, **kwargs):
    byts = getbytes(path)
    return w.Audio(value=byts, *args, **kwargs)


##############TODO: from here:###############################


def preview_text_string(text_str):
    return Markdown(
        f"""
```
{text_str}
```
"""
    )


def preview_text(path: ty.Union[pathlib.Path, HttpUrl, ty.Callable]):
    byts = getbytes(path)
    return preview_text_string(byts.decode())


def preview_dir(path: pathlib.Path):
    """preview folder"""
    # TODO: make recursive using AutoDisplay?
    li = path.glob("*")
    make_str = lambda p: f"📁 {p.stem}" if p.is_dir() else f"📄 {p.stem}"
    li = [make_str(l) for l in li]
    return HTML("<br>".join(li))


def preview_text_or_dir(path):
    """display path with ext == "" """
    if path.is_file():
        return preview_text(path)
    else:
        return preview_dir(path)


# TODO: how to preview markdown not as a file, but as a string?
def preview_markdown(path: pathlib.Path):
    import subprocess

    if not path.is_file():
        raise ValueError(
            f"path must be a valid pathlib.Path, not {path}. TODO: create render method."
        )
    p = os.path.relpath(path, start=ENV.IPYAUTOUI_ROOTDIR)
    c = subprocess.run(
        f"pandoc {str(p)} -f markdown+rebase_relative_paths",
        cwd=ENV.IPYAUTOUI_ROOTDIR,
        shell=True,
        capture_output=True,
    )
    s = c.stdout.decode("utf-8")
    return HTML(
        f"""
{s}
"""
    )


def preview_pdf(path: pathlib.Path):  # TODO: facillitate passing kwargs...
    if not isinstance(path, pathlib.PurePath):
        path = pathlib.Path(path)

    path = os.path.relpath(path, start=ENV.IPYAUTOUI_ROOTDIR)
    return IFrame(path, width=1000, height=1000)


DEFAULT_FILE_RENDERERS = frozenmap(
    **{
        ".csv": preview_csv,
        ".xlsx": PreviewExcel,
        ".json": preview_json,
        ".plotly": preview_plotly,
        ".plotly.json": preview_plotly,
        ".vg.json": preview_vega,
        ".vl.json": preview_vegalite,
        ".yaml": preview_yaml,
        ".yml": preview_yaml,
        ".png": preview_image,
        ".jpg": preview_image,
        ".jpeg": preview_image,
        ".gif": preview_image,
        ".svg": preview_svg,
        ".mp4": preview_video,
        ".mp3": preview_audio,
        #'.obj': obj_prev, # TODO: add ipyvolume viewer?
        ".txt": preview_text,
        ".bat": preview_text,
        ".rst": preview_text,
        "": preview_text_or_dir,  # make this recursive ?
        ".toml": preview_text,
        ".md": preview_markdown,
        ".py": PreviewPython,
        ".pdf": preview_pdf,
    }
)


def handle_compound_ext(ext, renderers=DEFAULT_FILE_RENDERERS):
    """_summary_

    Args:
        ext (_type_): _description_
        renderers (_type_, optional): _description_. Defaults to DEFAULT_FILE_RENDERERS.

    Returns:
        _type_: _description_
    """
    li_ext = ext.split(".")
    if ext in list(renderers.keys()):
        return ext
    elif len(li_ext) > 2:
        # it is a compound filetype when the compound didn't match
        # so return main ext
        return "." + li_ext[-1]
    else:
        return ext


def render_file(path: pathlib.Path, renderers=DEFAULT_FILE_RENDERERS):
    """simple renderer.

    Note:
        this function is not used by AutoDisplay, but is provided here for simple
        API functionality

    Args:
        path (pathlib.Path):
        renderers (_type_, optional): _description_. Defaults to DEFAULT_FILE_RENDERERS.

    Returns:
        something to display
    """
    # note: this isn't used by AutoDisplay
    path = pathlib.Path(path)
    ext = get_ext(path)
    ext = handle_compound_ext(ext)
    return renderers[ext](path)
