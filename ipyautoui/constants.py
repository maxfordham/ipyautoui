import pandas as pd
import pathlib

def make_cols_bool(df):
    """convert listed cols to bools"""
    cols = ['ensure_option_in_kwargs','options_in_kwargs','minmax_in_kwargs','autoui_default', 'string_len_is_long', 'tuple_vals_are_int']
    for col in cols:
        df[col] = df[col].fillna(0)
        df[col] = df[col].astype(bool)
    return df

def get_df_map():
    df_map = pd.read_csv(DIR_MODULE / 'autoui_mapping.csv')
    df_map = make_cols_bool(df_map)
    return df_map

DIR_MODULE = pathlib.Path(__file__).parent
DIR_TESTS = DIR_MODULE.parent / 'tests'
DF_MAP = get_df_map()
BUTTON_WIDTH_MIN = '41px'
BUTTON_WIDTH_MEDIUM = '90px'
BUTTON_HEIGHT_MIN = '25px'
ROW_WIDTH_MEDIUM = '120px'
ROW_WIDTH_MIN = '60px'

# documentinfo ------------------------------
#  update this with WebApp data
ROLES = ('Design Lead',
'Project Engineer',
'Engineer',
'Project Coordinator',
'Project Administrator',
'Building Performance Modeller')