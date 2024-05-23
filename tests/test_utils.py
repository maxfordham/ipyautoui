import pandas as pd
import numpy as np
from ipyautoui._utils import is_null

def test_is_null():
    assert is_null(None) == True
    assert is_null(np.nan) == True
    assert is_null(0) == False
    assert is_null("None") == False
    assert is_null("NULL") == False
    assert is_null([1, 2]) == False
    assert is_null({"a": 1, "b": 2}) == False
    assert is_null(pd.Series([1, 2])) == False
    assert is_null(pd.DataFrame({"a": [1, 2]})) == False
