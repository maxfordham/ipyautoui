"""wrapper around ipydatagrid"""
import ipydatagrid as ipg
import pandas as pd
from traitlets import HasTraits, Unicode

class Grid(ipg.DataGrid, HasTraits):
    """wrapper around ipydatagrid. 
    matching the convention for ipywidgets, the "value" parameter 
    is a json string of the ipydatagrid pandas dataframe. using  
    HasTraits from the traitlets library the 
    """
    value = Unicode() # TODO: store dataframe as dict instead of string
    def __init__(self, value: pd.DataFrame=pd.read_json('{"test":{"0":0,"1":1},"df":{"0":1,"1":2}}'), **kwargs):
        """
        Args:
            value: pd.DataFrame, dataframe to display as Grid. value is updated on change of the 
                ipydatagrid and is observed by the AutoUi widget.
            kwargs: dict, ipydatagrid kwargs that are passed when it is initialized
        """
        if type(value) == str:
            value = pd.read_json(value)
        if 'editable' not in kwargs.keys():
            kwargs = kwargs | {'editable':True}
        if 'layout' not in kwargs.keys():
            kwargs = kwargs | {"height": "300px", "width": "400px"}
            
        super().__init__(value, **kwargs)
        self._set_value('change')
        self._init_controls()
        
    def _init_controls(self):
        self.on_cell_change(self._set_value)
    
    def _set_value(self, onchange):
        self.value = self.data.to_json()

if __name__ == "__main__":
    gr = Grid()
    display(gr)