from ipyautoui.custom.edittsv import DisplayDeepDiff

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


