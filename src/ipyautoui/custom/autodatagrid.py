from ipydatagrid import DataGrid, TextRenderer, SelectionHelper
import traitlets as tr
import logging
from ipyautoui.automapschema import from_schema_method
import pandas as pd

logger = logging.getLogger(__name__)


class DataGrid(DataGrid):
    """extends DataGrid with useful generic functions"""

    global_decimal_places = tr.Int(default_value=None, allow_none=True)
    count_changes = tr.Int()
    fields = tr.List(default_value=None, allow_none=True)

    @property
    def map_name_title(self):
        try:
            return {f["name"]: f["title"] for f in self.fields}
        except:
            return None

    @property
    def map_title_name(self):
        try:
            return {f["title"]: f["name"] for f in self.fields}
        except:
            return None

    @tr.default("count_changes")
    def _default_count_changes(self):
        self._observe_changes()
        return 0

    @tr.observe("global_decimal_places")
    def _global_decimal_places(self, change):
        newfmt = f".{str(self.global_decimal_places)}f"
        number_cols = [
            f["name"] for f in self.datagrid_schema_fields if f["type"] == "number"
        ]
        di = {}
        for col in number_cols:
            if col in self.renderers.keys():
                if self.renderers[col].format is None:  # no overwrite format if set
                    self.renderers[col].format = newfmt
            else:
                di[col] = TextRenderer(format=newfmt)
        self.renderers = self.renderers | di

    @property
    def datagrid_schema_fields(self):
        return self._data["schema"]["fields"]

    def _observe_changes(self):
        self.on_cell_change(self._count_cell_changes)
        self.observe(self._count_data_change, "_data")

    def _count_cell_changes(self, cell):
        logger.info(
            "DataGrid Change --> {row}:{column}".format(
                row=cell["row"], column=cell["column_index"]
            )
        )
        self.count_changes += 1

    def _count_data_change(self, cell):
        self.count_changes += 1

    def get_dataframe_index(self, dataframe):
        """Returns a primary key to be used in ipydatagrid's
        view of the passed DataFrame.

        OVERRIDES get_dataframe_index in ipydatagrid. addes support for multi-index.
        TODO: add support for multi-index in ipydatagrid
        """
        # Passed index_name takes highest priority
        if self._index_name is not None:
            return self._index_name

        # Dataframe with names index used by default
        if dataframe.index.name is not None:
            return dataframe.index.name

        # as above but for multi-index
        if dataframe.index.names is not None:
            return dataframe.index.names

        # If no index_name param, nor named-index DataFrame
        # have been passed, revert to default "key"
        return "key"

    # ----------------
    # https://github.com/bloomberg/ipydatagrid/issues/340
    # selecting when a transform is applied...
    @property
    def selected_visible_cell_iterator(self):
        """
        An iterator to traverse selected cells one by one.
        """
        # Copy of the front-end data model
        view_data = self.get_visible_data()

        # Get primary key from dataframe
        index_key = self.get_dataframe_index(view_data)

        # Serielize to JSON table schema
        view_data_object = self.generate_data_object(view_data, "ipydguuid", index_key)

        return SelectionHelper(view_data_object, self.selections, self.selection_mode)

    # ----------

    @property
    def data(self):
        trimmed_primary_key = self._data["schema"]["primaryKey"][:-1]
        if self._data["data"]:
            df = pd.DataFrame(self._data["data"])
        else:
            df = pd.DataFrame(
                {value["name"]: [] for value in self._data["schema"]["fields"]}
            )
        final_df = df.set_index(trimmed_primary_key)
        final_df = final_df[final_df.columns[:-1]]
        return final_df

    @staticmethod
    def generate_data_object(dataframe, guid_key="ipydguuid", index_name="key"):
        dataframe[guid_key] = pd.RangeIndex(0, dataframe.shape[0])

        # Renaming default index name from 'index' to 'key' on
        # single index DataFrames. This allows users to use
        # 'index' as a column name. If 'key' exists, we add _x
        # suffix to id, where { x | 0 <= x < inf }
        if not isinstance(dataframe.index, pd.MultiIndex):
            if index_name in dataframe.columns:
                index = 0
                new_index_name = f"{index_name}_{index}"
                while new_index_name in dataframe.columns:
                    index += 1
                    new_index_name = f"{index_name}_{index}"
                dataframe = dataframe.rename_axis(new_index_name)
            else:
                dataframe = dataframe.rename_axis(index_name)

        schema = pd.io.json.build_table_schema(dataframe)
        reset_index_dataframe = dataframe.reset_index()
        data = reset_index_dataframe.to_dict(orient="records")

        # Check for multiple primary keys
        key = reset_index_dataframe.columns[: dataframe.index.nlevels].tolist()

        num_index_levels = len(key) if isinstance(key, list) else 1

        # Check for nested columns in schema, if so, we need to update the
        # schema to represent the actual column name values
        if isinstance(schema["fields"][-1]["name"], tuple):
            num_column_levels = len(dataframe.columns.levels)
            primary_key = key.copy()

            for i in range(num_index_levels):
                new_name = [""] * num_column_levels
                new_name[0] = schema["fields"][i]["name"]
                schema["fields"][i]["name"] = tuple(new_name)
                primary_key[i] = tuple(new_name)

            schema["primaryKey"] = primary_key
            uuid_pk = list(key[-1])
            uuid_pk[0] = guid_key
            schema["primaryKey"].append(tuple(uuid_pk))

        else:
            schema["primaryKey"] = key
            schema["primaryKey"].append(guid_key)

        schema["primaryKeyUuid"] = guid_key

        return {
            "data": data,
            "schema": schema,
            "fields": [{field["name"]: None} for field in schema["fields"]],
        }

    @data.setter
    def data(self, dataframe):
        # Reference for the original frame column and index names
        # This is used to when returning the view data model
        self.__dataframe_reference_index_names = dataframe.index.names
        self.__dataframe_reference_columns = dataframe.columns
        dataframe = dataframe.copy()

        # Primary key used
        index_key = self.get_dataframe_index(dataframe)

        self._data = self.generate_data_object(dataframe, "ipydguuid", index_key)


class AutoGrid(DataGrid):
    schema = tr.Dict(
        allow_none=True, default_value=None
    )  # TODO: deprecate / make optional...
    items = tr.Dict()
    fields = tr.List(default_value=None, allow_none=True)
    type = tr.Unicode(default_value="array")
    primary_key = tr.Unicode(default_value=None, allow_none=True)  # TODO
    min_items = tr.Int(default_value=None, allow_none=True)
    max_items = tr.Int(default_value=None, allow_none=True)
    transposed = tr.Bool(default_value=False)
    order = tr.Tuple(default_value=None, allow_none=True)

    @classmethod
    def from_schema(cls, schema, value=None):
        return from_schema_method(cls, schema, value=value)
