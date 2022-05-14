# from .constants import DIR_DOCS, PATH_TEST_AUI
# import subprocess

# PATH_AUTOUI = list(DIR_DOCS.glob("*autoui.ipynb"))[0]
# PATH_AUTOVJSF = list(DIR_DOCS.glob("*autovuetify.ipynb"))[0]
# PATH_AUTODISPLAY = list(DIR_DOCS.glob("*autodisplay.ipynb"))[0]
# li = [PATH_AUTOUI, PATH_AUTOVJSF, PATH_AUTODISPLAY]
# PATHS_OTHERS = [p for p in list(DIR_DOCS.glob("*.ipynb")) if p not in li]


# class TestDocs:
#     def test_autoui(self):
#         complete = subprocess.run(f"jupytext --execute {str(PATH_AUTOUI)}", shell=True)
#         assert complete.returncode == 0

#     def test_vuetify(self):
#         subprocess.run(f"jupytext --execute {str(PATH_AUTOVJSF)}", shell=True)

#     def test_autodisplay(self):
#         complete = subprocess.run(
#             f"jupytext --execute {str(PATH_AUTODISPLAY)}", shell=True
#         )
#         assert complete.returncode == 0

#     def test_othernotebooks(self):
#         for p in PATHS_OTHERS:
#             complete = subprocess.run(f"jupytext --execute {str(p)}", shell=True)
#             assert complete.returncode == 0

# TODO: figure out how to make this work a build time ^
