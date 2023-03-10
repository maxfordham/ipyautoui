# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

"""
displayfile is used to display certain types of files.
The module lets us preview a file, open a file, and open its directory.

Example:
    ::#

        from ipyautoui.constants import load_test_constants
        from ipyautoui.displayfile import DisplayFile, Markdown
        import ipywidgets as w

        DIR_FILETYPES = load_test_constants().DIR_FILETYPES

        fpths = list(pathlib.Path(DIR_FILETYPES).glob("*"))

        # single file
        d = DisplayFile(fpths[7])
        display(d)

"""
# %run _dev_sys_path_append.py
# %run __init__.py
# %load_ext lab_black

# +
import pathlib
import functools
from wcmatch.pathlib import Path as wcPath
from IPython.display import (
    display,
    clear_output,
    Markdown,
)
import time
import typing as ty
import ipywidgets as w
import traitlets as tr
from pydantic import BaseModel, validator, HttpUrl

#  local imports
from ipyautoui.autodisplay_renderers import (
    DEFAULT_FILE_RENDERERS,
    handle_compound_ext,
)
from ipyautoui._utils import (
    open_file,
    make_new_path,
    frozenmap,
    get_ext,
    st_mtime_string,
)
from ipyautoui.constants import (
    #  BUTTON_WIDTH_MIN,
    BUTTON_HEIGHT_MIN,
    KWARGS_OPENPREVIEW,
    KWARGS_OPENFILE,
    KWARGS_OPENFOLDER,
    KWARGS_DISPLAY_ALL_FILES,
    KWARGS_COLLAPSE_ALL_FILES,
    KWARGS_HOME_DISPLAY_FILES,
)

import requests

# from mf library
# try:
#     from xlsxtemplater import from_excel
# except:
#     pass


# -


def merge_default_renderers(
    renderers: dict[str, ty.Callable],
    default_renderers: frozenmap[str, ty.Callable] = DEFAULT_FILE_RENDERERS,
) -> dict[str, ty.Callable]:
    return {**dict(default_renderers), **renderers}


def get_renderers(
    renderers: ty.Optional[dict[str, ty.Callable]],
    extend_default_renderers: bool = True,
) -> dict[str, ty.Callable]:
    if renderers is None and not extend_default_renderers:
        raise ValueError("renderers must be given if extend_default_renderers is False")
    if renderers is not None and extend_default_renderers:
        return merge_default_renderers(renderers)
    else:
        return dict(DEFAULT_FILE_RENDERERS)


# +
class DisplayObjectActions(BaseModel):
    """base object with callables for creating a display object"""

    renderers: dict[str, ty.Callable] = dict(DEFAULT_FILE_RENDERERS)
    path: ty.Union[str, pathlib.Path, HttpUrl, ty.Callable]
    ext: str = None
    name: str = None
    check_exists: ty.Callable = None
    renderer: ty.Callable = None
    check_date_modified: ty.Callable = None

    @validator("renderer", always=True)
    def _renderer(cls, v, values):
        if v is None:
            ext = values["ext"]
            map_ = values["renderers"]
            if ext in map_.keys():
                fn = functools.partial(map_[ext], values["path"])
            else:
                fn = lambda: w.HTML("File renderer not found")
            return fn
        else:
            return functools.partial(v, values["path"])

    class Config:
        arbitrary_types_allowed = True


def check_exists(path):
    if path.is_file() or path.is_dir():
        return True
    else:
        return False


class DisplayFromPath(DisplayObjectActions):
    newroot: pathlib.PureWindowsPath = pathlib.PureWindowsPath("J:/")
    path_new: pathlib.Path = None
    open_file: ty.Callable = None
    open_folder: ty.Callable = None

    @validator("path", always=True)
    def _path(cls, v, values):
        return pathlib.Path(v)

    @validator("path_new", always=True)
    def _path_new(cls, v, values):
        return make_new_path(values["path"], newroot=values["newroot"])

    @validator("name", always=True)
    def _name(cls, v, values):
        if values["path"] is not None:
            v = values["path"].name
        return v

    @validator("ext", always=True)
    def _ext(cls, v, values):
        if values["path"] is not None:
            v = get_ext(values["path"])
            v = handle_compound_ext(v, renderers=values["renderers"])
        if v is None:
            ValueError("ext must be given to map data to renderer")
        return v

    @validator("check_exists", always=True)
    def _check_exists(cls, v, values):
        fn = functools.partial(check_exists, values["path"])
        return fn

    @validator("check_date_modified", always=True)
    def _date_modified(cls, v, values):
        p = values["path"]
        if p is not None:
            return functools.partial(st_mtime_string, p)
        else:
            return None

    @validator("open_file", always=True)
    def _open_file(cls, v, values):
        p = values["path"]
        if p is not None:
            fn = functools.partial(open_file, p, newroot=values["newroot"])
            return fn
        else:
            return lambda: "Error: path given is None"

    @validator("open_folder", always=True)
    def _open_folder(cls, v, values):
        p = values["path"]
        if not p.is_dir():
            p = p.parent
        if p is not None:
            fn = functools.partial(open_file, p, newroot=values["newroot"])
            return fn
        else:
            return lambda: "Error: path given is None"

    class Config:
        arbitrary_types_allowed = True


def url_ok(url):

    # exception block
    try:

        # pass the url into
        # request.head
        # response = requests.head(url)
        # ^ TODO : why doens't this work?

        response = requests.get(url)

        # check the status code
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.ConnectionError as e:
        return e


# TODO: create a DisplayFromRequest actions. for use with API queries...?
class DisplayFromRequest(DisplayObjectActions):
    path: HttpUrl

    @validator("check_exists", always=True)
    def _check_exists(cls, v, values):
        fn = functools.partial(url_ok, values["path"])
        return fn

    @validator("name", always=True)
    def _name(cls, v, values):
        return values["path"].path


def check_callable_in_namespace(fn: ty.Callable):  # NTO USED
    if fn.__name__ in globals():
        return True
    else:
        return False


def check_callable(fn: ty.Callable):  # NTO USED
    if isinstance(fn, ty.Callable):
        return True
    else:
        return False


class DisplayFromCallable(DisplayObjectActions):
    path: ty.Callable

    @validator("check_exists", always=True)
    def _check_exists(cls, v, values):
        return functools.partial(check_callable, values["path"])

    @validator("name", always=True)
    def _name(cls, v, values):
        if v is not None:
            return v
        else:
            return values["path"].__name__


# -

if __name__ == "__main__":
    d = DisplayFromPath(path="__init__.py")
    display(d.renderer())

# +
# TODO: separate out the bit that is display data and display from path...
# TODO: probs useful to have a `value` trait (allowing the object to be updated instead of remade)
#       this probably means having DisplayObject as a base class and extending it for display file...

ORDER_DEFAULT = ("exists", "openpreview", "openfile", "openfolder", "name")
ORDER_NOTPATH = ("exists", "openpreview", "name")


class DisplayObject(w.VBox):
    """
    class for displaying file-like objects.

    Args:
        auto_open: bool, auto opens preview of __init__
        order: list, controls how the UI displays:
            allowed values are: ("exists", "openpreview", "openfile", "openfolder", "name")
    """

    _value = tr.Unicode()
    auto_open = tr.Bool(default_value=False)
    order = tr.Tuple(default_value=ORDER_NOTPATH, allow_none=False)
    display_actions = tr.Instance(klass=DisplayObjectActions)

    @tr.validate("order")
    def _validate_order(self, proposal):
        for l in proposal["value"]:
            if l not in ORDER_DEFAULT:
                raise ValueError(
                    """
                    order must include the following: ("exists", "openpreview", "openfile", "openfolder", "name")
                """
                )
        order = self._check_order(proposal["value"])
        return order

    def _check_order(self, order):
        if order is None and isinstance(self.display_actions.path, pathlib.Path):
            return ORDER_DEFAULT
        elif order is None and not isinstance(self.display_actions.path, pathlib.Path):
            return ORDER_NOTPATH
        else:
            return order

    @tr.observe("order")
    def _observe_order(self, change):
        self._update_bx_bar(change["new"])

    @tr.observe("display_actions")
    def _display_actions(self, change):
        self._update_form()
        self._value = str(self.display_actions.path)

    def __init__(
        self,
        display_actions,
        **kwargs,
    ):
        """display object

        Args:
            display_actions (ty.Type[DisplayObjectActions]): actions used to display object
            auto_open (bool, optional): automatically display object data (i.e. auto-preview file). Defaults to False.
            order (tuple, optional): defines UI controls appearance. Defaults to None.
                allowed values are: ("exists", "openpreview", "openfile", "openfolder", "name")
                default is: ("exists", "openpreview", "openfile", "openfolder", "name")
                reduce tuple to hide components
        """

        self._init_form()  # generic form only
        self._init_controls()
        super().__init__(display_actions=display_actions, **kwargs)
        self._update_bx_bar(self.order)
        self.children = [self.bx_bar, self.bx_out]

    def _update_bx_bar(self, order):
        self.bx_bar.children = [getattr(self, l) for l in order]

    @classmethod
    def from_path(
        cls,
        path,
        newroot=pathlib.PureWindowsPath("J:/"),
        renderers=None,
        extend_default_renderers=True,
        auto_open=False,
    ):
        renderers = get_renderers(
            renderers=renderers, extend_default_renderers=extend_default_renderers
        )
        display_actions = DisplayFromPath(
            path=path, newroot=newroot, renderers=renderers
        )
        return cls(display_actions=display_actions, auto_open=auto_open)

    @classmethod
    def from_request(
        cls,
        path,
        ext,
        renderers=None,
        extend_default_renderers=True,
        auto_open=False,
    ):
        renderers = get_renderers(
            renderers=renderers, extend_default_renderers=extend_default_renderers
        )
        display_actions = DisplayFromRequest(path=path, ext=ext, renderers=renderers)
        return cls(display_actions=display_actions, auto_open=auto_open)

    @classmethod
    def from_callable(
        cls,
        path,
        ext,
        renderers=None,
        extend_default_renderers=True,
        auto_open=False,
    ):
        renderers = get_renderers(
            renderers=renderers, extend_default_renderers=extend_default_renderers
        )
        display_actions = DisplayFromCallable(path=path, ext=ext, renderers=renderers)
        return cls(display_actions=display_actions, auto_open=auto_open)

    def tooltip_openpath(self, path):
        return str(make_new_path(path, newroot=self.display_actions.newroot))

    def _init_form(self):
        self.exists = w.Valid(
            value=False,
            disabled=True,
            readout="-",
            tooltip="indicates if file exists",
            layout=w.Layout(width="20px", height=BUTTON_HEIGHT_MIN),
        )
        self.openpreview = w.ToggleButton(**KWARGS_OPENPREVIEW)
        self.openfile = w.Button(**KWARGS_OPENFILE)
        self.openfolder = w.Button(**KWARGS_OPENFOLDER)
        self.name = w.HTML(
            layout=w.Layout(justify_items="center"),
        )
        self.out_caller = w.Output()
        self.out = w.Output()
        self.out_caller.layout.display = "none"
        self.out.layout.display = "none"
        self.bx_bar = w.HBox()

        self.bx_out = w.VBox()
        self.bx_out.children = [self.out_caller, self.out]

    def _update_form(self):
        if isinstance(self.display_actions.path, pathlib.PurePath):
            self.openfile.tooltip = f"""
open file:
{self.tooltip_openpath(self.display_actions.path)}
"""
            self.openfolder.tooltip = f"""
open folder:
{self.tooltip_openpath(self.display_actions.path.parent)}
"""
        self.name.value = "<b>{0}</b>".format(self.display_actions.name)
        self.check_exists()

    def _init_controls(self):
        self.openfile.on_click(self._openfile)
        self.openfolder.on_click(self._openfolder)
        self.openpreview.observe(self._openpreview, names="value")

    def check_exists(self):
        if self.display_actions.check_exists is None:
            self.exists.value = False
        elif not self.display_actions.check_exists():
            self.exists.value = False
        elif self.display_actions.check_exists():
            self.exists.value = True
        else:
            raise ValueError("check_exists error")

    def _openpreview(self, onchange):
        if self.openpreview.value:
            self.openpreview.icon = "eye-slash"
            self.out.layout.display = ""

            with self.out:
                if (
                    hasattr(self.display_actions, "path")
                    and self.display_actions.check_exists()
                ):
                    display(self.display_actions.renderer())
                else:
                    display(Markdown("file does not exist"))
        else:
            self.openpreview.icon = "eye"
            self.out.layout.display = "none"
            with self.out:
                clear_output()

    def _openfile(self, sender):
        self.out_caller.layout.display = ""
        with self.out_caller:
            clear_output()
            self.display_actions.open_file()
            time.sleep(5)
            clear_output()
        self.out_caller.layout.display = "none"

    def _openfolder(self, sender):
        self.out_caller.layout.display = ""
        with self.out_caller:
            clear_output()
            self.display_actions.open_folder()
            time.sleep(5)
            clear_output()
        self.out_caller.layout.display = "none"


class DisplayPath(DisplayObject):
    _value = tr.Unicode(default_value="")

    def __init__(
        self,
        value,
        newroot=pathlib.PureWindowsPath("J:/"),
        renderers=None,
        extend_default_renderers=True,
        **kwargs,
    ):
        self.newroot = newroot
        self.renderers = get_renderers(
            renderers=renderers, extend_default_renderers=extend_default_renderers
        )
        display_actions = DisplayFromPath(
            path=value, newroot=self.newroot, renderers=self.renderers
        )
        super().__init__(display_actions=display_actions, **kwargs)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = ""
        self.display_actions = DisplayFromPath(
            path=value, newroot=self.newroot, renderers=self.renderers
        )


# -
if __name__ == "__main__":
    d = DisplayFromPath(path="__init__.py")
    do = DisplayObject(d)
    display(do)

if __name__ == "__main__":
    path = "https://catfact.ninja/fact"
    ext = ".json"
    display(DisplayFromRequest(path=path, ext=ext).renderer())


if __name__ == "__main__":
    path = "https://catfact.ninja/fact"
    ext = ".json"

    def get_catfact():
        return requests.get(path).content

    display(DisplayFromCallable(path=get_catfact, ext=ext).renderer())

if __name__ == "__main__":

    path = "https://catfact.ninja/fact"
    ext = ".json"
    display(DisplayObject.from_request(path=path, ext=ext))

if __name__ == "__main__":

    ext = ".json"
    dobj = DisplayObject.from_callable(path=get_catfact, ext=ext)
    display(dobj)

if __name__ == "__main__":
    import json
    from datetime import datetime

    def display_catfact(path):
        if callable(path):
            di = json.loads(path())
        else:
            di = json.loads(requests.get(path).content)
        s = f"""
🐱🐈😹 **CAT FACT** 😾🙀😿

{di['fact']}

*{datetime.now().strftime("%Y-%m-%d, %H:%M:%S")} - https://cat-fact.herokuapp.com/#/*"""
        return Markdown(s)

    path = "https://catfact.ninja/fact"
    ext = ".catfact"
    d = DisplayObject.from_request(
        path=path, ext=ext, renderers={".catfact": display_catfact}
    )
    display(d)

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.autoui import AutoUi
    from ipyautoui.constants import load_test_constants

    tests_constants = load_test_constants()
    DIR_FILETYPES = load_test_constants().DIR_FILETYPES
    paths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
    path = paths[6]
    d = DisplayObject.from_path(path)
    display(d)
    # ------------------


if __name__ == "__main__":
    d1 = DisplayPath(path)
    display(d1)

if __name__ == "__main__":
    d.order = (
        "openpreview",
        "name",
    )
    d.auto_open = True

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic

    user_file_renderers = AutoUi.create_autodisplay_map(
        ext=".aui.json", schema=TestAutoLogic
    )
    path1 = tests_constants.PATH_TEST_AUI

    d = DisplayObject.from_path(path1, renderers=user_file_renderers)
    display(d)

# +
from wcmatch import fnmatch


class AutoDisplay(tr.HasTraits):
    """
    displays the contents of a file in the notebook.
    comes with the following default renderers:
    DEFAULT_FILE_RENDERERS = {
        '.csv': csv_prev,
        '.json': json_prev,
        '.plotly': plotlyjson_prev,
        '.plotly.json': plotlyjson_prev,
        '.vg.json': vegajson_prev,
        '.vl.json': vegalitejson_prev,
        '.ipyui.json': ipyuijson_prev,
        '.yaml': yaml_prev,
        '.yml': yaml_prev,
        '.png': img_prev,
        '.jpg': img_prev,
        '.jpeg': img_prev,
        #'.obj': obj_prev, # add ipyvolume viewer?
        '.txt': txt_prev,
        '.md': md_prev,
        '.py': py_prev,
        '.pdf': pdf_prev,
    }
    user_file_renderers can be passed to class provided they have the correct
    dict format: user_file_renderers = {'.ext': myrenderer}
    notice that the class allows for "compound" filetypes, especially useful for .json files
    if you want to display the data in a specific way.
    """

    #     _paths = tr.List()

    #     @validate("_paths")
    #     def _valid_value(self, proposal):
    #         """makes path a wcmatch.Path (for enhanced pattern matching) and filters out directories"""
    #         return [wcPath(p) for p in proposal["value"] if not pathlib.Path(p).is_dir()]

    def __init__(
        self,
        display_objects_actions: ty.List[DisplayObjectActions],
        patterns: ty.Union[
            str, ty.List, None
        ] = None,  # TODO: add pattern matching. currently only works with paths
        title: ty.Union[str, None] = None,
        display_showhide: bool = True,
    ):
        """
        Args:
            display_objects_actions (ty.List[DisplayObjectActions]):
            patterns: (str or list), patterns to auto-open
            title: (str), default = None,
            display_showhide: bool = True,


        """
        self._init_form()
        self._init_controls()
        self.title = title
        self._display_objects_actions = display_objects_actions

        self.display_objects_actions = display_objects_actions
        self.display_showhide = display_showhide
        self.patterns = patterns

    @classmethod
    def from_paths(
        cls,
        paths: ty.List[pathlib.Path],
        newroot=pathlib.PureWindowsPath("J:/"),  # TODO: maproots
        renderers=None,
        patterns: ty.Union[str, ty.List] = None,
        title: ty.Union[str, None] = None,
        display_showhide: bool = True,
    ):
        if renderers is not None:
            renderers = merge_default_renderers(renderers)
        else:
            renderers = DEFAULT_FILE_RENDERERS
        if not isinstance(paths, list):
            paths = [pathlib.Path(paths)]

        display_objects_actions = cls.actions_from_paths(
            paths=paths,
            newroot=newroot,
            renderers=renderers,
        )
        return cls(
            display_objects_actions,
            patterns=patterns,
            title=title,
            display_showhide=display_showhide,
        )

    @classmethod
    def from_requests(
        cls,
        map_requests: ty.Dict[str, HttpUrl],
        renderers: ty.Optional[ty.Dict[str, ty.Callable]] = None,
        extend_default_renderers: bool = True,
        patterns: ty.Union[str, ty.List] = None,
        title: ty.Union[str, None] = None,
        display_showhide: bool = True,
    ):
        renderers = get_renderers(renderers, extend_default_renderers)

        display_objects_actions = cls.actions_from_requests(
            map_requests=map_requests,
            renderers=renderers,
        )
        return cls(
            display_objects_actions,
            patterns=patterns,
            title=title,
            display_showhide=display_showhide,
        )

    @classmethod
    def from_callables(
        cls,
        map_callables: ty.Dict[str, ty.Callable],
        renderers=None,
        extend_default_renderers=True,
        patterns: ty.Union[str, ty.List] = None,
        title: ty.Union[str, None] = None,
        display_showhide: bool = True,
    ):
        renderers = get_renderers(renderers, extend_default_renderers)

        display_objects_actions = cls.actions_from_callables(
            map_callables=map_callables,
            renderers=renderers,
        )
        return cls(
            display_objects_actions,
            patterns=patterns,
            title=title,
            display_showhide=display_showhide,
        )

    @classmethod
    def from_any(
        cls,
        paths: ty.List[
            ty.Union[ty.Dict[str, HttpUrl], ty.Dict[str, ty.Callable], pathlib.Path]
        ],
        renderers=None,
        extend_default_renderers=True,
        patterns: ty.Union[str, ty.List] = None,
        title: ty.Union[str, None] = None,
        display_showhide: bool = True,
    ):
        renderers = get_renderers(renderers, extend_default_renderers)
        if not isinstance(paths, list):
            paths = [paths]

        display_objects_actions = cls.actions_from_any(
            paths=paths,
            renderers=renderers,
        )
        return cls(
            display_objects_actions,
            patterns=patterns,
            title=title,
            display_showhide=display_showhide,
        )

    @staticmethod
    def actions_from_any(
        paths: ty.List[pathlib.Path],
        renderers=None,
    ):
        def choose(path, renderers):
            if isinstance(path, pathlib.Path):
                return DisplayFromPath(path=path, renderers=renderers)
            elif isinstance(path, dict):
                if len(path) == 1:
                    k, v = list(path.items())[0]
                    if isinstance(v, pathlib.Path):
                        return DisplayFromPath(path=v, ext=k, renderers=renderers)
                    elif isinstance(v, HttpUrl):
                        return DisplayFromRequest(path=v, ext=k, renderers=renderers)
                    elif callable(v):
                        return DisplayFromCallable(path=v, ext=k, renderers=renderers)
                    else:
                        raise TypeError(
                            f"expected pathlib.Path or HttpUrl, got {type(v)}"
                        )
                else:
                    raise TypeError(
                        f"expected a dict with one key, got {len(path)} keys"
                    )
            else:
                raise TypeError(f"expected pathlib.Path or dict, got {type(path)}")

        return [choose(path=path, renderers=renderers) for path in paths]

    @staticmethod
    def actions_from_paths(
        paths: ty.List[pathlib.Path],
        newroot=pathlib.PureWindowsPath("J:/"),  # maproots
        renderers=None,
    ):
        return [
            DisplayFromPath(path=path, newroot=newroot, renderers=renderers)
            for path in paths
        ]

    @staticmethod
    def actions_from_requests(map_requests: ty.Dict[str, HttpUrl], renderers=None):
        return [
            DisplayFromRequest(path=v, ext=k, renderers=renderers)
            for k, v in map_requests.items()
        ]

    @staticmethod
    def actions_from_callables(
        map_callables: ty.Dict[str, ty.Callable], renderers=None
    ):
        return [
            DisplayFromCallable(path=v, ext=k, renderers=renderers)
            for k, v in map_callables.items()
        ]

    def add_from_paths(
        self,
        paths,
        newroot=pathlib.PureWindowsPath("J:/"),
        renderers=None,
    ):
        if renderers is not None:
            renderers = merge_default_renderers(renderers)
        else:
            renderers = DEFAULT_FILE_RENDERERS
        paths = [p for p in paths if p not in self.paths]
        _new_actions = self.actions_from_paths(
            paths=paths, newroot=newroot, renderers=renderers
        )
        actions = self.display_objects_actions + _new_actions
        self.display_objects_actions = actions

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        if self.title is None:
            self.box_title.children = []
        else:
            self.box_title.children = [w.HTML(self.title)]

    @property
    def display_showhide(self):
        return self._display_showhide

    @display_showhide.setter
    def display_showhide(self, value):
        if hasattr(self, "display_objects") and len(self.display_objects) == 1:
            value = False
        self._display_showhide = value
        if self.display_showhide:
            self.box_showhide.children = [
                w.HBox(layout=w.Layout(width="24px", height=BUTTON_HEIGHT_MIN)),
                self.b_display_all,
                self.b_collapse_all,
                self.b_display_default,
            ]
        else:
            self.box_showhide.children = []

    @property
    def paths(self):
        return [d.path for d in self.display_objects_actions]

    @property
    def map_names_paths(self):
        return {d.name: d.path for d in self.display_objects_actions}

    @property
    def display_objects_actions(self):
        return self._display_objects_actions

    @display_objects_actions.setter
    def display_objects_actions(self, display_objects_actions):
        self._display_objects_actions = display_objects_actions
        self.display_objects = [DisplayObject(d) for d in display_objects_actions]

        self.box_files.children = self.display_objects

    @property
    def patterns(self):
        return self._patterns

    @patterns.setter
    def patterns(self, value):
        self._patterns = value
        if value is None:
            self.b_display_default.layout.display = "None"
            self.auto_open = [False] * len(self.paths)
        else:
            match = (
                lambda name, path: str(path) if isinstance(path, pathlib.Path) else name
            )
            self.auto_open = [
                fnmatch.fnmatch(match(name, path), patterns=self.patterns)
                for name, path in self.map_names_paths.items()
            ]
            if sum(self.auto_open) == len(self.paths):
                self.b_display_default.layout.display = "None"
            else:
                self.b_display_default.layout.display = ""

    @property
    def auto_open(self):
        return [d.auto_open for d in self.display_objects]

    @auto_open.setter
    def auto_open(self, value):
        [
            setattr(d, "auto_open", v)
            for d, v in dict(zip(self.display_objects, value)).items()
        ]

    def _init_form(self):
        self.b_display_all = w.Button(**KWARGS_DISPLAY_ALL_FILES)
        self.b_collapse_all = w.Button(**KWARGS_COLLAPSE_ALL_FILES)
        self.b_display_default = w.Button(**KWARGS_HOME_DISPLAY_FILES)
        self.box_header = w.VBox()
        self.box_showhide = w.HBox()
        self.box_title = w.HBox()
        self.box_header.children = [self.box_title, self.box_showhide]
        self.box_files = w.VBox()
        self.box_form = w.VBox()
        self.box_form.children = [self.box_header, self.box_files]

    def _init_controls(self):
        self.b_display_all.on_click(self.display_all)
        self.b_collapse_all.on_click(self.collapse_all)
        self.b_display_default.on_click(self.display_default)

    def display_all(self, onclick=None):
        for d in self.display_objects:
            d.openpreview.value = True

    def collapse_all(self, onclick=None):
        for d in self.display_objects:
            d.openpreview.value = False

    def display_default(self, onclick=None):
        for d, a in zip(self.display_objects, self.auto_open):
            d.openpreview.value = a

    def display(self):
        display(self.box_form)

    def _ipython_display_(self):
        self.display()

    def _activate_waiting(self):
        [d._activate_waiting() for d in self.display_objects]

    def _update_files(self):
        [d._update_file() for d in self.display_objects]


# +
# TODO: render pdf update the relative path

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.autoui import AutoUi
    from ipyautoui.constants import load_test_constants

    tests_constants = load_test_constants()
    DIR_FILETYPES = load_test_constants().DIR_FILETYPES
    paths = list(pathlib.Path(DIR_FILETYPES).glob("*"))
    ad = AutoDisplay.from_paths(
        paths, newroot=pathlib.PureWindowsPath("C:/"), patterns="*.csv"
    )
    display(ad)
# -
if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic

    user_file_renderers = AutoUi.create_autodisplay_map(
        ext=".aui.json", schema=TestAutoLogic
    )

    test_ui = AutoDisplay.from_paths(
        paths=[tests_constants.PATH_TEST_AUI],
        renderers=user_file_renderers,
        display_showhide=False,
    )

    display(test_ui)

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic

    test_ui = AutoDisplay.from_requests(
        map_requests={
            ".catfact": "https://catfact.ninja/fact",
            ".json": "https://official-joke-api.appspot.com/random_joke",
        },
        renderers={".catfact": display_catfact},
        display_showhide=False,
    )

    display(test_ui)

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from pydantic import parse_obj_as

    test_ui = AutoDisplay.from_any(
        paths=[
            {".catfact": parse_obj_as(HttpUrl, "https://catfact.ninja/fact")},
            {".catfact": get_catfact},
            paths[0],
        ],
        renderers={".catfact": display_catfact},
        display_showhide=False,
        patterns="get_catfact",
    )

    display(test_ui)

if __name__ == "__main__":
    import json
    from datetime import datetime

    def display_catfact(path):
        di = json.loads(requests.get(path).content)
        s = f"""
🐱🐈😹 **CAT FACT** 😾🙀😿

{di['fact']}

*{datetime.now().strftime("%Y-%m-%d, %H:%M:%S")} - https://cat-fact.herokuapp.com/#/*"""
        return Markdown(s)

    path = "https://catfact.ninja/fact"
    ext = ".catfact"
    d1 = DisplayFromRequest(path=path, ext=ext, renderer=display_catfact)

    path = "https://official-joke-api.appspot.com/random_joke"
    ext = ".json"
    d2 = DisplayFromRequest(path=path, ext=ext)

    test_display = AutoDisplay([d1, d2])
    display(Markdown("### From requests: "))
    display(test_display)


