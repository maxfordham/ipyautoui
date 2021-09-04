"""
this is messy. think of better implementation.
"""

import pandas as pd
import logging
from constants import DF_MAP
import datetime
import pathlib
from typing import Union
import datetime

ALLOWED_VALUE_TYPES = Union[
    int,
    float,
    bool,
    str,
    tuple,
    dict,
    pd.DataFrame,
    pathlib.PurePath,
    None,
    datetime.date
]

def filter_byvalue_widgets(value, kwargs):
    
    """creates filter queries from "value" type when "options" not in kwargs"""
    
    queries = []
    if type(value) == int: 
        queries.append('value_type == "int"')
        if set(['min', 'max']).issubset(set(kwargs.keys())): # check if min, max in kwargs
            queries.append('minmax_in_kwargs == True')
            queries.append('options_in_kwargs == False')
        else:
            queries.append('minmax_in_kwargs == False')
            queries.append('options_in_kwargs == False')
    elif type(value) == float:
        queries.append('value_type == "float"')
        if set(['min', 'max']).issubset(set(kwargs.keys())): # check if min, max in kwargs
            queries.append('minmax_in_kwargs == True')
            queries.append('options_in_kwargs == False')
        else:
            queries.append('minmax_in_kwargs == False')
            queries.append('options_in_kwargs == False')
    elif type(value) == str:
        queries.append('value_type == "str"')
        if len(value) < 40:
            queries.append('string_len_is_long == False')
        else:
            queries.append('string_len_is_long == True')
    elif type(value) == tuple:
        queries.append('value_type == "tuple"')
        if type(value[0]) == int:
            queries.append('tuple_vals_are_int == True')
        else:
            queries.append('tuple_vals_are_int == False')
    elif type(value) == bool:
        queries.append('value_type == "bool"')
    elif type(value) == datetime.date:
        queries.append('value_type == "datetime.date"')  
    elif type(value) == pd.DataFrame:
        queries.append('value_type == "pd.DataFrame"')  
    elif type(value) == dict:
        try:
            pd.DataFrame.from_dict(value)
            queries.append('value_type == "pd.DataFrame"')  
        except:
            pass
    elif value is None:
        queries.append('value_type == "None"')  
    elif isinstance(value, pathlib.PurePath):
        queries.append('value_type == "pathlib.Path"')  
    else:
        AssertionError('no widgets found to match your inputs')
        
    return queries

def filter_selection_widgets(value, kwargs):
    """creates filter queries by "value" type when "options" is in kwargs"""
    queries = []
    if type(value) == tuple: 
        queries.append('value_type == "tuple"')
    elif type(value) == list:
        queries.append('value_type == "list"')
    else:
        if "ensure_option_in_kwargs" in kwargs.keys():
            queries.append('value_type != "tuple"') 
            queries.append('value_type != "list"') 
            queries.append('ensure_option_in_kwargs == True') 
        else:
            queries.append('value_type != "tuple"') 
            queries.append('value_type != "list"') 
            queries.append('ensure_option_in_kwargs == False') 
    return queries

def get_filter_query(value, kwargs):
    """create list of filter query based on value and kwargs of AutoUi"""
    queries = []
    queries.append('autoui_default == True') 
    if "options" in kwargs.keys():
        queries.append('options_in_kwargs == True')
        queries.extend(filter_selection_widgets(value, kwargs))
    else:
        queries.append('options_in_kwargs == False') 
        queries.extend(filter_byvalue_widgets(value, kwargs))
    # logging
    string = 'queries used to select widget type:'
    string += '\n'
    string += '-----------------------------------'
    for q in queries:
        string += f'\n{q}'
    logging.info(string) 
    return queries

def pd_execute_queries(df: pd.DataFrame, queries: list):
    """execute a list of queries using pd.query"""
    df_new = df
    for q in queries:
        df_new =  df_new.query(q)
    return df_new

def name_from_class_string(s):
    """return object name from class string
    
    Example:
        >>> name_from_class_string("<class 'ipywidgets.widgets.widget_int.IntSlider'>") 
        >>> "IntSlider"
    """
    return s.split('.')[-1].strip("'>")

def get_widget_class_strings(value, kwargs, df_map=DF_MAP):
    """filters queries built from evaluating the value and kwargs and 
    returns a widget_class_string from the lookup table that can be evaluated
    as a class object"""
    queries = get_filter_query(value, kwargs)
    df_tmp = pd_execute_queries(df_map, queries)
    assert len(df_tmp) == 1, 'len(df_tmp) == {} - MUST == 1'.format(len(df_tmp))
    widget_class_string = df_tmp.reset_index().loc[0, 'widget_class_string']
    return widget_class_string