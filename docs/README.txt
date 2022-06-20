To build, do the following: 

**note: we assume you are in the same dir as this README.txt file. 

1. create conda environment for docs
>>> mamba env create -f environment.yml

2. generate conf.py file from jupyterbook _config.yml
>>> jupyter-book config sphinx .

3. generate docs
>>> sphinx-build . _build/html -b html

Notes.
- when authoring notebooks that will be executed the notebook must be authored from directly within the environment - __not__ using nb_conda_kernels
- to crop the logo, run `python crop_logo.py`
