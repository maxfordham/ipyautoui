import shutil
import pytest

# from src.ipyautoui.test_schema import TestSchema

# from ipyautoui.tests import test_display_widget_mapping
from .constants import DIR_TESTS, DIR_FILETYPES
from .example_objects import fn_add, get_descriptions, ExampleSchema
from ipyautoui.custom import Array, Dictionary, Grid, RunName, MultiSelectSearch, SaveButtonBar, LoadProject
from ipyautoui.custom.edit_grid import BaseForm, GridWrapper, EditGrid, ButtonBar


DIR_TEST_DATA = DIR_TESTS / "test_data"
DIR_TEST_DATA.mkdir(parents=True, exist_ok=True) 
shutil.rmtree(DIR_TEST_DATA) #  remove previous data. this allows tests to check if files exist.
 

class TestCustom:
    def test_iterables_array(self):
        di_arr = {
            "items": [fn_add()],
            "fn_add": fn_add,
            "maxlen": 10,
            "show_hash": "index",
            "toggle": True,
            "title": "Array",
            "add_remove_controls": "append_only",
            "orient_rows": False,
        }
        arr = Array(**di_arr)

    def test_iterables_dict(self):
        di_arr = {
            "items": {"key": fn_add()},
            "fn_add": fn_add,
            "maxlen": 10,
            "show_hash": None,
            "toggle": True,
            "title": "Array",
            "add_remove_controls": "append_only",
            "orient_rows": True,
        }
        arr = Dictionary(**di_arr)

    def test_grid(self):
        gr = Grid()

    def test_model_run(self):
        run = RunName(value='03-lean-description', index=3)
        run.value = '06-green-thingymabob' 

    def test_multiselect_search(self):
        descriptions = get_descriptions()
        m = MultiSelectSearch(options=descriptions)

    def test_save_button_bar(self):
        save_button_bar = SaveButtonBar()

    def test_load_project(self):
        load_project = LoadProject()

    def test_button_bar(self):
        def add():
            print("ADD")

        def edit():
            print("EDIT")
            
        def copy():
            print("EDIT")

        def delete():
            print("DELETE")
            
        def backward():
            print("BACK")

        button_bar = ButtonBar(
            add=add,
            edit=edit,
            copy=copy,
            delete=delete,
            backward=backward,
        )

    def test_base_form(self):
        def save():
            print("SAVE")
        
        def revert():
            print("REVERT")
        
        # Testing with UnitsBase
        base_form = BaseForm(ExampleSchema, save=save, revert=revert)

    def test_base_form_set_value(self):
        di_eg_unit = {
            "string": "Updated value"
        }

        def save():
            print("SAVE")
        
        def revert():
            print("REVERT")
        
        # Testing with UnitsBase
        base_form = BaseForm(ExampleSchema, save=save, revert=revert)
        base_form.value = di_eg_unit

    def test_grid_wrapper(self):
        grid = GridWrapper(
            ExampleSchema,
        )

    def test_grid_wrapper_from_dict_method(self):
        # Testing class method "from_dict"
        di_eg_unit = {
            "text": "Updated value"
        }
        li_dict = [di_eg_unit for i in range(3)]
        GridWrapper.from_dict(
            pydantic_model=ExampleSchema, 
            li=li_dict,
        )

    # def test_grid_wrapper_pydantic_model_check(self): # TODO: Fix this
    #     li_incorrect_dict = [{
    #     'WRONG COLUMN': 'Test',
    #     }]
    #     exc_info = "Exception: Pydantic model fields and data fields do not match. Rejected Columns: ['WRONG COLUMN']"
    #     try:
    #         GridWrapper.from_dict(ExampleSchema, li_incorrect_dict)
    #     except Exception as e:
    #         print(f"Exception: {e}")

    #     assert e == exc_info

    def test_edit_grid(self):
        grid = EditGrid(
            pydantic_model=ExampleSchema,
        )