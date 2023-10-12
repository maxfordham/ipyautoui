:py:mod:`ipyautoui.custom.selectdir`
====================================

.. py:module:: ipyautoui.custom.selectdir


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.selectdir.Usage
   ipyautoui.custom.selectdir.SelectDirBase
   ipyautoui.custom.selectdir.SelectDir
   ipyautoui.custom.selectdir.SelectDirUi



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.selectdir.get_projects
   ipyautoui.custom.selectdir.record_load
   ipyautoui.custom.selectdir.print_fdir



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.selectdir.NAME
   ipyautoui.custom.selectdir.FDIR_PROJECTS_ROOT
   ipyautoui.custom.selectdir.FDIR_LOG_DIRS
   ipyautoui.custom.selectdir.FPTH_WORKING_DIRS
   ipyautoui.custom.selectdir.c1_str_exists


.. py:data:: NAME

   

.. py:data:: FDIR_PROJECTS_ROOT

   

.. py:data:: FDIR_LOG_DIRS

   

.. py:data:: FPTH_WORKING_DIRS

   

.. py:class:: Usage(**data: Any)

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


   .. py:attribute:: user
      :type: str

      

   .. py:attribute:: timestamp
      :type: datetime.datetime

      


.. py:class:: SelectDirBase(**data: Any)

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


   .. py:attribute:: fdir_root
      :type: pathlib.Path

      

   .. py:attribute:: fdir_log
      :type: pathlib.Path

      

   .. py:attribute:: tags
      :type: list

      

   .. py:attribute:: key
      :type: str

      

   .. py:attribute:: fdir
      :type: pathlib.Path

      

   .. py:attribute:: fpth_log
      :type: pathlib.Path

      

   .. py:attribute:: app_name
      :type: str

      

   .. py:attribute:: pyobject_read_dir
      :type: str

      

   .. py:attribute:: model_config

      

   .. py:method:: _key(v, values)


   .. py:method:: _fdir(v, values)


   .. py:method:: _fpth_log(v, values)



.. py:class:: SelectDir(**data: Any)

   Bases: :py:obj:`SelectDirBase`

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


   .. py:attribute:: usage
      :type: List[Usage]

      

   .. py:attribute:: pyobject
      :type: str

      


.. py:function:: get_projects()


.. py:function:: record_load(value)


.. py:function:: print_fdir(value)


.. py:class:: SelectDirUi(config: ipyautoui.custom.decision_branch.TreeModel, fdir_root: pathlib.Path = None, fdir_log: pathlib.Path = None, fn_onload: Union[Callable, List] = print_fdir, checks: List[Callable] = None)

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

   .. py:property:: fdir


   .. py:property:: fn_onload


   .. py:attribute:: value

      

   .. py:method:: _validate_value(proposal)


   .. py:method:: _observe_value_update_path(change)


   .. py:method:: _observe_value_run_checks(change)


   .. py:method:: _init_controls()


   .. py:method:: _load(onclick)


   .. py:method:: _update_value(onchange)



.. py:data:: c1_str_exists
   :value: '📁👍 - `{}` : folder exists in location. press to load.'

   

