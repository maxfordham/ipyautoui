from ipyautoui.custom.save_buttonbar import SaveButtonBar, SaveActions, ButtonBar
from ipyautoui.constants import TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT


class TestSaveActions:
    def test_save_actions(self):
        actions = SaveActions()
        f = lambda: "test"
        f.__name__ = "fn_test"
        actions.fns_onsave_add_action(f)
        li = actions.fn_save()
        assert li[2] == "test"


class TestSaveButtonBar:
    def test_unsaved_changes_initial_state(self):
        sb = SaveButtonBar()
        assert sb.unsaved_changes == False

    def test_unsaved_changes_updates_button_style(self):
        sb = SaveButtonBar()

        # no unchanged changes
        assert sb.unsaved_changes == False
        assert sb.tgl_unsaved_changes.button_style == "success"

        # unchanged changes
        sb.unsaved_changes = True
        assert sb.tgl_unsaved_changes.button_style == "danger"

        # unchanged changes
        sb.unsaved_changes = False
        assert sb.tgl_unsaved_changes.button_style == "success"


bbar_crud = ButtonBar()


class TestButtonBar:
    def test_initial_state(self):
        assert bbar_crud.add.value == False
        assert bbar_crud.edit.value == False
        assert bbar_crud.delete.value == False

    def test_add(self):
        bbar_crud.add.value = True
        assert bbar_crud.add.layout.border == TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT
        assert bbar_crud.edit.value == bbar_crud.delete.value == False

    def test_edit(self):
        bbar_crud.edit.value = True
        assert bbar_crud.edit.layout.border == TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT
        assert bbar_crud.add.value == bbar_crud.delete.value == False

    def test_delete(self):
        bbar_crud.delete.value = True
        assert bbar_crud.delete.layout.border == TOGGLEBUTTON_ONCLICK_BORDER_LAYOUT
        assert bbar_crud.add.value == bbar_crud.edit.value == False
