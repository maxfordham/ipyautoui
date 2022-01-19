# Set formats to create notebooks
FDIR_MODULE="src/ipyautoui"
FDIR_CUSTOM="$FDIR_MODULE"/custom""

notebooks_module=( "autoui.py" "displayfile.py" ) # Array of python scripts in FDIR_MODULE
notebooks_custom=( "grid.py" "iterable.py" "modelrun.py" "multiselect_search.py" "save_button_bar.py" ) # Array of python scripts in FDIR_CUSTOM

for i in "${notebooks_module[@]}"
do
	echo "$FDIR_MODULE/$i"
	jupytext --set-formats ipynb,py "$FDIR_MODULE/$i"
done

for i in "${notebooks_custom[@]}"
do
	echo "$FDIR_CUSTOM/$i"
	jupytext --set-formats ipynb,py "$FDIR_CUSTOM/$i"
done
