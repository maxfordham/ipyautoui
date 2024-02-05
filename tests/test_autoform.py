from ipyautoui.autoform import (
    demo_autoobject_form,
    AutoObjectFormLayout,
)
import ipywidgets as w

form = demo_autoobject_form()


class TestAutoObjectFormLayout:
    def test_show_raw(self):
        # check that that showraw gets added and removed on trait change
        assert form.bn_showraw.layout.display == ""
        assert form.show_raw == True
        form.show_raw = False
        assert form.bn_showraw.layout.display == "None"

    def test_show_title(self):
        # check that that title gets display and hidden on trait change
        assert form.html_title.layout.display is None
        form.show_title = False
        assert form.html_title.layout.display == "None"
        form.show_title = True
        assert form.html_title.layout.display == ""

    def test_show_description(self):
        # check that that description gets display and hidden on trait change
        assert form.html_description.layout.display is None
        form.show_description = False
        assert form.html_description.layout.display == "None"
        form.show_description = True
        assert form.html_description.layout.display == ""

    def test_show_savebuttonbar(self):
        # check that that description gets display and hidden on trait change
        assert form.savebuttonbar.layout.display is None
        form.show_savebuttonbar = False
        assert form.savebuttonbar.layout.display == "None"
        form.show_savebuttonbar = True
        assert form.savebuttonbar.layout.display == ""

def test_show_null():
    form = demo_autoobject_form()
    assert isinstance(form.bn_shownull, w.ToggleButton)
    assert form.display_bn_shownull == True
    assert form.bn_shownull.layout.display == ""
    form.display_bn_shownull = False
    assert form.bn_shownull.layout.display == "None"