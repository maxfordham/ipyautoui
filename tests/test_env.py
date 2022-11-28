import os
from ipyautoui.env import Env
from .constants import DIR_REPO, DIR_TESTS


class TestEnv:
    def test_dev_env(self):
        env = Env()
        assert env.IPYAUTOUI_ROOTDIR == DIR_REPO

    def test_set_env(self):
        os.environ["IPYAUTOUI_ROOTDIR"] = str(DIR_TESTS)
        env = Env()
        assert env.IPYAUTOUI_ROOTDIR == DIR_TESTS
