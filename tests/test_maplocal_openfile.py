import pathlib
import typing as ty

# NOTE: this requires user specific configuration of the .env file to work
from maplocal import maplocal, openlocal
from maplocal.maplocal import MAPENV


class TestMAPENV:
    def test_MAPENV(self):
        assert MAPENV.MAPLOCAL_FROM == pathlib.PurePosixPath("/home")
        assert MAPENV.MAPLOCAL_TO == pathlib.PureWindowsPath(
            "//wsl.localhost/20221021/home"
        )


class TestEnv:
    # @pytest.mark.usefixtures("mock_env_user")
    def test_dev_env(self):

        assert isinstance(MAPENV.openpath, ty.Callable)
        p = pathlib.Path(__file__).resolve()
        assert maplocal(p) == pathlib.PureWindowsPath(
            "//wsl.localhost/20221021/home/jovyan/ipyautoui/tests/test_maplocal_openfile.py"
        )
        openlocal(p)
