#  note. commands below intended to be run line-by-line rather than as a script
#        this is to be used when building locally.
conda build conda.recipe
cp /home/jovyan/miniconda3/envs/mf_base/conda-bld/linux-64/ipyautoui-0.2.4*.tar.bz2 /mnt/conda-bld/linux-64
conda convert --platform all /mnt/conda-bld/linux-64/ipyautoui-0.2.4*.tar.bz2 --output-dir /mnt/conda-bld
conda index /mnt/conda-bld