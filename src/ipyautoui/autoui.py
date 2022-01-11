# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# TODO: add ipyvuetify-jsonschema to this repo

# %run __init__.py
# %load_ext lab_black
import pathlib
import functools
import pandas as pd
import ipywidgets as widgets
from IPython.display import display, Markdown
from datetime import datetime, date
from dataclasses import dataclass
from pydantic import BaseModel
from markdown import markdown
import immutables
import json
import traitlets
import typing
from enum import Enum

from ipyautoui.displayfile import PreviewPy
from ipyautoui.test_schema import TestAutoLogic
from ipyautoui._utils import obj_from_string, display_pydantic_json
from ipyautoui.custom import Grid, FileChooser
from ipyautoui.constants import DI_JSONSCHEMA_WIDGET_MAP, BUTTON_WIDTH_MIN

from ipyautoui.constants import load_test_constants
from ipyautoui.test_schema import TestAutoLogic
# +
def display_template_ui_model():
    display(PreviewPy(test_schema, docstring_priority=False))


#  -- ATTACH DEFINITIONS TO PROPERTIES ----------------------
def recursive_search_schema(sch: typing.Dict, li: typing.List) -> typing.Dict:
    """searches down schema tree to retrieve definitions

    Args:
        sch (typing.Dict): json schema made from pydantic
        li (typing.List): list of keys to search down tree

    Returns:
        typing.Dict: definition retrieved from schema
    """
    if len(li) > 1:
        f = li[0]
        li_tmp = li[1:]
        sch_tmp = sch[f]
        return recursive_search_schema(sch_tmp, li_tmp)
    else:
        return sch[li[0]]


def update_property_from_definition(
    sch: typing.Dict, item: typing.Dict, key: typing.Any
) -> typing.Dict:
    """attaches definition back to properties in schema

    Args:
        sch (typing.Dict): json schema
        item (typing.Dict): definition item
        key (typing.Any): what to search for (#ref)

    Returns:
        typing.Dict: sch
    """
    k = list(item.keys())[0]
    v = list(item.values())[0]

    li_filt = v[key].split("/")[1:]
    definition = recursive_search_schema(sch, li_filt)

    di_new = {}
    for k_, v_ in item.items():
        di_new[k_] = definition

    sch["properties"][k] = di_new[k]
    return sch


def update_property_definitions(sch: typing.Dict, key: str):
    """attaches all definitions back to properties.
    TODO - currently only looks at the first level!

    Args:
        sch (typing.Dict): [description]
        key (str): [description]

    Returns:
        [type]: [description]
    """
    li_definitions = [{k: v} for k, v in sch["properties"].items() if key in v]
    for l in li_definitions:
        sch = update_property_from_definition(sch, l, key)
    return sch


#  ----------------------------------------------------------

#  -- CHANGE JSON-SCHEMA KEYS TO IPYWIDGET KEYS -------------
def update_key(key, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    if key in di_map.keys():
        return di_map[key]
    else:
        return key


def update_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    return {update_key(k, di_map): v for k, v in di.items()}


def add_description_field(di):
    for k, v in di.items():
        if "description" not in v:
            v["description"] = ""
        # t=v['title']
        # d=v['description']
        # v['description'] = f"<b>{t}</b>, <i>{d}</i>"

    return di


def rename_schema_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP):
    di = add_description_field(di)
    rename = {k: update_keys(v, di_map) for k, v in di.items()}
    return rename


def call_rename_schema_keys(di, di_map=DI_JSONSCHEMA_WIDGET_MAP, rename_keys=True):
    if rename_keys:
        return rename_schema_keys(di, di_map=di_map)
    else:
        return di


#  ----------------------------------------------------------

#  -- HELPER FUNCTIONS --------------------------------------
def get_type(pr, typ="string"):
    return {k: v for k, v in pr.items() if v["type"] == typ}


def get_format(pr, typ="date"):
    pr = {k: v for k, v in pr.items() if "format" in v}
    return {k: v for k, v in pr.items() if v["format"] == typ}


def get_range(pr, typ="integer"):
    array = get_type(pr, typ="array")
    array = {k: v for k, v in array.items() if len(v["items"]) == 2}
    tmp = {}
    for k, v in array.items():
        tmp[k] = v
        for i in v["items"]:
            if "minimum" not in i and "maximum" not in i:
                tmp = {}
    if len(tmp) == 0:
        return tmp
    else:
        rng = {k: v for k, v in tmp.items() if v["items"][0]["type"] == typ}
        for k, v in rng.items():
            rng[k]["minimum"] = v["items"][0]["minimum"]
            rng[k]["maximum"] = v["items"][0]["maximum"]
    return rng


def drop_enums(pr):
    return {k: v for k, v in pr.items() if "enum" not in v}


def find_enums(pr):
    return {k: v for k, v in pr.items() if "enum" in v}


def drop_explicit_autoui(pr):
    return {k: v for k, v in pr.items() if "autoui" not in v}


def find_explicit_autoui(pr):
    return {k: v for k, v in pr.items() if "autoui" in v}


#  ----------------------------------------------------------

#  -- FILTER FUNCTIONS --------------------------------------
#  -- find relevant inputs from json-schema properties ------
def get_IntText(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    ints = get_type(pr, typ="integer")
    simple_ints = {
        k: v for k, v in ints.items() if "minimum" not in v and "maximum" not in v
    }
    return call_rename_schema_keys(simple_ints, rename_keys=rename_keys)


def get_IntSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    ints = get_type(pr, typ="integer")
    simple_ints = {k: v for k, v in ints.items() if "minimum" in v and "maximum" in v}
    return call_rename_schema_keys(simple_ints, rename_keys=rename_keys)


def get_FloatText(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    floats = get_type(pr, typ="number")
    simple_floats = {
        k: v for k, v in floats.items() if "minimum" not in v and "maximum" not in v
    }
    return call_rename_schema_keys(simple_floats, rename_keys=rename_keys)


def get_FloatSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    floats = get_type(pr, typ="number")
    simple_floats = {
        k: v for k, v in floats.items() if "minimum" in v and "maximum" in v
    }
    return call_rename_schema_keys(simple_floats, rename_keys=rename_keys)


def get_Text(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    strings = get_type(pr)
    short_strings = drop_enums(strings)
    # short_strings = {k:v for k,v in strings.items() if 'maxLength' in v and v['maxLength']<200}
    return call_rename_schema_keys(short_strings, rename_keys=rename_keys)


def get_Textarea(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    strings = get_type(pr)
    simple_strings = drop_enums(strings)
    long_strings = {
        k: v for k, v in strings.items() if "maxLength" in v and v["maxLength"] >= 200
    }
    return call_rename_schema_keys(long_strings, rename_keys=rename_keys)


def get_Dropdown(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    drops = find_enums(pr)
    drops = {k: v for k, v in drops.items() if v["type"] != "array"}
    return call_rename_schema_keys(drops, rename_keys=rename_keys)


def get_SelectMultiple(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    mult = find_enums(pr)
    mult = {k: v for k, v in mult.items() if v["type"] == "array"}
    return call_rename_schema_keys(mult, rename_keys=rename_keys)


def get_Checkbox(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    return call_rename_schema_keys(get_type(pr, typ="boolean"), rename_keys=rename_keys)


def get_DatePicker(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    date = get_type(pr, "string")
    date = get_format(date)
    for k, v in date.items():
        if type(v["default"]) == str:
            v["default"] = datetime.strptime(v["default"], "%Y-%m-%d").date()
    return call_rename_schema_keys(date, rename_keys=rename_keys)


def get_FileChooser(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    file = get_type(pr, "string")
    file = get_format(file, typ="path")
    return call_rename_schema_keys(file, rename_keys=rename_keys)


def get_DataGrid(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    grid = get_type(pr, "string")
    grid = get_format(grid, typ="DataFrame")
    return call_rename_schema_keys(grid, rename_keys=rename_keys)


def get_ColorPicker(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    color = get_type(pr, "string")
    color = get_format(color, typ="color")
    return call_rename_schema_keys(color, rename_keys=rename_keys)


def get_IntRangeSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    return call_rename_schema_keys(
        get_range(pr, typ="integer"), rename_keys=rename_keys
    )


def get_FloatRangeSlider(pr, rename_keys=True):
    pr = drop_explicit_autoui(pr)
    return call_rename_schema_keys(get_range(pr, typ="number"), rename_keys=rename_keys)


def get_AutoOveride(pr, rename_keys=True):
    pr = find_explicit_autoui(pr)
    return call_rename_schema_keys(pr, rename_keys=rename_keys)


#  ----------------------------------------------------------

#  -- WIDGET MAPPING ----------------------------------------
#  -- uses filter functions to map schema objects to widgets
def auto_overide(str_widget_type):
    return obj_from_string(str_widget_type)


class WidgetMapper(BaseModel):
    """defines a filter function and associated widget. the "fn_filt" is used to search the
    json schema to find appropriate objects, the objects are then passed to the "widget" for the ui
    """

    fn_filt: typing.Callable
    widget: typing.Callable


DI_WIDGETS_MAPPER = {
    "IntText": WidgetMapper(fn_filt=get_IntText, widget=widgets.IntText),
    "IntSlider": WidgetMapper(fn_filt=get_IntSlider, widget=widgets.IntSlider),
    "FloatText": WidgetMapper(fn_filt=get_FloatText, widget=widgets.FloatText),
    "FloatSlider": WidgetMapper(fn_filt=get_FloatSlider, widget=widgets.FloatSlider),
    "Text": WidgetMapper(fn_filt=get_Text, widget=widgets.Text),
    "Textarea": WidgetMapper(fn_filt=get_Textarea, widget=widgets.Textarea),
    "Dropdown": WidgetMapper(fn_filt=get_Dropdown, widget=widgets.Dropdown),
    "SelectMultiple": WidgetMapper(
        fn_filt=get_SelectMultiple, widget=widgets.SelectMultiple
    ),
    "Checkbox": WidgetMapper(fn_filt=get_Checkbox, widget=widgets.Checkbox),
    "DatePicker": WidgetMapper(fn_filt=get_DatePicker, widget=widgets.DatePicker),
    "FileChooser": WidgetMapper(fn_filt=get_FileChooser, widget=FileChooser),
    "Grid": WidgetMapper(fn_filt=get_DataGrid, widget=Grid),
    "ColorPicker": WidgetMapper(fn_filt=get_ColorPicker, widget=widgets.ColorPicker),
    "IntRangeSlider": WidgetMapper(
        fn_filt=get_IntRangeSlider, widget=widgets.IntRangeSlider
    ),
    "FloatRangeSlider": WidgetMapper(
        fn_filt=get_FloatRangeSlider, widget=widgets.FloatRangeSlider
    ),
    "AutoOveride": WidgetMapper(fn_filt=get_AutoOveride, widget=auto_overide),
}


def map_to_widget(
    sch: typing.Dict, di_widgets_mapper: typing.Dict = None
) -> typing.Dict:
    """maps the widgets to the appropriate data using the di_widgets_mapper.
    also renames json schema keys to names that ipywidgets can understand.

    Args:
        sch (typing.Dict): [description]
        di_widgets_mapper (typing.Dict, optional): [description]. Defaults to DI_WIDGETS_MAPPER.
            if new mappings given they extend DI_WIDGETS_MAPPER. it is expected that renaming
            schema keys (call_rename_schema_keys) is done in the filter function

    Returns:
        typing.Dict: a dict (same order as original) with widget type
    """
    if di_widgets_mapper is None:
        di_widgets_mapper = DI_WIDGETS_MAPPER
    else:
        di_widgets_mapper = {**DI_WIDGETS_MAPPER, **di_widgets_mapper}
    sch = update_property_definitions(sch, "$ref")
    pr = sch["properties"]
    li_pr = pr.keys()
    di_ = {}
    for k, v in di_widgets_mapper.items():
        di = v.fn_filt(pr)
        for k_, v_ in di.items():
            di_[k_] = v_
            if "autoui" not in v_:
                di_[k_]["autoui"] = v.widget
            else:
                di_[k_]["autoui"] = v.widget(v_["autoui"])
    not_matched = set(di_.keys()) ^ set(li_pr)
    if len(not_matched) > 0:
        print("the following UI items from schema not matched to a widget:")
        print(not_matched)
    li_ordered = [l for l in li_pr if l not in not_matched]
    di_ordered = {l: di_[l] for l in li_ordered}
    return di_ordered


# -

if __name__ == "__main__":
    from ipyautoui.test_schema import TestAutoLogic
    from ipyautoui.constants import load_test_constants

    test_constants = load_test_constants()
    test = TestAutoLogic()
    sch = test.schema()
    mapped = map_to_widget(sch)
    [print(f"{k} --> {v['autoui']}") for k, v in mapped.items()]


# +
def _init_widgets_and_rows(pr: typing.Dict) -> tuple((widgets.VBox, typing.Dict)):
    """initiates widget for from dict built from schema

    Args:
        pr (typing.Dict): schema properties - sanitised for ipywidgets

    Returns:
        (widgets.VBox, typing.Dict): box with widgets, di of widgets
    """
    di_widgets = {k: v["autoui"](**v) for k, v in pr.items()}
    labels = {
        k: widgets.HTML(f"<b>{v['title']}</b>, <i>{v['autoui_description']}</i>")
        for k, v in pr.items()
    }
    ui_box = widgets.VBox()
    rows = []
    for (k, v), (k2, v2) in zip(di_widgets.items(), labels.items()):
        rows.append(widgets.HBox([v, v2]))
    ui_box.children = rows
    return ui_box, di_widgets


from ipyautoui._utils import file


class SaveControls(str, Enum):
    save_on_edit = "save_on_edit"  #  TODO: test this
    save_buttonbar = "save_buttonbar"
    disable_edits = "disable_edits"  #  TODO: implement this
    # archive_versions = 'archive_versions' #  TODO: implement this?


class AutoUiConfig(BaseModel):
    pydantic_model: typing.Type[BaseModel]
    widgets_mapper: typing.Dict[str, WidgetMapper] = DI_WIDGETS_MAPPER
    save_controls: SaveControls = SaveControls.save_buttonbar
    show_raw: bool = True
    ext: str = ".aui.json"


def save():
    print("save")


def revert():
    print("revert")


class SaveButtonBar:
    def __init__(
        self,
        save: typing.Callable = save,
        revert: typing.Callable = revert,
        fn_onsave: typing.Callable = lambda: None,
    ):
        """
        UI save dialogue 
        
        Args: 
            save: typing.Callable, zero input fn called on click of save button
            revert: typing.Callable, zero input fn called on click of revert button
            fn_onsave: typing.Callable, additional action that can be added to save button click
        
        """
        self.fn_save = save
        self.fn_revert = revert
        self.fn_onsave = fn_onsave
        self.out = widgets.Output()
        self._init_form()
        self._init_controls()

    def _init_form(self):
        self.unsaved_changes = widgets.ToggleButton(
            disabled=True, layout=widgets.Layout(width=BUTTON_WIDTH_MIN)
        )
        self.revert = widgets.Button(
            icon="fa-undo",
            tooltip="revert to last save",
            button_style="warning",
            style={"font_weight": "bold"},
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )  # ,button_style='success'
        self.save = widgets.Button(
            icon="fa-save",
            tooltip="save changes",
            button_style="success",
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
        )
        self.showraw = widgets.ToggleButton(
            icon="code",
            layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
            tooltip="show raw text data",
            style={"font_weight": "bold", "button_color": None},
        )
        self.message = widgets.HTML("a message")
        children = [self.unsaved_changes, self.revert, self.save]
        children.append(self.message)
        self.save_buttonbar = widgets.HBox(children)

    def _init_controls(self):
        self.save.on_click(self._save)
        self.revert.on_click(self._revert)

    def _save(self, click):
        self.fn_save()
        self.message.value = markdown(
            f'_changes saved: {datetime.now().strftime("%H:%M:%S")}_'
        )
        self._unsaved_changes(False)
        self.fn_onsave()

    def _revert(self, click):
        self.fn_revert()
        self.message.value = markdown(f"_UI reverted to last save_")
        self._unsaved_changes(False)

    def _unsaved_changes(self, istrue: bool):
        if istrue:
            self.unsaved_changes.button_style = "danger"
            self.unsaved_changes.icon = "circle"
            self.tooltip = "DANGER: changes have been made since the last save"
        else:
            self.unsaved_changes.button_style = "success"
            self.unsaved_changes.icon = "check"
            self.tooltip = "SAFE: no changes have been made since the last save"

    def display(self):
        with self.out:
            display(self.save_buttonbar)
        display(self.out)

    def _ipython_display_(self):
        self.display()


# +
def displayfile_renderer(path, renderer=None):
    if renderer is None:
        raise ValueError("renderer must not be None")
    display(renderer(path))


class AutoUi(widgets.VBox, traitlets.HasTraits):
    """AutoUi widget. generates UI form from pydantic schema. keeps the "value" field
    up-to-date on_change

    Args:
        traitlets.HasTraits ([type]): traitlets.HasTraits makes it possible to observe the value
            of this widget.
    """

    value = traitlets.Dict()
    _pydantic_model: BaseModel = None

    def __init__(
        self,
        pydantic_obj: typing.Type[BaseModel],
        config_autoui: AutoUiConfig = None,
        path: pathlib.Path = None,
        fn_onsave: typing.Callable = lambda: None,
    ):
        """init AutoUi

        Args:
            pydantic_obj (typing.Type[BaseModel]): initiated pydantic data object
            config_autoui (AutoUiConfig): _default = None_.
                pydantic_model: model definition
                widgets_mapper: maps ipywidgets to datatypes in the pydantic_model json schema
                save_controls: enum, handles saving to file
                ext: compound json file extension. maps type to UI reader.
            path (pathlib.Path): save file to path

        Returns:
            display self.ui_form in Notebook

        Example:
            # import example
            from ipyautoui.test_schema import TestAutoLogic
            # from ipyautoui.autoui import display_template_ui_model
            # display_template_ui_model()
            # ^ view python / pydantic definition for TestAutoLogic
            # ?TestAutoLogic
            # ^ inspect TestAutoLogic

            # create AutoUi instance
            from ipyautoui.autoui import AutoUi, AutoUiConfig
            config_autoui = AutoUiConfig(pydantic_model=TestAutoLogic, ext='.aui.json')
            testui = TestAutoLogic()
            path = pathlib.Path('test.aui.json')
            ui = AutoUi(pydantic_object=testui, config_autoui=config_autoui, path=path)
            display(ui)
        """

        self.pydantic_obj = pydantic_obj
        self.fn_onsave = fn_onsave
        if config_autoui is None:
            self.config_autoui = AutoUiConfig(pydantic_model=type(pydantic_obj))
        else:
            assert self.config_autoui.pydantic_model == type(
                self.pydantic_obj
            ), "self.config_autoui.pydantic_model != type(self.pydantic_obj)"
        self.path = path
        self.save_on_edit = False
        self._init_ui()

    @property
    def pydantic_obj(self):
        return self._pydantic_obj

    @pydantic_obj.setter
    def pydantic_obj(self, pydantic_obj):
        self._pydantic_obj = pydantic_obj
        self.value = (
            self.pydantic_obj.dict()
        )  # json.loads(self.pydantic_obj.json()) # set value
        if hasattr(self, "di_widgets"):
            for k, v in self.value.items():
                if k in self.di_widgets.keys():
                    self.di_widgets[k].value = v
                else:
                    print(
                        f"no widget created for {k}. fix this in the schema! TODO: fix the schema reader and UI to support nesting. or use ipyvuetify"
                    )

    def _extend_pydantic_base_model(self):
        setattr(self.config_autoui.pydantic_model, "file", file)

    def _init_ui(self):
        self._extend_pydantic_base_model()
        self._init_schema()
        self._init_form()
        self._init_titlebox()
        self._init_save_dialogue()
        self._init_controls()

    def _init_schema(self):
        sch = self.pydantic_obj.schema().copy()
        key = "$ref"
        self.sch = update_property_definitions(sch, key)
        self.pr = map_to_widget(
            self.sch, di_widgets_mapper=self.config_autoui.widgets_mapper
        )

    def _init_form(self):
        super().__init__(
            layout=widgets.Layout(width="100%", display="flex", flex="flex-grow")
        )  # main container
        self.ui_header = widgets.VBox()
        self.ui_main = widgets.VBox()

        self.ui_titlebox = widgets.VBox()
        self.ui_buttonbar = widgets.HBox()
        self.ui_header.children = [self.ui_buttonbar, self.ui_titlebox]

        self.ui_box, self.di_widgets = _init_widgets_and_rows(self.pr)
        self.ui_main.children = [self.ui_box]
        self.children = [self.ui_header, self.ui_main]

    def _init_titlebox(self):
        children = []
        titlebox_children = []
        self.titlebox = widgets.HBox()
        children.append(self.titlebox)

        if self.config_autoui.show_raw:
            self.showraw = widgets.ToggleButton(
                icon="code",
                layout=widgets.Layout(width=BUTTON_WIDTH_MIN),
                tooltip="show raw data",
                style={"font_weight": "bold", "button_color": None},
            )
            titlebox_children.append(self.showraw)
        self.title = widgets.HTML(f"<big><b>{self.sch['title']}</b></big>")
        titlebox_children.append(self.title)
        if "description" in self.sch.keys():
            children.append(widgets.HTML(markdown(f"{self.sch['description']}")))

        self.titlebox.children = titlebox_children
        self.ui_titlebox.children = children

    def _init_save_dialogue(self):
        if self.path is not None:
            map_save_dialogue = immutables.Map(
                save_on_edit=self.call_save_on_edit,
                save_buttonbar=self.call_save_buttonbar,
                disable_edits=self.disable_edits,
            )
            map_save_dialogue[self.config_autoui.save_controls]()
        else:
            print("self.path == None. must be a valid path to save as json")

    def call_save_buttonbar(self):
        self.save_buttonbar = SaveButtonBar(
            save=self.file, revert=self._revert, fn_onsave=self.fn_onsave,
        )
        self.ui_buttonbar.children = [self.save_buttonbar.save_buttonbar]

    def disable_edits(self):
        for k, v in self.di_widgets.items():
            try:
                v.disabled = True
            except:
                pass

    def _init_controls(self):
        [
            v.observe(functools.partial(self._watch_change, key=k), "value")
            for k, v in self.di_widgets.items()
        ]
        if self.config_autoui.show_raw:
            self.showraw.observe(self._showraw, "value")

    def _showraw(self, onchange):
        if self.showraw.value:
            self.showraw.tooltip = "show user interface"
            self.showraw.icon = "user-edit"
            out = widgets.Output()
            with out:
                display(
                    Markdown(
                        "\n```Python\n"
                        + "#  raw json data of the user input form"
                        + "\n```"
                    )
                )
                display(display_pydantic_json(self.pydantic_obj))
            self.ui_main.children = [out]
        else:
            self.showraw.tooltip = "show raw data"
            self.showraw.icon = "code"
            self.ui_main.children = [self.ui_box]

    def call_save_on_edit(self):
        self.save_on_edit = True

    def _revert(self):
        assert self.path is not None, f"self.path = {self.path}. must not be None"
        self.pydantic_obj = self.config_autoui.pydantic_model.parse_file(
            self.path
        )  # calls setter

    @classmethod
    def create_displayfile(
        cls, config_autoui: AutoUiConfig, fn_onsave: typing.Callable = lambda: None
    ):
        """
        creates a configured AutoUi callable. this is used to extend ipyautoui.DisplayFiles which
        requires a function with only a single input variable (path).

        Args:
            config_autoui (AutoUiConfig): _default = None_.
                pydantic_model: model definition
                widgets_mapper: maps ipywidgets to datatypes in the pydantic_model json schema
                save_controls: enum, handles saving to file
                ext: compound json file extension. maps type to UI reader.

        Returns:
            functools.partial(cls.parse_file, config_autoui=config_autoui) (callable function)

        Example:
            # import example
            from ipyautoui.test_schema import TestAutoLogic
            # from ipyautoui.autoui import display_template_ui_model
            # display_template_ui_model()
            # ^ view python / pydantic definition for TestAutoLogic
            # ?TestAutoLogic
            # ^ inspect TestAutoLogic

            # create AutoUi instance
            config_autoui = AutoUiConfig(pydantic_model=TestAutoLogic, ext='.aui.json')
            TestUi = AutoUi.create_displayfile(config_autoui)

            # extend DisplayFiles
            import functools
            from ipyautoui.displayfile import DisplayFiles
            def test_ui_prev(path):
                display(TestUi(path))
            config_autoui = AutoUiConfig(pydantic_model=LineGraph, ext='.lg.json')
            LineGraphUi = AutoUi.create_displayfile(config_autoui)
            user_file_renderers = {'.lg.json': line_graph_prev}
            DisplayFiles = functools.partial(DisplayFiles, user_file_renderers=user_file_renderers)
        """
        return functools.partial(
            cls.parse_file, config_autoui=config_autoui, fn_onsave=fn_onsave
        )

    @classmethod
    def create_displayfile_renderer(
        cls, config_autoui: AutoUiConfig, fn_onsave: typing.Callable = lambda: None
    ):
        renderer = cls.create_displayfile(
            config_autoui=config_autoui, fn_onsave=fn_onsave
        )
        displayfile = functools.partial(displayfile_renderer, renderer=renderer)
        return {config_autoui.ext: displayfile}

    @classmethod
    def parse_file(
        cls,
        path: pathlib.Path,
        config_autoui: AutoUiConfig = None,
        fn_onsave: typing.Callable = lambda: None,
    ):
        if config_autoui is not None:
            cls.config_autoui = config_autoui
        assert cls.config_autoui is not None, ValueError(
            "self.config_autoui must not be None"
        )
        return AutoUi(
            cls.config_autoui.pydantic_model.parse_file(path),
            config_autoui=cls.config_autoui,
            path=path,
            fn_onsave=fn_onsave,
        )

    def file(self, path: pathlib.Path = None):
        if self.path is None:
            if path is None:
                raise AssertionError(
                    f"self.path = {self.path}, path = {path}. no path given."
                )
        if self.path is not None and path is None:
            path = self.path
        ext = "".join(path.suffixes)
        assert ext == self.config_autoui.ext, ValueError(
            f"the file extension should be: {self.config_autoui.ext}, but {ext} given. "
        )
        self.pydantic_obj.file(path)

    def _watch_change(self, change, key=None):
        setattr(self._pydantic_obj, key, self.di_widgets[key].value)
        self.value = (
            self.pydantic_obj.dict()
        )  # TODO: apply like serialisation to dicts not just strings
        if self.save_on_edit:
            self.file()
        if hasattr(self, "save_buttonbar"):
            self.save_buttonbar._unsaved_changes(True)


if __name__ == "__main__":

    test_constants = load_test_constants()
    test = TestAutoLogic()

    ui = AutoUi(test)
    display(ui)
    display(Markdown("# test write to file"))
    ui.file(test_constants.PATH_TEST_AUI)
    print(
        f"test_constants.PATH_TEST_AUI.is_file() == {test_constants.PATH_TEST_AUI.is_file()} == {str(test_constants.PATH_TEST_AUI)}"
    )
    display(Markdown("# test create displayfile widget"))
    config_autoui = AutoUiConfig(pydantic_model=TestAutoLogic)
    TestAuiDisplayFile = AutoUi.create_displayfile(
        config_autoui=config_autoui, fn_onsave=lambda: print("done")
    )
    ui_file = TestAuiDisplayFile(test_constants.PATH_TEST_AUI)
    display(ui_file)

# +
# out = widgets.Output()
# box = widgets.VBox([ui])
# with out:
#     display(ui)
# out
# -


