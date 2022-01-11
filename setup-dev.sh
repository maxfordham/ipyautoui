# run line by line in shell or cmd
# assumes miniconda is installed with mamba installed in base env
mamba env create -f environment-dev.yml
conda activate ipyautoui
pip install mydocstring
pip install traitlets_paths