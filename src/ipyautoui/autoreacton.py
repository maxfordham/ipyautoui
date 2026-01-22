import datetime
import typing
from typing import Any, Dict, Union

import ipywidgets
import numpy as np
from numpy import ndarray

import reacton
from reacton.core import ContainerAdder, Element, _get_render_context

from reacton import ipywidgets as w
from reacton.ipywidgets import Layout
from reacton.utils import implements

import ipyautoui
from ipyautoui import autoui
from ipywidgets import *

from collections.abc import Sequence

# to execute run:
# `python -m ipyautoui.autoreacton`

if __name__ == "__main__":
    from reacton import generate

    class CodeGen(generate.CodeGen):
        def get_extra_argument(self, cls):
            return {ipywidgets.Button: [("on_click", None, typing.Callable[[], Any])]}.get(cls, [])

    current_module = __import__(__name__)

    CodeGen([autoui]).generate(__file__)

# generated code:


def _AutoBox(
    align_horizontal: bool = True,
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    description: str = None,
    hide: bool = True,
    indent: bool = False,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    nested: bool = False,
    show_description: bool = True,
    show_title: bool = True,
    tabbable: bool = None,
    title: str = None,
    tooltip: str = None,
    widget: Any = ToggleButton(value=False, layout=Layout(width="600px"), tooltip="placeholder..."),
    on_align_horizontal: typing.Callable[[bool], Any] = None,
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_hide: typing.Callable[[bool], Any] = None,
    on_indent: typing.Callable[[bool], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_nested: typing.Callable[[bool], Any] = None,
    on_show_description: typing.Callable[[bool], Any] = None,
    on_show_title: typing.Callable[[bool], Any] = None,
    on_tabbable: typing.Callable[[bool], Any] = None,
    on_title: typing.Callable[[str], Any] = None,
    on_tooltip: typing.Callable[[str], Any] = None,
    on_widget: typing.Callable[[Any], Any] = None,
) -> Element[ipyautoui.autobox.AutoBox]:
    """
    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    :param tabbable: Is widget tabbable?
    :param tooltip: A tooltip caption.
    """
    ...


@implements(_AutoBox)
def AutoBox(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = ipyautoui.autobox.AutoBox
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _AutoBox


def _EditGrid(
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    close_crud_dialogue_on_action: bool = False,
    description: str = None,
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    show_copy_dialogue: bool = False,
    show_description: bool = True,
    show_title: bool = True,
    tabbable: bool = None,
    title: str = None,
    tooltip: str = None,
    warn_on_delete: bool = False,
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_close_crud_dialogue_on_action: typing.Callable[[bool], Any] = None,
    on_description: typing.Callable[[str], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_show_copy_dialogue: typing.Callable[[bool], Any] = None,
    on_show_description: typing.Callable[[bool], Any] = None,
    on_show_title: typing.Callable[[bool], Any] = None,
    on_tabbable: typing.Callable[[bool], Any] = None,
    on_title: typing.Callable[[str], Any] = None,
    on_tooltip: typing.Callable[[str], Any] = None,
    on_warn_on_delete: typing.Callable[[bool], Any] = None,
) -> Element[ipyautoui.custom.editgrid.EditGrid]:
    """
    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    :param tabbable: Is widget tabbable?
    :param tooltip: A tooltip caption.
    """
    ...


@implements(_EditGrid)
def EditGrid(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = ipyautoui.custom.editgrid.EditGrid
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _EditGrid


def _SaveButtonBar(
    box_style: str = "",
    children: Sequence[Element[ipywidgets.Widget]] = (),
    fns_onrevert: list = [],
    fns_onsave: list = [],
    layout: Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]] = {},
    tabbable: bool = None,
    tooltip: str = None,
    unsaved_changes: bool = False,
    on_box_style: typing.Callable[[str], Any] = None,
    on_children: typing.Callable[[Sequence[Element[ipywidgets.Widget]]], Any] = None,
    on_fns_onrevert: typing.Callable[[list], Any] = None,
    on_fns_onsave: typing.Callable[[list], Any] = None,
    on_layout: typing.Callable[[Union[Dict[str, Any], Element[ipywidgets.widgets.widget_layout.Layout]]], Any] = None,
    on_tabbable: typing.Callable[[bool], Any] = None,
    on_tooltip: typing.Callable[[str], Any] = None,
    on_unsaved_changes: typing.Callable[[bool], Any] = None,
) -> Element[ipyautoui.custom.buttonbars.SaveButtonBar]:
    """
    :param box_style: Use a predefined styling for the box.
    :param children: List of widget children
    :param tabbable: Is widget tabbable?
    :param tooltip: A tooltip caption.
    """
    ...


@implements(_SaveButtonBar)
def SaveButtonBar(**kwargs):
    if isinstance(kwargs.get("layout"), dict):
        kwargs["layout"] = w.Layout(**kwargs["layout"])
    widget_cls = ipyautoui.custom.buttonbars.SaveButtonBar
    comp = reacton.core.ComponentWidget(widget=widget_cls)
    return Element(comp, kwargs=kwargs)


del _SaveButtonBar
