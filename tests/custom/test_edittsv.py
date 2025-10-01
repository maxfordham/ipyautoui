from ipyautoui.custom.edittsv import DisplayDeepDiff
from ipyautoui.custom.edittsv import EditTsvWithDiff
from ipyautoui.demo_schemas import EditableGrid
from ipyautoui.custom.edittsv import data_to_tsv

def test_DisplayDeepDiff():
    d1 = [
        {"name": "John", "age": 30, "scores": [1, 2, 3], "address": {"city": "New York", "zip": "10001"}},
        {"name": "John", "age": 30, "scores": [1, 2, 3], "address": {"city": "New York", "zip": "10001"}}
    ]
    d2 = [
        {"name": "John", "age": 31, "scores": [1, 2, 4], "address": {"city": "Boston", "zip": "10001"}, "new": "value"},
        {"name": "John", "age": 30, "scores": [1, 2, 3], "address": {"city": "New York", "zip": "10001"}}
    ]
    ddiff = DisplayDeepDiff()
    assert ddiff.diff is None
    assert ddiff is not None

    ddiff.value = d1
    ddiff.new_value = d2

    assert ddiff.diff is not None


def get_edit_tsv_with_diff():
    AUTO_GRID_DEFAULT_VALUE = [
        {
            "string": "important string",
            "integer": 1,
            "floater": 3.14,
        },
    ]
    AUTO_GRID_DEFAULT_VALUE = AUTO_GRID_DEFAULT_VALUE * 4
    
    updatedData = [{
        "string": "important string",
        "integer": 2,
        "floater": 3.24,
    }]
    edit_tsv_with_diff = EditTsvWithDiff(value=AUTO_GRID_DEFAULT_VALUE, model=EditableGrid)
    
    return updatedData, edit_tsv_with_diff

def check_objects_initialised(edit_tsv_with_diff):
    assert edit_tsv_with_diff.ddiff is not None
    assert edit_tsv_with_diff.bn_confirmation is not None
    assert edit_tsv_with_diff.bn_cross is not None
    assert edit_tsv_with_diff.text is not None

def check_initial_editing_mode(edit_tsv_with_diff):
    assert edit_tsv_with_diff.bn_confirmation.layout.display == "None"
    assert edit_tsv_with_diff.bn_cross.layout.display == "None"
    assert edit_tsv_with_diff.ddiff.layout.display == "None"
    assert edit_tsv_with_diff.text.layout.display is None
    assert edit_tsv_with_diff.bn_upload_text.layout.display is None
    
def check_diff_mode(edit_tsv_with_diff):
    assert edit_tsv_with_diff.bn_upload_text.layout.display == "None"
    assert edit_tsv_with_diff.bn_confirmation.layout.display == ""
    assert edit_tsv_with_diff.bn_cross.layout.display == ""
    assert edit_tsv_with_diff.ddiff.layout.display == ""
    
def check_editing_mode(edit_tsv_with_diff):
    assert edit_tsv_with_diff.bn_confirmation.layout.display == "None"
    assert edit_tsv_with_diff.bn_cross.layout.display == "None"
    assert edit_tsv_with_diff.ddiff.layout.display == "None"
    assert edit_tsv_with_diff.text.layout.display == ""
    assert edit_tsv_with_diff.bn_upload_text.layout.display == ""

def test_edit_tsv_with_diff_confirmation():
    updatedData, edit_tsv_with_diff = get_edit_tsv_with_diff()
    
    assert edit_tsv_with_diff is not None
    
    check_objects_initialised(edit_tsv_with_diff)
    check_initial_editing_mode(edit_tsv_with_diff)
        
    assert edit_tsv_with_diff.value == edit_tsv_with_diff.prev_value
    
    edit_tsv_with_diff.text.value = data_to_tsv(updatedData)
    assert edit_tsv_with_diff.bn_upload_text.disabled is False
    
    edit_tsv_with_diff.bn_upload_text.click()
    check_diff_mode(edit_tsv_with_diff)
    
    assert edit_tsv_with_diff.value != edit_tsv_with_diff.prev_value

    edit_tsv_with_diff.bn_confirmation.click()
    assert edit_tsv_with_diff.value == edit_tsv_with_diff.prev_value
    
    check_editing_mode(edit_tsv_with_diff)
    
    assert edit_tsv_with_diff.bn_upload_text.disabled is True
  
    
def test_edit_tsv_with_diff_rejection():
    updatedData, edit_tsv_with_diff = get_edit_tsv_with_diff()
    
    assert edit_tsv_with_diff is not None
    
    check_objects_initialised(edit_tsv_with_diff)
    check_initial_editing_mode(edit_tsv_with_diff)
        
    assert edit_tsv_with_diff.value == edit_tsv_with_diff.prev_value
    
    edit_tsv_with_diff.text.value = data_to_tsv(updatedData)
    assert edit_tsv_with_diff.bn_upload_text.disabled is False
    
    edit_tsv_with_diff.bn_upload_text.click()
    check_diff_mode(edit_tsv_with_diff)
    
    assert edit_tsv_with_diff.value != edit_tsv_with_diff.prev_value

    edit_tsv_with_diff.bn_cross.click()
    assert edit_tsv_with_diff.value != updatedData
    
    check_editing_mode(edit_tsv_with_diff)
    
    assert edit_tsv_with_diff.bn_upload_text.disabled is True
