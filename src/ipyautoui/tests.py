# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.12.0
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
# %run __init__.py

import datetime
import pandas as pd
import pathlib
import ipywidgets as widgets
from markdown import markdown
from IPython.display import display, Markdown

from ipyautoui.constants import DF_MAP
from ipyautoui.autoui import AutoUi, AutoUiBase, WidgetRow, WidgetRowBase, _markdown
from ipyautoui._utils import obj_from_string
from ipyautoui._auto_logic import *

from ipyautoui._custom_widgets import AutoUiFileChooser, AutoUiFileUpload, AutoUiDataGrid, AutoModelRunName
from ipyautoui.test_autoui_data import di_test_autologic

# TESTING #-----------------------------------------------------
#---------------------------------------------------------------

def test_mapping(di_test_autologic, df_map=DF_MAP):
    for k, v in di_test_autologic.items():
        if 'autoui_type' not in v:
            queries = get_filter_query(**v)
            df_tmp = pd_execute_queries(df_map, queries)
            assert len(df_tmp) == 1, '{} --> len(df_tmp) == {}'.format(k, len(df_tmp))
            widget_class_string = df_tmp.reset_index().loc[0, 'widget_class_string']
        else:
            widget_class_string = v['autoui_type']
        widget_name = name_from_class_string(widget_class_string)
        assert k in widget_name, f'{k} != {widget_name}'
    
def test_display_widget_mapping(di_test_autologic, df_map=DF_MAP):
    li = []
    for k, v in di_test_autologic.items():
        data = WidgetRowBase(**v)
        ui = WidgetRow(data)
        assert str(type(ui.widget)) == data.autoui_type, 'WidgetRow not initalised'

def test_display_WidgetRow_widget(di_test_autologic, df_map=DF_MAP):
    li = []
    for k, v in di_test_autologic.items():
        data = WidgetRowBase(**v)
        ui = WidgetRow(data)
        assert str(type(ui.widget)) == data.autoui_type, 'WidgetRow not initalised'
        if 'ipywidget' in str(type(ui.widget)):
            label = f'<b>{k}</b>'
        else:
            label = f'<p style="color:blue"><b>{k}</b></p>'
        try:
            display(widgets.HBox([widgets.HTML(label, layout={'width':'200px'}),ui.row]))
        except:
            AssertionError('widget not formed for class string: {}'.format(ui.autoui_type))
            
def test_display_AutoUi(di_test_autologic, df_map=DF_MAP):
    rows = []
    for k, v in di_test_autologic.items():
        tmp = v
        tmp['name'] = k
        
        rows.append(tmp)
    data = AutoUiBase(**{'rows':rows})
    ui = AutoUi(data)
    return ui

if __name__ == "__main__":
    test_display_WidgetRow_widget(di_test_autologic)
    ui=test_display_AutoUi(di_test_autologic)
    display(ui)
    #---------------------------------------------------------------
    # -

