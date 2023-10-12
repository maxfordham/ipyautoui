:py:mod:`ipyautoui.custom.autogrid`
===================================

.. py:module:: ipyautoui.custom.autogrid

.. autoapi-nested-parse::

   defines a schema for a datagrid. this is used to build the datagrid and
   contains methods for validation, coercion, and default values.

   defines AutoGrid, a datagrid generated from a jsonschema.



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.autogrid.GridSchema
   ipyautoui.custom.autogrid.DataFrameCols
   ipyautoui.custom.autogrid.DataGrid
   ipyautoui.custom.autogrid.AutoGrid
   ipyautoui.custom.autogrid.DataFrameCols
   ipyautoui.custom.autogrid.DataFrameCols
   ipyautoui.custom.autogrid.DataFrameCols
   ipyautoui.custom.autogrid.DataFrameCols
   ipyautoui.custom.autogrid.DataFrameCols
   ipyautoui.custom.autogrid.DataFrameCols



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.autogrid.get_property_types
   ipyautoui.custom.autogrid.get_default_row_data_from_schema_properties
   ipyautoui.custom.autogrid.get_column_widths_from_schema
   ipyautoui.custom.autogrid.build_renderer
   ipyautoui.custom.autogrid.get_column_renderers_from_schema
   ipyautoui.custom.autogrid.get_global_renderer_from_schema
   ipyautoui.custom.autogrid.get_global_renderers_from_schema
   ipyautoui.custom.autogrid.is_incremental



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.autogrid.MAP_TRANSPOSED_SELECTION_MODE
   ipyautoui.custom.autogrid.df


.. py:data:: MAP_TRANSPOSED_SELECTION_MODE

   

.. py:function:: get_property_types(properties)


.. py:function:: get_default_row_data_from_schema_properties(properties: dict, property_types: dict) -> Optional[dict]

   pulls default value from schema. intended for a dataframe (i.e. rows
   of known columns only). assumes all fields have a 'title' (true when using
   pydantic)

   :param properties: schema["items"]["properties"]
   :type properties: dict
   :param property_types:
   :type property_types: dict

   :returns: dictionary column values
   :rtype: dict


.. py:function:: get_column_widths_from_schema(schema, column_properties, map_name_index, **kwargs)

   Set the column widths of the data grid based on column_width given in the schema.


.. py:function:: build_renderer(var: Union[str, dict]) -> ipydatagrid.CellRenderer

   builds a renderer for datagrid. if the input is a dict, the function assumes
   the renderer to use is `ipydatagrid.TextRenderer` and initiates it with the dict.
   This is appropriate for simple renderers only. If it is a string, it assumes that
   the renderer must be built by a zero-arg callable function that is referenced by an
   object string.

   :param var: _description_
   :type var: ty.Union[str, dict]


.. py:function:: get_column_renderers_from_schema(schema, column_properties, map_name_index, **kwargs) -> dict

   when saved to schema the renderer is a PyObject callable...


.. py:function:: get_global_renderer_from_schema(schema, renderer_name, **kwargs) -> Union[None, ipydatagrid.CellRenderer]


.. py:function:: get_global_renderers_from_schema(schema, **kwargs) -> dict


.. py:function:: is_incremental(li)


.. py:class:: GridSchema(schema, get_traits=None, **kwargs)

   this is inherited by AutoDataGrid. schema attributes are therefore set on the
   base class to ensure that when they are called the traits get set.

   Notes
   -----
       - this schema is valid only for an array (i.e. integer index) of objects
           the object names are the column names and the object values are the rows
       - data has 1no name based index (multi or otherwise) and 1no. integer index
       - the methods support "transposed" data. transposed is used to flip the
           dataframe to flip the view. the schema remains the same.
       - Gridschema handles converting between the user facing column names and the
           backend column names. this is done using `map_name_index` and `map_index_name`
           "index" is used for the front-end pandas dataframe column names
           "name" is used for the back-end keys


   NOTE: index below can be either column index or row index. it can be swapped using
         transposed=True / False. the other index is always a range.

   .. py:property:: types


   .. py:property:: index_name


   .. py:property:: is_multiindex


   .. py:property:: datagrid_traits
      :type: dict[str, Any]


   .. py:property:: properties


   .. py:property:: property_keys


   .. py:property:: default_order


   .. py:property:: property_titles


   .. py:method:: set_renderers(**kwargs)


   .. py:method:: validate_editable_grid_schema()

      Check if the schema is valid for an editable grid


   .. py:method:: get_map_name_index()


   .. py:method:: get_index(order=None) -> Union[pandas.MultiIndex, pandas.Index]

      Get pandas Index based on the data passed. The data index
      must be a subset of the gridschema index.

      :param order: ordered columns
      :type order: list

      :returns: pandas index
      :rtype: Union[pd.MultiIndex, pd.Index]


   .. py:method:: _get_default_data(order=None)


   .. py:method:: _get_default_row()


   .. py:method:: get_default_dataframe(order=None, transposed=False)


   .. py:method:: get_order_titles(order)


   .. py:method:: get_field_names_from_properties(field_names: Union[str, list], order: Optional[tuple] = None) -> list[Union[tuple, str]]


   .. py:method:: coerce_data(data: pandas.DataFrame, order=None, transposed=False) -> pandas.DataFrame

      data must be passed with an integer index and columns matching the schema.
      Column names can be either the outward facing index names or the schema property keys.
      if transposed is True, the data will be transposed before getting passed to the grid

      :param data: data to coerce
      :type data: pd.DataFrame, optional

      :returns: coerced data
      :rtype: pd.DataFrame



.. py:class:: DataFrameCols(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/

   A base class for creating Pydantic models.

   :ivar __class_vars__: The names of classvars defined on the model.
   :ivar __private_attributes__: Metadata about the private attributes of the model.
   :ivar __signature__: The signature for instantiating the model.

   :ivar __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
   :ivar __pydantic_core_schema__: The pydantic-core schema used to build the SchemaValidator and SchemaSerializer.
   :ivar __pydantic_custom_init__: Whether the model has a custom `__init__` function.
   :ivar __pydantic_decorators__: Metadata containing the decorators defined on the model.
                                  This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
   :ivar __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
                                        __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
   :ivar __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
   :ivar __pydantic_post_init__: The name of the post-init method for the model, if defined.
   :ivar __pydantic_root_model__: Whether the model is a `RootModel`.
   :ivar __pydantic_serializer__: The pydantic-core SchemaSerializer used to dump instances of the model.
   :ivar __pydantic_validator__: The pydantic-core SchemaValidator used to validate instances of the model.

   :ivar __pydantic_extra__: An instance attribute with the values of extra fields from validation when
                             `model_config['extra'] == 'allow'`.
   :ivar __pydantic_fields_set__: An instance attribute with the names of fields explicitly specified during validation.
   :ivar __pydantic_private__: Instance attribute with the values of private attributes set on the model instance.


   .. py:attribute:: string
      :type: str

      

   .. py:attribute:: integer
      :type: int

      

   .. py:attribute:: floater
      :type: float

      


.. py:class:: DataGrid(dataframe, index_name=None, **kwargs)

   Bases: :py:obj:`ipydatagrid.DataGrid`

   extends DataGrid with useful generic functions

   .. py:property:: map_index_name


   .. py:property:: datagrid_schema_fields


   .. py:property:: selected_visible_cell_iterator

      An iterator to traverse selected cells one by one.

   .. py:attribute:: global_decimal_places

      

   .. py:attribute:: hide_nan

      

   .. py:attribute:: count_changes

      

   .. py:attribute:: map_name_index

      

   .. py:method:: _default_count_changes()


   .. py:method:: _set_text_value(change)


   .. py:method:: _observe_changes()


   .. py:method:: _count_cell_changes(cell)


   .. py:method:: _count_data_change(cell)


   .. py:method:: get_dataframe_index(dataframe)

      Returns a primary key to be used in ipydatagrid's
      view of the passed DataFrame.

      OVERRIDES get_dataframe_index in ipydatagrid. addes support for multi-index.
      TODO: add support for multi-index in ipydatagrid



.. py:class:: AutoGrid(schema: Union[dict, Type[pydantic.BaseModel]], data: Optional[pandas.DataFrame] = None, by_alias: bool = False, by_title: bool = True, order: Optional[tuple] = None, **kwargs)

   Bases: :py:obj:`DataGrid`

   a thin wrapper around DataGrid that makes makes it possible to initiate the
   grid from a json-schema / pydantic model.

   Traits that can be set in a DataGrid instance can be reviewed using gr.traits().
   Note that of these traits, `column_widths` and `renderers` have the format
   {'column_name': <setting>}.

   NOTE:
   - Currently only supports a range index (or transposed therefore range columns)


   .. py:property:: is_transposed


   .. py:property:: default_row


   .. py:property:: default_row_title_keys


   .. py:property:: datagrid_trait_names


   .. py:property:: properties


   .. py:property:: map_name_index


   .. py:property:: map_index_name


   .. py:property:: index_names


   .. py:property:: column_names


   .. py:property:: selected


   .. py:property:: selected_items


   .. py:property:: selected_index


   .. py:property:: selected_indexes


   .. py:property:: selected_row

      Get the data selected in the table which is returned as a dataframe.

   .. py:property:: selected_rows

      Get the data selected in the table which is returned as a dataframe.

   .. py:property:: selected_col

      Get the data selected in the table which is returned as a dataframe.

   .. py:property:: selected_cols

      Get the data selected in the table which is returned as a dataframe.

   .. py:property:: selected_row_index
      :type: Any


   .. py:property:: selected_row_indexes

      Return the indexes of the selected rows. still works if transform applied.

   .. py:property:: selected_col_index

      returns the first.

   .. py:property:: selected_col_indexes

      Return the indexes of the selected rows. still works if transform applied.

   .. py:property:: selected_dict

      Return the dictionary of selected rows where index is row index. still works if transform applied.

   .. py:attribute:: schema

      

   .. py:attribute:: transposed

      

   .. py:attribute:: order

      

   .. py:attribute:: datagrid_index_name

      

   .. py:method:: _update_from_schema(change)


   .. py:method:: _valid_schema(proposal)


   .. py:method:: _observe_order(change)


   .. py:method:: _transposed(change)


   .. py:method:: records(keys_as_title=False)


   .. py:method:: get_col_name_from_index(index)


   .. py:method:: get_default_data()


   .. py:method:: _init_data(data) -> pandas.DataFrame


   .. py:method:: set_cell_value_if_different(column_name, primary_key_value, new_value)


   .. py:method:: set_item_value(index: int, value: dict)

      set row (transposed==False) or col (transposed==True) value


   .. py:method:: _check_indexes(value: dict)

      Check whether indexes of value are a subset of the schema

      :param value: The data we want to input into the row.
      :type value: dict


   .. py:method:: set_row_value(index: int, value: dict)

      Set a chosen row using the index and a value given.

      :param index: The key of the row. # TODO: is this defo an int?
      :type index: int
      :param value: The data we want to input into the row.
      :type value: dict


   .. py:method:: apply_map_name_title(row_data)


   .. py:method:: set_col_value(index: int, value: dict)

      Set a chosen col using the index and a value given.

      Note: We do not call value setter to apply values as it resets the datagrid.

      :param index: The index of the col
      :type index: int
      :param value: The data we want to input into the col.
      :type value: dict


   .. py:method:: filter_by_column_name(column_name: str, li_filter: list)

      Filter rows to display based on a column name and a list of objects belonging to that column.

      :param column_name: column name we want to apply the transform to.
      :type column_name: str
      :param li_filter: Values within the column we want to display in the grid.
      :type li_filter: list


   .. py:method:: map_value_keys_index_name(value: dict) -> dict

      Checks if the keys of the dictionary are using the original field
      names and, if not, returns a new dict using the original field names.

      :param value: dictionary (potentially) using index names
      :type value: dict

      :returns: New dictionary of same values but using original field names
      :rtype: dict


   .. py:method:: _swap_indexes(index_a: int, index_b: int)

      Swap two indexes by giving their indexes.

      :param index_a: index of a index.
      :type index_a: int
      :param index_b: index of another index.
      :type index_b: int


   .. py:method:: _move_index_down(index: int)

      Move an index down numerically e.g. 1 -> 0

      :param index: index of the index
      :type index: int


   .. py:method:: _move_index_up(index: int)

      Move an index up numerically e.g. 1 -> 2.

      :param index: index of the index
      :type index: int


   .. py:method:: _move_indexes_up(li_indexes: List[int])

      Move multiple indexes up numerically.

      :param li_indexes: ty.List of index indexes.
      :type li_indexes: ty.List[int]


   .. py:method:: _move_indexes_down(li_indexes: List[int])

      Move multiple indexes down numerically.

      :param li_indexes: ty.List of index indexes.
      :type li_indexes: ty.List[int]



.. py:class:: DataFrameCols(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/

   A base class for creating Pydantic models.

   :ivar __class_vars__: The names of classvars defined on the model.
   :ivar __private_attributes__: Metadata about the private attributes of the model.
   :ivar __signature__: The signature for instantiating the model.

   :ivar __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
   :ivar __pydantic_core_schema__: The pydantic-core schema used to build the SchemaValidator and SchemaSerializer.
   :ivar __pydantic_custom_init__: Whether the model has a custom `__init__` function.
   :ivar __pydantic_decorators__: Metadata containing the decorators defined on the model.
                                  This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
   :ivar __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
                                        __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
   :ivar __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
   :ivar __pydantic_post_init__: The name of the post-init method for the model, if defined.
   :ivar __pydantic_root_model__: Whether the model is a `RootModel`.
   :ivar __pydantic_serializer__: The pydantic-core SchemaSerializer used to dump instances of the model.
   :ivar __pydantic_validator__: The pydantic-core SchemaValidator used to validate instances of the model.

   :ivar __pydantic_extra__: An instance attribute with the values of extra fields from validation when
                             `model_config['extra'] == 'allow'`.
   :ivar __pydantic_fields_set__: An instance attribute with the names of fields explicitly specified during validation.
   :ivar __pydantic_private__: Instance attribute with the values of private attributes set on the model instance.


   .. py:attribute:: string
      :type: str

      

   .. py:attribute:: integer
      :type: int

      

   .. py:attribute:: floater
      :type: float

      


.. py:class:: DataFrameCols(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/

   A base class for creating Pydantic models.

   :ivar __class_vars__: The names of classvars defined on the model.
   :ivar __private_attributes__: Metadata about the private attributes of the model.
   :ivar __signature__: The signature for instantiating the model.

   :ivar __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
   :ivar __pydantic_core_schema__: The pydantic-core schema used to build the SchemaValidator and SchemaSerializer.
   :ivar __pydantic_custom_init__: Whether the model has a custom `__init__` function.
   :ivar __pydantic_decorators__: Metadata containing the decorators defined on the model.
                                  This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
   :ivar __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
                                        __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
   :ivar __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
   :ivar __pydantic_post_init__: The name of the post-init method for the model, if defined.
   :ivar __pydantic_root_model__: Whether the model is a `RootModel`.
   :ivar __pydantic_serializer__: The pydantic-core SchemaSerializer used to dump instances of the model.
   :ivar __pydantic_validator__: The pydantic-core SchemaValidator used to validate instances of the model.

   :ivar __pydantic_extra__: An instance attribute with the values of extra fields from validation when
                             `model_config['extra'] == 'allow'`.
   :ivar __pydantic_fields_set__: An instance attribute with the names of fields explicitly specified during validation.
   :ivar __pydantic_private__: Instance attribute with the values of private attributes set on the model instance.


   .. py:attribute:: string
      :type: str

      

   .. py:attribute:: integer
      :type: int

      

   .. py:attribute:: floater
      :type: float

      


.. py:class:: DataFrameCols(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/

   A base class for creating Pydantic models.

   :ivar __class_vars__: The names of classvars defined on the model.
   :ivar __private_attributes__: Metadata about the private attributes of the model.
   :ivar __signature__: The signature for instantiating the model.

   :ivar __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
   :ivar __pydantic_core_schema__: The pydantic-core schema used to build the SchemaValidator and SchemaSerializer.
   :ivar __pydantic_custom_init__: Whether the model has a custom `__init__` function.
   :ivar __pydantic_decorators__: Metadata containing the decorators defined on the model.
                                  This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
   :ivar __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
                                        __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
   :ivar __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
   :ivar __pydantic_post_init__: The name of the post-init method for the model, if defined.
   :ivar __pydantic_root_model__: Whether the model is a `RootModel`.
   :ivar __pydantic_serializer__: The pydantic-core SchemaSerializer used to dump instances of the model.
   :ivar __pydantic_validator__: The pydantic-core SchemaValidator used to validate instances of the model.

   :ivar __pydantic_extra__: An instance attribute with the values of extra fields from validation when
                             `model_config['extra'] == 'allow'`.
   :ivar __pydantic_fields_set__: An instance attribute with the names of fields explicitly specified during validation.
   :ivar __pydantic_private__: Instance attribute with the values of private attributes set on the model instance.


   .. py:attribute:: string
      :type: str

      

   .. py:attribute:: integer
      :type: int

      

   .. py:attribute:: floater
      :type: float

      


.. py:class:: DataFrameCols(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/

   A base class for creating Pydantic models.

   :ivar __class_vars__: The names of classvars defined on the model.
   :ivar __private_attributes__: Metadata about the private attributes of the model.
   :ivar __signature__: The signature for instantiating the model.

   :ivar __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
   :ivar __pydantic_core_schema__: The pydantic-core schema used to build the SchemaValidator and SchemaSerializer.
   :ivar __pydantic_custom_init__: Whether the model has a custom `__init__` function.
   :ivar __pydantic_decorators__: Metadata containing the decorators defined on the model.
                                  This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
   :ivar __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
                                        __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
   :ivar __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
   :ivar __pydantic_post_init__: The name of the post-init method for the model, if defined.
   :ivar __pydantic_root_model__: Whether the model is a `RootModel`.
   :ivar __pydantic_serializer__: The pydantic-core SchemaSerializer used to dump instances of the model.
   :ivar __pydantic_validator__: The pydantic-core SchemaValidator used to validate instances of the model.

   :ivar __pydantic_extra__: An instance attribute with the values of extra fields from validation when
                             `model_config['extra'] == 'allow'`.
   :ivar __pydantic_fields_set__: An instance attribute with the names of fields explicitly specified during validation.
   :ivar __pydantic_private__: Instance attribute with the values of private attributes set on the model instance.


   .. py:attribute:: string
      :type: str

      

   .. py:attribute:: integer
      :type: int

      

   .. py:attribute:: floater
      :type: float

      


.. py:data:: df

   

.. py:class:: DataFrameCols(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/

   A base class for creating Pydantic models.

   :ivar __class_vars__: The names of classvars defined on the model.
   :ivar __private_attributes__: Metadata about the private attributes of the model.
   :ivar __signature__: The signature for instantiating the model.

   :ivar __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
   :ivar __pydantic_core_schema__: The pydantic-core schema used to build the SchemaValidator and SchemaSerializer.
   :ivar __pydantic_custom_init__: Whether the model has a custom `__init__` function.
   :ivar __pydantic_decorators__: Metadata containing the decorators defined on the model.
                                  This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
   :ivar __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
                                        __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
   :ivar __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
   :ivar __pydantic_post_init__: The name of the post-init method for the model, if defined.
   :ivar __pydantic_root_model__: Whether the model is a `RootModel`.
   :ivar __pydantic_serializer__: The pydantic-core SchemaSerializer used to dump instances of the model.
   :ivar __pydantic_validator__: The pydantic-core SchemaValidator used to validate instances of the model.

   :ivar __pydantic_extra__: An instance attribute with the values of extra fields from validation when
                             `model_config['extra'] == 'allow'`.
   :ivar __pydantic_fields_set__: An instance attribute with the names of fields explicitly specified during validation.
   :ivar __pydantic_private__: Instance attribute with the values of private attributes set on the model instance.


   .. py:attribute:: string
      :type: str

      

   .. py:attribute:: integer
      :type: int

      

   .. py:attribute:: floater
      :type: float

      


.. py:class:: DataFrameCols(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/

   A base class for creating Pydantic models.

   :ivar __class_vars__: The names of classvars defined on the model.
   :ivar __private_attributes__: Metadata about the private attributes of the model.
   :ivar __signature__: The signature for instantiating the model.

   :ivar __pydantic_complete__: Whether model building is completed, or if there are still undefined fields.
   :ivar __pydantic_core_schema__: The pydantic-core schema used to build the SchemaValidator and SchemaSerializer.
   :ivar __pydantic_custom_init__: Whether the model has a custom `__init__` function.
   :ivar __pydantic_decorators__: Metadata containing the decorators defined on the model.
                                  This replaces `Model.__validators__` and `Model.__root_validators__` from Pydantic V1.
   :ivar __pydantic_generic_metadata__: Metadata for generic models; contains data used for a similar purpose to
                                        __args__, __origin__, __parameters__ in typing-module generics. May eventually be replaced by these.
   :ivar __pydantic_parent_namespace__: Parent namespace of the model, used for automatic rebuilding of models.
   :ivar __pydantic_post_init__: The name of the post-init method for the model, if defined.
   :ivar __pydantic_root_model__: Whether the model is a `RootModel`.
   :ivar __pydantic_serializer__: The pydantic-core SchemaSerializer used to dump instances of the model.
   :ivar __pydantic_validator__: The pydantic-core SchemaValidator used to validate instances of the model.

   :ivar __pydantic_extra__: An instance attribute with the values of extra fields from validation when
                             `model_config['extra'] == 'allow'`.
   :ivar __pydantic_fields_set__: An instance attribute with the names of fields explicitly specified during validation.
   :ivar __pydantic_private__: Instance attribute with the values of private attributes set on the model instance.


   .. py:attribute:: floater
      :type: float

      

   .. py:attribute:: inty
      :type: int

      

   .. py:attribute:: stringy
      :type: str

      


