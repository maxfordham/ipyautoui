import logging
from copy import deepcopy

import pandas as pd
import traitlets as tr

from ipydatagrid import CellRenderer, DataGrid, TextRenderer, VegaExpr
from ipydatagrid.datagrid import SelectionHelper


class DataGrid(DataGrid):
    """extends DataGrid with useful generic functions"""

    global_decimal_places = tr.Int(default_value=None, allow_none=True)
    hide_nan = tr.Bool(default_value=False)
    count_changes = tr.Int()
    map_name_index = tr.Dict()
    transposed = tr.Bool(default_value=False)

    def __init__(self, dataframe, index_name=None, **kwargs):
        if "transposed" in kwargs:
            self.transposed = True
        super().__init__(dataframe, index_name=None, **kwargs)

    @property
    def map_index_name(self):
        return {v: k for k, v in self.map_name_index.items()}

    @tr.default("count_changes")
    def _default_count_changes(self):
        self._observe_changes()
        return 0

    @tr.observe("global_decimal_places", "hide_nan")
    def _set_text_value(self, change):
        if self.global_decimal_places is None:
            vega_expr = "cell.value"
        else:
            newfmt = f".{self.global_decimal_places}f"
            vega_expr = f"""
                if (
                    !isNumber(cell.value),
                    cell.value,
                    if (
                        round(cell.value) == cell.value,
                        cell.value,
                        format(cell.value, '{newfmt}')
                    )
                )
            """
            # ^ If not a number then return the value, else if the value is a whole number
            # then return the value, else format the value to the number of decimal places specified
        if self.hide_nan:
            vega_expr = f"""
                if(
                    !isValid(cell.value),
                    ' ',
                    {vega_expr}
                )
                """
            # ^ If the value is not valid (i.e. NaN) then return a blank space, else return the value
            # evaluated by global_decimal_place vega expression
        self.default_renderer.text_value = VegaExpr(vega_expr)

    @property
    def datagrid_schema_fields(self):
        return self._data["schema"]["fields"]

    def _observe_changes(self):
        self.on_cell_change(self._count_cell_changes)
        self.observe(self._count_data_change, "_data")

    def _count_cell_changes(self, cell):
        logging.info(
            "DataGrid Change --> {row}:{column}".format(
                row=cell["row"], column=cell["column_index"]
            )
        )
        self.count_changes += 1

    def _count_data_change(self, cell):
        self.count_changes += 1
