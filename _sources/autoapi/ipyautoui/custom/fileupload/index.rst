:py:mod:`ipyautoui.custom.fileupload`
=====================================

.. py:module:: ipyautoui.custom.fileupload

.. autoapi-nested-parse::

   file upload wrapper



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.fileupload.File
   ipyautoui.custom.fileupload.FilesUploadToDir
   ipyautoui.custom.fileupload.AutoUploadPaths
   ipyautoui.custom.fileupload.Test
   ipyautoui.custom.fileupload.AutoUploadPathsValueString
   ipyautoui.custom.fileupload.Test



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.fileupload.read_file_upload_item
   ipyautoui.custom.fileupload.add_file
   ipyautoui.custom.fileupload.add_files_ipywidgets8
   ipyautoui.custom.fileupload.add_files



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.fileupload.IPYAUTOUI_ROOTDIR
   ipyautoui.custom.fileupload.IS_IPYWIDGETS8
   ipyautoui.custom.fileupload.logger
   ipyautoui.custom.fileupload.p
   ipyautoui.custom.fileupload.upld
   ipyautoui.custom.fileupload.aui


.. py:data:: IPYAUTOUI_ROOTDIR

   

.. py:data:: IS_IPYWIDGETS8

   

.. py:data:: logger

   

.. py:class:: File(**data: Any)

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


   .. py:attribute:: name
      :type: str

      

   .. py:attribute:: fdir
      :type: pathlib.Path

      

   .. py:attribute:: path
      :type: pathlib.Path

      

   .. py:method:: _path(v, values)



.. py:function:: read_file_upload_item(di: dict, fdir=pathlib.Path('.'), added_by=None)


.. py:function:: add_file(upld_item, fdir=pathlib.Path('.'))


.. py:function:: add_files_ipywidgets8(upld_value, fdir=pathlib.Path('.'))


.. py:function:: add_files(upld_value, fdir=pathlib.Path('.'))


.. py:class:: FilesUploadToDir(value=None, fdir=pathlib.Path('.'), kwargs_display_path: Optional[dict] = None, **kwargs)

   Bases: :py:obj:`ipyautoui.custom.iterable.Array`

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


   .. py:method:: _init_controls_FilesUploadToDir()


   .. py:method:: _upld(on_change)


   .. py:method:: add_files(paths: list[str])


   .. py:method:: fn_remove_file(key=None)



.. py:class:: AutoUploadPaths(schema=None, value=None, fdir=pathlib.Path('.'), kwargs_display_path: Optional[dict] = None, **kwargs)

   Bases: :py:obj:`FilesUploadToDir`

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


.. py:data:: p

   

.. py:class:: Test(**data: Any)

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

      

   .. py:attribute:: paths
      :type: list[pathlib.Path]

      


.. py:class:: AutoUploadPathsValueString(schema=None, value=None, fdir=pathlib.Path('.'), kwargs_display_path: Optional[dict] = None, **kwargs)

   Bases: :py:obj:`ipywidgets.VBox`

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


   .. py:attribute:: _value

      

   .. py:method:: _init_controls()


   .. py:method:: _update_value(on_change)



.. py:class:: Test(**data: Any)

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


   .. py:attribute:: paths
      :type: list[pathlib.Path]

      


.. py:data:: upld

   

.. py:data:: aui

   

