import pathlib

DIR_TESTS = pathlib.Path(__file__).parent
DIR_REPO = DIR_TESTS.parent
PATH_TEST_AUI = DIR_TESTS / "testdata" / "test.aui.json"  # TODO: delete
DIR_FILETYPES = DIR_TESTS / "filetypes"
DIR_DOCS = DIR_REPO / "docs"
DIR_PACKAGE = DIR_REPO / "src" / "ipyautoui"

PATH_INSTANCE_SPEC = DIR_TESTS / "instance_spec.json"
