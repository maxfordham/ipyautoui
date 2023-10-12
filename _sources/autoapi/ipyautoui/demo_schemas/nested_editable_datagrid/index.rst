:py:mod:`ipyautoui.demo_schemas.nested_editable_datagrid`
=========================================================

.. py:module:: ipyautoui.demo_schemas.nested_editable_datagrid


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.nested_editable_datagrid.DataFrameCols
   ipyautoui.demo_schemas.nested_editable_datagrid.NestedEditableGrid




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.nested_editable_datagrid.DATAGRID_TEST_VALUE


.. py:data:: DATAGRID_TEST_VALUE

   

.. py:class:: DataFrameCols(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

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

      

   .. py:attribute:: something_else
      :type: float

      


.. py:class:: NestedEditableGrid(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

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


   .. py:attribute:: title
      :type: str
      :value: 'My editable Dataframe'

      

   .. py:attribute:: reference
      :type: Optional[str]

      

   .. py:attribute:: grid
      :type: List[DataFrameCols]

      


