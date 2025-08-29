import io
import os
import json
import yaml
import codecs
import zipfile
import logging
import pathlib
import getpass
import inspect
import immutables
import importlib
import importlib.util
import pandas as pd
import ipywidgets as w
import typing as ty
import traitlets as tr
from typing import Type
from base64 import b64encode
from markdown import markdown
from math import log10, floor
from pydantic import BaseModel, field_validator, Field, ValidationInfo
from IPython.display import display, Markdown

logger = logging.getLogger(__name__)
frozenmap = immutables.Map

try:
    import maplocal

    if maplocal.maplocal_openlocal_exists():
        from maplocal import openlocal as open_path
        from maplocal import maplocal as make_new_path
    else:

        def make_new_path(path, *args, **kwargs):
            return path

        def open_path(path):
            import subprocess
            import sys

            if sys.platform == "linux":
                subprocess.call(["xdg-open", path])
            else:
                subprocess.call(["explorer.exe", path])

except:

    def make_new_path(path, *args, **kwargs):
        return path

    def open_path(path):
        import subprocess
        import sys

        if sys.platform == "linux":
            subprocess.call(["xdg-open", path])
        else:
            subprocess.call(["explorer.exe", path])


def getuser():
    try:
        return os.environ["JUPYTERHUB_USER"]
    except:
        return getpass.getuser()


# ------------------------------
def str_presenter(dumper, data):
    """configures yaml for dumping multiline strings
    Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
    """
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, str_presenter)
yaml.representer.SafeRepresenter.add_representer(
    str, str_presenter
)  # to use with safe_dum
# ------------------------------
# ^ configures yaml for pretty dumping of multiline strings


def display_pydantic_json(
    pydantic_obj: ty.Type[BaseModel], as_yaml=False, sort_keys=False
):
    parsed = json.loads(pydantic_obj.json())
    if as_yaml:
        s = yaml.dump(parsed, indent=2, sort_keys=sort_keys)  # , sort_keys=True)
        return Markdown("\n```yaml\n" + s + "\n```")
    else:
        s = json.dumps(parsed, indent=2, sort_keys=sort_keys)  # , sort_keys=True)
        return Markdown("\n```Python\n" + s + "\n```")


def _markdown(value="_Markdown_", **kwargs):
    """
    a simple template for markdown text input that templates required input
    fields. additional user defined fields can be added as kwargs
    """
    _kwargs = {}
    _kwargs["value"] = markdown(value)  # required field
    _kwargs.update(kwargs)  # user overides
    return w.HTML(**_kwargs)


def write_json(data, fpth="data.json", sort_keys=True, indent=4):
    """
    write output to json file
    Args:
        data
        ** sort_keys = True
        ** indent=4
        ** fpth='data.json'

    Code:
        out=json.dumps(data, sort_keys=sort_keys, indent=indent)
        f = open(fpth,"w")
        f.write(out)
        f.close()
    """
    out = json.dumps(data, sort_keys=sort_keys, indent=indent)
    f = open(fpth, "w")
    f.write(out)
    f.close()
    return fpth


def read_json(fpth, encoding="utf8"):
    """
    read info in a .json file
    """
    with open(fpth, "r", encoding=encoding) as f:
        json_file = json.loads(f.read())
    return json_file


def del_cols(df, cols):
    """delete a pandas column if it is in
    the column index otherwise ignore it."""
    if type(cols) == str:
        try:
            del df[cols]
        except:
            print(cols + " is not in column index")
    else:
        for col in cols:
            try:
                del df[col]
            except:
                print(col + " is not in column index")
    return df


def del_matching(df, string):
    """
    deletes columns if col name matches string
    """
    matching = [s for s in list(df) if string in s]
    df = del_cols(df, matching)
    return df


#  ------------------------------------------------------------------------------------------------


def display_python_string(string, show=True, return_str=False, myst_format=False):
    if myst_format:
        s = "\n```{code-cell} ipython3\n" + string + "\n```"
    else:
        s = "\n```python\n" + string + "\n```"
    if show:
        display(Markdown(s))
    if return_str:
        return s


def display_python_file(fpth, show=True, return_str=False):
    """
    pass the fpth of a python file and get a
    rendered view of the code.
    """
    with open(fpth, "r") as myfile:
        data = myfile.read()
    s = display_python_string(data, show=False, return_str=True)
    if show:
        display(Markdown(s))
    if return_str:
        return s


def display_python_module(mod, show=True, return_str=False):
    """
    pass the fpth of a python file and get a
    rendered view of the code.
    """
    if str(type(mod)) != "<class 'module'>":
        raise ValueError("input must be a python module")
    fpth = mod.__file__
    s = display_python_file(fpth, show=False, return_str=True)
    if show:
        display(Markdown(s))
    if return_str:
        return s


def read_txt(fpth, encoding="utf-8", delim=None, read_lines=True):
    """
    read a .txt file

    Args:
        fpth(string): filepath
        encoding(string): https://docs.python.org/3/library/codecs.html, examples:
            utf-16, utf-8, ascii
        delim(char): character to string split, examples:
            '\t', ','
        read_lines(bool): readlines or whole string (delim may not work if read_lines==False

    """
    with codecs.open(fpth, encoding=encoding) as f:
        if read_lines == True:
            content = f.readlines()
        else:
            content = f.read()
    f.close()
    if delim != None:
        li = []
        for n in range(0, len(content)):
            li.append(content[n].split(delim))
        return li
    else:
        return content


def read_yaml(fpth, encoding="utf8"):
    """
    read yaml file.

    Ref:
        https://stackoverflow.com/questions/1773805/how-can-i-parse-a-yaml-file-in-python
    """
    with open(fpth, encoding=encoding) as stream:
        try:
            data = yaml.safe_load(stream)
            return data
        except yaml.YAMLError as exc:
            print(exc)


def file(self: Type[BaseModel], path: pathlib.Path, **json_kwargs):
    """
    this is a method that is added to the pydantic BaseModel within AutoUi using
    "setattr".

    Example:
        ```setattr(self.config_autoui.pydantic_model, 'file', file)```

    Args:
        self (pydantic.BaseModel): instance
        path (pathlib.Path): to write file to
    """
    if "indent" not in json_kwargs.keys():
        json_kwargs.update({"indent": 4})
    path.write_text(self.model_dump_json(**json_kwargs), encoding="utf-8")


def round_sig_figs(x: float, sig_figs: int):
    if x > 0:
        sig = sig_figs
        return round(x, sig - int(floor(log10(abs(x)))) - 1)
    else:
        return x


class PyObj(BaseModel):
    """a definition of a python object"""

    path: pathlib.Path
    obj_name: str
    module_name: str = Field(
        None, description="ignore, this is overwritten by a validator"
    )

    @field_validator("module_name")
    @classmethod
    def _module_name(cls, v, info: ValidationInfo):
        return info.data["path"].stem


def load_PyObj(obj: PyObj):
    submodule_search_locations = None
    p = obj.path
    if obj.path.is_dir():
        p = p / "__main__.py"
        submodule_search_locations = []
    spec = importlib.util.spec_from_file_location(
        obj.module_name, p, submodule_search_locations=submodule_search_locations
    )
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    return getattr(foo, obj.obj_name)


# TODO: use obj_to_importstr and obj_from_importstr rather than load_PyObj
def obj_to_importstr(obj: ty.Callable):  # NOT IN USE
    """
    given a callable callable object this will return the
    import string to. From the string the object can be
    initiated again using importlib. This is useful for
    defining a function or class in a json serializable manner

    Args:
        obj: ty.Callable
    Returns:
        str: import string

    Example:
        >>> obj_from_importstr(pathlib.Path)
        'pathlib.Path'
    """
    try:
        mod = obj.__module__
    except:
        raise ValueError(f"{str(obj)} doesnt have a __module__ attribute.")
    try:
        nm = obj.__name__
    except:
        raise ValueError(
            f"{str(obj)} doesnt have a __name__ attribute. (might be a functool.partial?)"
        )

    return mod + "." + nm


def obj_from_importstr(importstr: str) -> ty.Type:
    """
    given the import string of an object this function and returns the Obj.

    makes it easy to define class used as a string in a json
    object and then use this class to re-initite it.

    Args:
        import_string: == obj.__module__ + '.' + obj.__name__
    Returns:
        obj

    Example:
        >>> obj_from_importstr('pathlib.Path')
        pathlib.Path
    """
    if "." not in importstr:
        importstr = "__main__." + importstr
    mod, nm = importstr.rsplit(".", 1)

    return getattr(importlib.import_module(mod), nm)


def argspecs_in_kwargs(call: ty.Callable, kwargs: dict):
    """get argspecs for kwargs"""
    return {k: v for k, v in kwargs.items() if k in inspect.getfullargspec(call).args}


def traits_in_kwargs(call: ty.Callable, kwargs: dict):
    """get traits for kwargs"""
    if not hasattr(call, "traits"):
        logger.info(f"{call.__name__} does not have traits attribute")
        return {}
    else:
        li = list(call.traits(call).keys())
        return {k: v for k, v in kwargs.items() if k in li or f"_{k}" in li}

def trait_order(cls: ty.Callable):
    return [k for k, v in cls.__dict__.items() if isinstance(v, tr.TraitType)]


def remove_non_present_kwargs(callable_: ty.Callable, di: dict):
    """do this if required (get allowed args from callable)"""
    argspec = argspecs_in_kwargs(callable_, di)
    traits = traits_in_kwargs(callable_, di)
    return {**argspec, **traits}


def get_ext(fpth):
    """get file extension including compound json files"""
    return "".join(pathlib.Path(fpth).suffixes).lower()


def st_mtime_string(path):
    """st_mtime_string for a given path"""
    try:
        import time

        t = path.stat().st_mtime
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
    except:
        return "####-##-## ##:##:##"


def check_installed(package_name):
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return False
    else:
        return True


def html_link(url: str, description: str, color: str = "blue"):
    """returns an html link string to open in new tab

    Args:
        url (url):
        description (str): the text to display for the link
        color (str, optional): color of description text. Defaults to "blue".

    Returns:
        str: html text
    """
    return f'<font color="{color}"><a href="{url}" target="blank" >{description}</a></font>'


def get_user():
    """get user. gets JUPYTERHUB_USER if present (i.e. if notebook served via a JupyterHub)"""
    nm = "JUPYTERHUB_USER"
    if nm in list(os.environ.keys()):
        return os.environ[nm]
    else:
        from getpass import getuser

        return getuser()


def type_as_json(value):
    if isinstance(value, str):
        return "string"
    elif isinstance(value, int):
        return "integer"
    elif isinstance(value, float):
        return "number"
    elif isinstance(value, bool):
        return "number"
    elif isinstance(value, list):
        return "array"
    elif isinstance(value, dict):
        return "object" + "-" + "".join(value.keys())
    elif isinstance(value, None):
        return "null"
    else:
        raise ValueError(
            "value must be: string, integer, number, array, object or None"
        )


def json_as_type(s) -> ty.Type:
    if s == "string":
        return str
    elif s == "integer":
        return int
    elif s == "number":
        return float
    elif s == "boolean":
        return bool
    elif s == "array":
        return list
    elif s == "object":
        return dict
    elif s == "null":
        return None
    else:
        raise ValueError(
            "value must be: string, integer, number, array, object or None"
        )


def show_hide_widget(widget, show: bool):
    try:
        if show:
            widget.layout.display = ""
        else:
            widget.layout.display = "None"
    except:
        ValueError(str(widget) + "failed to change layout.display")


def zip_files_to_string(fpths: ty.List[pathlib.Path]) -> str:
    # Create a BytesIO object
    zip_buffer = io.BytesIO()

    # Create a ZipFile object with the BytesIO object as the file
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # Loop over each file
        for file in fpths:
            # Add file to the zip
            zip_file.write(file, arcname=file.name)

    # Get the byte content of the zip file
    zip_bytes = zip_buffer.getvalue()

    # Convert the bytes to a base64 string
    zip_string = b64encode(zip_bytes).decode()

    return zip_string


def calc_select_multiple_size(no_items, min=100, max=600, step=5.8):
    h = no_items * min / step
    if h < min:
        return min
    elif h > max:
        return max
    else:
        return h


def is_null(v) -> bool:
    """Check if a value is null.

    This function exists because pd.isnull returns an ndarray of bools for
    non-scalar values, which is not what we want. Therefore, we check if the
    value is a list, dict, pd.Series, or pd.DataFrame and return False if it is,
    otherwise we return the result of pd.isnull.
    """
    if isinstance(v, (list, dict, pd.Series, pd.DataFrame)):
        return False
    else:
        return pd.isnull(v)
