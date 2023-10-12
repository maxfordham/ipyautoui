:py:mod:`ipyautoui.demo_schemas.ruleset`
========================================

.. py:module:: ipyautoui.demo_schemas.ruleset


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.ruleset.StrEnum
   ipyautoui.demo_schemas.ruleset.RuleSetType
   ipyautoui.demo_schemas.ruleset.CategoriesEnum
   ipyautoui.demo_schemas.ruleset.Rule
   ipyautoui.demo_schemas.ruleset.RuleUi
   ipyautoui.demo_schemas.ruleset.ScheduleRuleSet



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.ruleset.get_property_names
   ipyautoui.demo_schemas.ruleset.get_uniclass_product_codes
   ipyautoui.demo_schemas.ruleset.get_uniclass_system_codes
   ipyautoui.demo_schemas.ruleset.get_value_kwargs
   ipyautoui.demo_schemas.ruleset.rule_ui



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.ruleset.RevitCategoriesEnum
   ipyautoui.demo_schemas.ruleset.RevitOperatorsEnum
   ipyautoui.demo_schemas.ruleset.URL_REVIT_FILTERS
   ipyautoui.demo_schemas.ruleset.DI_UNICLASS_PR
   ipyautoui.demo_schemas.ruleset.DI_UNICLASS_SS
   ipyautoui.demo_schemas.ruleset.UniclassProducts
   ipyautoui.demo_schemas.ruleset.UniclassSystems
   ipyautoui.demo_schemas.ruleset.ScheduleRuleSet
   ipyautoui.demo_schemas.ruleset.ui


.. py:class:: StrEnum

   Bases: :py:obj:`str`, :py:obj:`enum.Enum`

   str(object='') -> str
   str(bytes_or_buffer[, encoding[, errors]]) -> str

   Create a new string object from the given object. If encoding or
   errors is specified, then the object must expose a data buffer
   that will be decoded using the given encoding and error handler.
   Otherwise, returns the result of object.__str__() (if defined)
   or repr(object).
   encoding defaults to sys.getdefaultencoding().
   errors defaults to 'strict'.


.. py:class:: RuleSetType

   Bases: :py:obj:`str`, :py:obj:`enum.Enum`

   how the rules logically multiply. Must be `AND` for schedules

   .. py:attribute:: AND
      :type: str
      :value: 'AND'

      

   .. py:attribute:: OR
      :type: str
      :value: 'OR'

      


.. py:data:: RevitCategoriesEnum

   

.. py:data:: RevitOperatorsEnum

   

.. py:class:: CategoriesEnum(root: RootModelRootType = PydanticUndefined, **data)

   Bases: :py:obj:`pydantic.RootModel`

   Usage docs: https://docs.pydantic.dev/2.4/concepts/models/#rootmodel-and-custom-root-types

   A Pydantic `BaseModel` for the root object of the model.

   :ivar root: The root object of the model.
   :ivar __pydantic_root_model__: Whether the model is a RootModel.
   :ivar __pydantic_private__: Private fields in the model.
   :ivar __pydantic_extra__: Extra fields in the model.



   .. py:attribute:: root
      :type: RevitCategoriesEnum

      


.. py:class:: Rule(**data: Any)

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


   .. py:attribute:: categories
      :type: list[CategoriesEnum]

      

   .. py:attribute:: parameter
      :type: str

      

   .. py:attribute:: operator
      :type: RevitOperatorsEnum

      

   .. py:attribute:: value
      :type: str

      

   .. py:attribute:: model_config

      


.. py:data:: URL_REVIT_FILTERS
   :value: 'https://help.autodesk.com/view/RVT/2023/ENU/?guid=GUID-400FD74B-00E0-4573-B3AC-3965E65CBBDB'

   

.. py:data:: DI_UNICLASS_PR

   

.. py:data:: DI_UNICLASS_SS

   

.. py:data:: UniclassProducts

   

.. py:data:: UniclassSystems

   

.. py:function:: get_property_names()


.. py:function:: get_uniclass_product_codes()


.. py:function:: get_uniclass_system_codes()


.. py:function:: get_value_kwargs(property_name)


.. py:class:: RuleUi(**kwargs)

   Bases: :py:obj:`ipyautoui.autoobject.AutoObject`

   creates an ipywidgets form from a json-schema or pydantic model.
   datatype must be "object"

   :ivar # AutoObjectFormLayout:
   :ivar # -------------------------:
   :ivar title: form title
   :vartype title: str
   :ivar description: form description
   :vartype description: str
   :ivar show_description: show the description. Defaults to True.
   :vartype show_description: bool, optional
   :ivar show_title: show the title. Defaults to True.
   :vartype show_title: bool, optional
   :ivar show_savebuttonbar: show the savebuttonbar. Defaults to True.
   :vartype show_savebuttonbar: bool, optional
   :ivar show_raw: show the raw json. Defaults to False.
   :vartype show_raw: bool, optional
   :ivar fn_onshowraw: do not edit
   :vartype fn_onshowraw: callable
   :ivar fn_onhideraw: do not edit
   :vartype fn_onhideraw: callable
   :ivar fns_onsave: additional functions to be called on save
   :vartype fns_onsave: callable
   :ivar fns_onrevert: additional functions to be called on revert

   :vartype fns_onrevert: callable
   :ivar # AutoObject:
   :ivar # -------------------------:
   :ivar _value: use `value` to set and get. the value of the form. this is a dict of the form {key: value}
   :vartype _value: dict
   :ivar fdir: fdir to work from. useful for widgets that link to files. Defaults to None.
   :vartype fdir: path, optional
   :ivar align_horizontal: aligns widgets horizontally. Defaults to True.
   :vartype align_horizontal: bool, optional
   :ivar nested_widgets: allows user to indicate widgets that should be show / hide type. Defaults to [].
   :vartype nested_widgets: list, optional
   :ivar order: allows user to re-specify the order for widget rows to appear by key name in self.di_widgets
   :vartype order: list
   :ivar order_can_hide_rows: allows user to hide rows by removing them from the order list.
   :vartype order_can_hide_rows: bool
   :ivar insert_rows: e.g. {3:w.Button()}. allows user to insert a widget into the rows. its presence
                      is ignored by the widget otherwise.
   :vartype insert_rows: dict
   :ivar disabled: disables all widgets. If widgets are disabled
                   using schema kwargs this is remembered when re-enabled. Defaults to False.


   :vartype disabled: bool, optional

   .. py:method:: _init_RuleUi_controls()


   .. py:method:: _update_rule_value(on_change)



.. py:function:: rule_ui(value=None, **kwargs)


.. py:data:: ScheduleRuleSet

   

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

      


.. py:data:: ui

   

