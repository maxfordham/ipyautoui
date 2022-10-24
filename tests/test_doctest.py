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
import os

# https://docs.pytest.org/en/7.1.x/how-to/doctest.html#how-to-run-doctests
CMD = "pytest --doctest-modules"


class TestDocTests:
    def test_automapschema(self):
        complete = subprocess.call(f"{CMD} {automapschema.__file__}", shell=True)
        assert complete == 0

    def test_autowidgets(self):
        complete = subprocess.call(f"{CMD} {autowidgets.__file__}", shell=True)
        assert complete == 0

    def test_autoipywidget(self):
        complete = subprocess.call(f"{CMD} {autoipywidget.__file__}", shell=True)
        assert complete == 0
