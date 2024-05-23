import pathlib
import typing as ty

# NOTE: this requires user specific configuration of the .env file to work
# from maplocal import maplocal, openlocal, maplocal_openlocal_exists
# from maplocal.maplocal import MAPENV

# TODO: Fix test
# if maplocal_openlocal_exists():
#     class TestMAPENV:
#         def test_MAPENV(self):
#             assert MAPENV.MAPLOCAL_FROM == pathlib.PurePosixPath("/home")
#             assert MAPENV.MAPLOCAL_TO == pathlib.PureWindowsPath(
#                 "//wsl.localhost/Ubuntu/home"
#             )


#     class TestEnv:
#         # @pytest.mark.usefixtures("mock_env_user")
#         def test_dev_env(self):

#             assert isinstance(MAPENV.openpath, ty.Callable)
#             p = pathlib.Path(__file__).resolve()
#             assert maplocal(p) == pathlib.PureWindowsPath(
#                 "//wsl.localhost/Ubuntu/home/jovyan/ipyautoui/tests/test_maplocal_openfile.py"
#             )
#             openlocal(p)
# else:
#     pass