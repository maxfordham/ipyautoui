import pathlib
import json
import yaml
import importlib
from typing import Type
from markdown import markdown
from math import log10, floor
import ipywidgets as w
from IPython.display import display, Markdown
import codecs
from pydantic import BaseModel, validator, Field
import typing as ty
import importlib.util
import inspect
import immutables
import getpass

frozenmap = immutables.Map


def make_new_path(path, *args, **kwargs):
    return path


try:
    # TODO: remove these.
    from mf_file_utilities import go as open_file
    from mf_file_utilities.applauncher_wrapper import make_new_path
except:

    def open_file(path):
        import subprocess

        subprocess.call(["open", path])


def getuser():
    try:
        return os.environ["JUPYTERHUB_USER"]
    except:
        return getpass.getuser()


# ------------------------------
def str_presenter(dumper, data):
    """configures yaml for dumping multiline strings
    Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data"""
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
        https://stackoverflow.com/questions/1773805/how-can-i-parse-a-yaml-file-in-python"""
    with open(fpth, encoding=encoding) as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data


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
    path.write_text(self.json(**json_kwargs), encoding="utf-8")


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

    @validator("module_name", always=True)
    def _module_name(cls, v, values):
        return values["path"].stem


def load_PyObj(obj: PyObj):
    spec = importlib.util.spec_from_file_location(obj.module_name, obj.path)
    foo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(foo)
    return getattr(foo, obj.obj_name)


def create_pydantic_json_file(pyobj: PyObj, path: pathlib.Path, **kwargs):
    """
    loads a pyobj (which must be a pydantic model) and then saves the default Json to file.
    this requires defaults for all pydantic attributes.

    Todo:
        could extend the functionality to cover models that don't have defaults
        using [pydantic-factories](https://github.com/Goldziher/pydantic-factories)

    Args:
        pyobj (PyObj): definition of where to get a pydantic model
        path (pathlib.Path): where to save the pydantic json
        **kwargs : passed to the pydantic model upon initiation

    Returns:
        path
    """
    obj = load_PyObj(pyobj)
    assert (
        str(type(obj)) == "<class 'pydantic.main.ModelMetaclass'>"
    ), "the python object must be a pydantic model"
    if not hasattr(obj, "file"):
        setattr(obj, "file", file)
    assert hasattr(
        obj, "file"
    ), "the pydantic BaseModel must be extended to have method 'file' for writing model to json"
    myobj = obj(**kwargs)
    myobj.file(path)
    return path


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


class SerializableCallable(BaseModel):  # NOT IN USE
    callable_str: ty.Union[ty.Callable, str] = Field(
        ...,
        description="import string that can use importlib\
                                                              to create a python obj. Note. if a Callable object\
                                                              is given it will be converted into a string",
    )
    callable_obj: ty.Union[ty.Callable, ty.Type] = Field(None, exclude=True)

    @validator("callable_str", always=True)
    def _callable_str(cls, v, values):
        if type(v) != str:
            return obj_to_importstr(v)
        invalid = [i for i in "!@#£[]()<>|¬$%^&*,?''- "]
        for i in invalid:
            if i in v:
                raise ValueError(
                    f"callable_str = {v}. import_str must not contain spaces {i}"
                )
        return v

    @validator("callable_obj", always=True)
    def _callable_obj(cls, v, values):
        return obj_from_importstr(values["callable_str"])


def create_pydantic_json_file(
    pyobj: ty.Union[str, PyObj], path: pathlib.Path, **kwargs
):
    """
    loads a pyobj (which must be a pydantic model) and then saves the default Json to file.
    this requires defaults for all pydantic attributes.

    Todo:
        could extend the functionality to cover models that don't have defaults
        using [pydantic-factories](https://github.com/Goldziher/pydantic-factories)

    Args:
        pyobj (SerializableCallable): definition of where to get a pydantic model
        path (pathlib.Path): where to save the pydantic json
        **kwargs : passed to the pydantic model upon initiation

    Returns:
        path
    """
    if type(pyobj) == str:
        obj = SerializableCallable(pyobj).callable_obj
    else:
        obj = load_PyObj(pyobj)
    assert (
        str(type(obj)) == "<class 'pydantic.main.ModelMetaclass'>"
    ), "the python object must be a pydantic model"
    if not hasattr(obj, "file"):
        setattr(obj, "file", file)
    assert hasattr(
        obj, "file"
    ), "the pydantic BaseModel must be extended to have method 'file' for writing model to json"
    myobj = obj(**kwargs)
    myobj.file(path)
    return path


def remove_non_present_kwargs(callable_: ty.Callable, di: dict):
    """do this if required (get allowed args from callable)"""
    args = inspect.getfullargspec(callable_).args
    return {k_: v_ for k_, v_ in di.items() if k_ in args}


def get_ext(fpth):
    """get file extension including compound json files"""
    return "".join(pathlib.Path(fpth).suffixes).lower()


def st_mtime_string(path):
    """st_mtime_string for a given path"""
    try:
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
