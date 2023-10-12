:py:mod:`ipyautoui.demo_schemas`
================================

.. py:module:: ipyautoui.demo_schemas


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   array_examples/index.rst
   array_object_dataframe/index.rst
   complex_serialization/index.rst
   core_ipywidgets/index.rst
   editable_datagrid/index.rst
   nested/index.rst
   nested_editable_datagrid/index.rst
   null_and_required/index.rst
   nullable_core_ipywidgets/index.rst
   override_ipywidgets/index.rst
   recursive_array/index.rst
   recursive_object/index.rst
   root_array/index.rst
   root_array_enum/index.rst
   root_enum/index.rst
   root_simple/index.rst
   ruleset/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.CoreIpywidgets
   ipyautoui.demo_schemas.OverrideIpywidgets
   ipyautoui.demo_schemas.ComplexSerialisation
   ipyautoui.demo_schemas.Nested
   ipyautoui.demo_schemas.EditableGrid
   ipyautoui.demo_schemas.NestedEditableGrid
   ipyautoui.demo_schemas.RootArray
   ipyautoui.demo_schemas.RootSimple
   ipyautoui.demo_schemas.RootEnum
   ipyautoui.demo_schemas.RootArrayEnum
   ipyautoui.demo_schemas.ArrayObjectDataframe
   ipyautoui.demo_schemas.ArrayWithUnionType
   ipyautoui.demo_schemas.RecursiveArray
   ipyautoui.demo_schemas.RecursiveObject
   ipyautoui.demo_schemas.ScheduleRuleSet




.. py:class:: CoreIpywidgets(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   this is a test UI form to demonstrate how pydantic class can  be used to generate an ipywidget input form.
   only simple datatypes used (i.e. not lists/arrays or objects)

   .. py:attribute:: int_slider_req
      :type: typing_extensions.Annotated[int, Field(ge=1, le=3)]

      

   .. py:attribute:: int_slider_nullable
      :type: Optional[typing_extensions.Annotated[int, Field(ge=1, le=3)]]

      

   .. py:attribute:: int_slider
      :type: typing_extensions.Annotated[int, Field(ge=1, le=3)]
      :value: 2

      

   .. py:attribute:: int_text_req
      :type: int

      

   .. py:attribute:: int_text_nullable
      :type: Optional[int]

      

   .. py:attribute:: int_range_slider
      :type: tuple[conint(ge=0, le=4), conint(ge=0, le=4)]

      

   .. py:attribute:: int_range_slider_disabled
      :type: tuple[conint(ge=0, le=4), conint(ge=0, le=4)]

      

   .. py:attribute:: float_slider
      :type: float

      

   .. py:attribute:: float_text
      :type: float
      :value: 2.2

      

   .. py:attribute:: float_text_locked
      :type: float

      

   .. py:attribute:: float_range_slider
      :type: tuple[confloat(ge=0, le=4), confloat(ge=0, le=4)]

      

   .. py:attribute:: checkbox
      :type: bool

      

   .. py:attribute:: dropdown
      :type: Optional[FruitEnum]

      

   .. py:attribute:: dropdown_int
      :type: Number

      

   .. py:attribute:: dropdown_int_optional
      :type: Optional[Number]

      

   .. py:attribute:: combobox
      :type: str

      

   .. py:attribute:: combobox1
      :type: Union[str, FruitEnum]

      

   .. py:attribute:: dropdown_edge_case
      :type: FruitEnum

      

   .. py:attribute:: dropdown_simple
      :type: str

      

   .. py:attribute:: text
      :type: str

      

   .. py:attribute:: text_short
      :type: typing_extensions.Annotated[str, StringConstraints(min_length=0, max_length=20)]
      :value: 'short text'

      

   .. py:attribute:: textarea
      :type: typing_extensions.Annotated[str, StringConstraints(min_length=0, max_length=800)]

      

   .. py:attribute:: model_config

      


.. py:class:: OverrideIpywidgets(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   sometimes it isn't possible to guess what widget to use based on type information.
   For example, the Combobox has the same inputs as a Dropdown. You can specify to use
   a specify widget using the `autoui` field.

   .. py:attribute:: combobox
      :type: str

      

   .. py:attribute:: toggle
      :type: bool

      


.. py:class:: ComplexSerialisation(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   all of these types need to be serialised to json and parsed back to objects upon reading...

   .. py:attribute:: file_chooser
      :type: pathlib.Path

      

   .. py:attribute:: date_picker_string
      :type: Optional[datetime.date]

      

   .. py:attribute:: naive_datetime_picker_string
      :type: Optional[datetime.datetime]

      

   .. py:attribute:: color_picker_ipywidgets
      :type: pydantic_extra_types.color.Color
      :value: '#f5f595'

      

   .. py:attribute:: markdown_widget
      :type: str

      

   .. py:attribute:: any_of
      :type: Union[conint(ge=0, le=3), str]

      


.. py:class:: Nested(**data: Any)

   Bases: :py:obj:`ipyautoui.basemodel.BaseModel`

   demonstrates nested objects

   .. py:attribute:: nested
      :type: NestedObject

      

   .. py:attribute:: recursive_nest
      :type: RecursiveNest

      

   .. py:attribute:: array_simple
      :type: list[str]

      

   .. py:attribute:: array_objects
      :type: list[NestedObject]

      

   .. py:attribute:: nullable_list
      :type: list[str]

      

   .. py:attribute:: nullable_object
      :type: NestedObject

      


.. py:class:: EditableGrid(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: List[DataFrameCols]

      

   .. py:attribute:: model_config

      


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

      


.. py:class:: RootArray(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: list[NestedObject]

      


.. py:class:: RootSimple(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: conint(ge=0, le=3)
      :value: 2

      


.. py:class:: RootEnum(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: list[UniclassProducts]

      

   .. py:attribute:: model_config

      


.. py:class:: RootArrayEnum(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: list[UniclassProductsUi]

      


.. py:class:: ArrayObjectDataframe(**data: Any)

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


   .. py:attribute:: auto_array
      :type: list[str]

      

   .. py:attribute:: auto_object
      :type: NestedObject

      

   .. py:attribute:: edit_grid
      :type: list[NestedObject]

      


.. py:class:: ArrayWithUnionType(**data: Any)

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


   .. py:attribute:: auto_simple
      :type: list[str]

      

   .. py:attribute:: auto_custom_str
      :type: list[MyString]

      

   .. py:attribute:: auto_object
      :type: list[NestedObject]

      

   .. py:attribute:: auto_anyof
      :type: list[Union[NestedObject, str]]

      


.. py:class:: RecursiveArray(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   a recursive array

   .. py:attribute:: root
      :type: list[Union[RecursiveArray, MyObject]]

      


.. py:class:: RecursiveObject(**data: Any)

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


   .. py:attribute:: op_type
      :type: RuleSetType

      

   .. py:attribute:: obj_set
      :type: list[Union[Obj, RecursiveObject]]

      


.. py:class:: ScheduleRuleSet(**data: Any)

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


   .. py:attribute:: set_type
      :type: RuleSetType

      

   .. py:attribute:: rule_sets
      :type: List[Union[Rule, ScheduleRuleSet]]

      

   .. py:attribute:: model_config

      


