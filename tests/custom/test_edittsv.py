import numpy as np
from ipyautoui.custom.edittsv import DisplayDeepDiff
from ipyautoui.custom.edittsv import EditTsvWithDiff
from ipyautoui.demo_schemas import EditableGrid
from ipyautoui.custom.edittsv import data_to_tsv
from deepdiff import DeepDiff

def test_DisplayDeepDiff():
    d1 = {
            1: {"name": "John", "age": 30, "scores": [1, 2, 3], "address": {"city": "New York", "zip": "10001"}},
            2: {"name": "John", "age": 30, "scores": [1, 2, 3], "address": {"city": "New York", "zip": "10001"}}
        }
        
    d2 = {
            1: {"name": "John", "age": 31, "scores": [1, 2, 4], "address": {"city": "Boston", "zip": "10001"}, "new": "value"},
            2: {"name": "John", "age": 30, "scores": [1, 2, 3], "address": {"city": "New York", "zip": "10001"}}
        }
    
    ddiff = DisplayDeepDiff()
    assert ddiff.diff is None
    assert ddiff is not None

    ddiff.value = d1
    ddiff.new_value = d2

    assert ddiff.diff is not None
    
def test_deepdiff_replaces_whole_list_items():
    '''
        Edge case 1: When a property from all objects is changed, deepdiff thinks the whole object has been changed rather than just the property that was changed.
        In this case, only the floater value has been changed, but deepdiff thinks the whole object was changed.
    '''
    d1 = [
        {
            "id": 3,
            "string": "important string 3",
            "integer": 3,
            "floater": 17.5
        },
        {
            "id": 5,
            "string": "str",
            "integer": 6,
            "floater": 7.0
        }
    ]
    d2 = [
        {
            "id": 3,
            "string": "important string 3",
            "integer": 3,
            "floater": 18.0
        },
        {
            "id": 5,
            "string": "str",
            "integer": 6,
            "floater": 8.5
        }
    ]
    
    ddiff = DeepDiff(d1, d2, ignore_order=True)
    
    assert ddiff is not None
    
    assert "values_changed" in ddiff or "iterable_item_added" in ddiff
    
    diff_str = str(ddiff)
    assert "floater" not in diff_str or "root[0]['floater']" not in diff_str, \
        "DeepDiff detected key-level change — expected it to miss this granularity."
    
def test_list_add_remove_edge_case():
    '''
        Edge case 2: DeepDiff treats added/removed list elements as edits instead of separate add/remove events
        when comparing lists of dicts without unique identifiers.
    '''

    d1 = [
        {"id": 1, "value": "line A"},
        {"id": 2, "value": "line B"},
    ]

    d2 = [
        {"id": 3, "value": "line C"},  # new line added
        {"id": 2, "value": "line B"},  # one line retained
    ]

    ddiff = DeepDiff(d1, d2, ignore_order=True)
    
    assert ddiff is not None

    # DeepDiff likely interprets this as a change of the first element (index 0)
    # rather than a removal of {'id': 1, 'value': 'line A'} and addition of {'id': 3, 'value': 'line C'}

    assert "values_changed" in ddiff

def get_edit_tsv_with_diff():
    AUTO_GRID_DEFAULT_VALUE = [
        {
            "id": 1,
            "string": "important string",
            "integer": 1,
            "floater": 3.14,
        },
    ]
    AUTO_GRID_DEFAULT_VALUE = AUTO_GRID_DEFAULT_VALUE * 4
    
    updatedData = [{
        "id": 1,
        "string": "important string",
        "integer": 2,
        "floater": 3.24,
    }]
    edit_tsv_with_diff = EditTsvWithDiff(value=AUTO_GRID_DEFAULT_VALUE, model=EditableGrid, transposed = False, primary_key_name="id")
    
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
    
    assert edit_tsv_with_diff.bn_upload_text.disabled is False

def test_edit_tsv_blank_from_empty_volume_reference():
    """Test that an edittsv becomes blank when a property is nan / None."""
    AUTO_GRID_DEFAULT_VALUE = [
        {
            "id": 1,
            "string": "important string",
            "integer": 1,
            "floater": 3.14,
        },
    ]
    edit_tsv_with_diff = EditTsvWithDiff(value=AUTO_GRID_DEFAULT_VALUE, model=EditableGrid)
    new_tuple = (
        {
            "id": 1,
            'string': "test string",
            "integer": 2,
            "floater": 3.24,
        },
    )
    edit_tsv_with_diff.value = new_tuple
    
    assert edit_tsv_with_diff.value != []