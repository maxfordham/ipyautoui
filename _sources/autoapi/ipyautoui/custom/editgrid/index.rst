:py:mod:`ipyautoui.custom.editgrid`
===================================

.. py:module:: ipyautoui.custom.editgrid

.. autoapi-nested-parse::

   General widget for editing data



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.editgrid.DataHandler
   ipyautoui.custom.editgrid.TestModel
   ipyautoui.custom.editgrid.RowEditor
   ipyautoui.custom.editgrid.UiDelete
   ipyautoui.custom.editgrid.UiCopy
   ipyautoui.custom.editgrid.EditGrid
   ipyautoui.custom.editgrid.TestListCol
   ipyautoui.custom.editgrid.DataFrameCols




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.editgrid.MAP_TRANSPOSED_SELECTION_MODE
   ipyautoui.custom.editgrid.delete
   ipyautoui.custom.editgrid.AUTO_GRID_DEFAULT_VALUE
   ipyautoui.custom.editgrid.datahandler


.. py:data:: MAP_TRANSPOSED_SELECTION_MODE

   

.. py:class:: DataHandler(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   CRUD operations for a for EditGrid.
   Can be used to connect to a database or other data source.
   note - the TypeHints below are hints only. The functions can be any callable.

   :param fn_get_all_data: Function to get all data.
   :type fn_get_all_data: Callable
   :param fn_post: Function to post data. is passed a dict of a single row/col to post.
                   Following the post, fn_get_all_data is called
   :type fn_post: Callable
   :param fn_patch: Function to patch data. is passed a dict of a single row/col to patch.
   :type fn_patch: Callable
   :param fn_delete: Function to delete data. is passed the index of the row/col to delete.
   :type fn_delete: callable
   :param fn_copy: Function to copy data. is passed a list of dicts with values of rows/cols to copy.
   :type fn_copy: Callable

   .. py:attribute:: fn_get_all_data
      :type: Callable

      

   .. py:attribute:: fn_post
      :type: Callable[[dict], None]

      

   .. py:attribute:: fn_patch
      :type: Callable[[Any, dict], None]

      

   .. py:attribute:: fn_delete
      :type: Callable[[list[int]], None]

      

   .. py:attribute:: fn_copy
      :type: Callable[[list[int]], None]

      


.. py:class:: TestModel(**data: Any)

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

      


.. py:class:: RowEditor

   .. py:attribute:: fn_add
      :type: List[Callable[[Any, dict], None]]

      

   .. py:attribute:: fn_edit
      :type: List[Callable[[Any, dict], None]]

      

   .. py:attribute:: fn_move
      :type: Callable

      

   .. py:attribute:: fn_copy
      :type: Callable

      

   .. py:attribute:: fn_delete
      :type: Callable

      


.. py:class:: UiDelete(fn_delete: Callable = lambda: print('delete'), **kwargs)

   Bases: :py:obj:`ipywidgets.HBox`

   Displays multiple widgets horizontally using the flexible box model.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Horizontal Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.HBox([title_widget, slider])

   .. py:property:: value_summary


   .. py:attribute:: value

      

   .. py:attribute:: columns

      

   .. py:method:: observe_value(on_change)


   .. py:method:: observe_columns(on_change)


   .. py:method:: _update_display()


   .. py:method:: _init_controls()


   .. py:method:: _bn_delete(onclick)



.. py:data:: delete

   

.. py:class:: UiCopy(fn_copy_beginning: Callable = lambda: print('duplicate selection to beginning'), fn_copy_inplace: Callable = lambda: print('duplicate selection to below current'), fn_copy_end: Callable = lambda: print('duplicate selection to end'), fn_copy_to_selection: Callable = lambda: print('select new row/col to copy to'), transposed: bool = False)

   Bases: :py:obj:`ipywidgets.HBox`

   Displays multiple widgets horizontally using the flexible box model.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Horizontal Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.HBox([title_widget, slider])

   .. py:attribute:: index

      

   .. py:method:: _init_controls()


   .. py:method:: _bn_copy(onclick)



.. py:class:: EditGrid(schema: Union[dict, Type[pydantic.BaseModel]], value: Optional[list[dict[str, Any]]] = None, by_alias: bool = False, by_title: bool = True, datahandler: Optional[DataHandler] = None, ui_add: Optional[Callable] = None, ui_edit: Optional[Callable] = None, ui_delete: Optional[Callable] = None, ui_copy: Optional[Callable] = None, warn_on_delete: bool = False, show_copy_dialogue: bool = False, close_crud_dialogue_on_action: bool = False, title: str = None, description: str = None, show_title: bool = True, **kwargs)

   Bases: :py:obj:`ipywidgets.VBox`, :py:obj:`ipyautoui.custom.title_description.TitleDescription`

   Displays multiple widgets vertically using the flexible box model.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Vertical Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.VBox([title_widget, slider])

   .. py:property:: value


   .. py:property:: transposed


   .. py:property:: schema


   .. py:property:: row_schema


   .. py:property:: model


   .. py:attribute:: _value

      

   .. py:attribute:: warn_on_delete

      

   .. py:attribute:: show_copy_dialogue

      

   .. py:attribute:: close_crud_dialogue_on_action

      

   .. py:method:: observe_warn_on_delete(on_change)


   .. py:method:: observe_show_copy_dialogue(on_change)


   .. py:method:: _update_value_from_grid()


   .. py:method:: _init_row_controls()


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: _observe_order(on_change)


   .. py:method:: _observe_selections(onchange)


   .. py:method:: _grid_changed(onchange)


   .. py:method:: _setview(onchange)


   .. py:method:: _check_one_row_selected()


   .. py:method:: _validate_edit_click()


   .. py:method:: _save_edit_to_grid()


   .. py:method:: _set_ui_edit_to_selected_row()


   .. py:method:: _patch()


   .. py:method:: _edit()


   .. py:method:: _save_add_to_grid()


   .. py:method:: _set_ui_add_to_default_row()


   .. py:method:: _post()


   .. py:method:: _add()


   .. py:method:: _get_selected_data()


   .. py:method:: _copy_selected_inplace()


   .. py:method:: _copy_selected_to_beginning()


   .. py:method:: _copy_selected_to_end()


   .. py:method:: _copy()


   .. py:method:: _reload_datahandler()


   .. py:method:: _reload_all_data()


   .. py:method:: _delete_selected()


   .. py:method:: _set_ui_delete_to_selected_row()


   .. py:method:: _delete()



.. py:data:: AUTO_GRID_DEFAULT_VALUE

   

.. py:class:: TestListCol(**data: Any)

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


   .. py:attribute:: li_col
      :type: list[str]
      :value: ['a']

      

   .. py:attribute:: stringy
      :type: str
      :value: 'as'

      

   .. py:attribute:: num
      :type: int
      :value: 1

      


.. py:data:: datahandler

   

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

      


