from ipyautoui.custom.save_buttonbar import SaveButtonBar, SaveActions


class TestSaveActions:
    def test_save_actions(self):
        actions = SaveActions()
        f = lambda: "test"
        f.__name__ = "fn_test"
        actions.fns_onsave_add_action(f)
        li = actions.fn_save()
        assert li[2] == "test"
