from .constants import DIR_DOCS, DIR_PACKAGE
import subprocess
from ipyautoui import (
    AutoUi,
    AutoDisplay,
    AutoVjsf,
    automapschema,
    autowidgets,
    autoipywidget,
)


class TestDocTests:
    def test_automapschema(self):
        complete = subprocess.call(
            f"python -m doctest -v {automapschema.__file__}", shell=True
        )
        assert complete == 0

    def test_autowidgets(self):
        complete = subprocess.call(
            f"python -m doctest -v {autowidgets.__file__}", shell=True
        )
        assert complete == 0

    def test_autoipywidget(self):
        complete = subprocess.call(
            f"python -m doctest -v {autoipywidget.__file__}", shell=True
        )
        assert complete == 0
