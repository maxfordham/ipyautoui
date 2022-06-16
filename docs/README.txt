To build, do the following: 

**note: we assume you are in the same dir as this README.txt file. 

1. delete the ../src/__init__.py
^ this is here for dev only and makes the doc generator think that ipyautoui is a subpackage of src

2. generate conf.py file from jupyterbook
>>> jupyter-book config sphinx .

3. generate docs
>>> sphinx-build . _build/html -b html

Notes.
- when authoring notebooks that will be executed the notebook must be authored from directly within the environment - __not__ using nb_conda_kernels
- to crop the logo, run `python crop_logo.py`