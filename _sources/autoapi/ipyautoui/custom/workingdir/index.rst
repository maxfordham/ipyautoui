:py:mod:`ipyautoui.custom.workingdir`
=====================================

.. py:module:: ipyautoui.custom.workingdir

.. autoapi-nested-parse::

   a UI element that loads a folder for data caching, whilst storing a record of folders in use



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.workingdir.RibaStages
   ipyautoui.custom.workingdir.ProcessSubType
   ipyautoui.custom.workingdir.Usage
   ipyautoui.custom.workingdir.WorkingDir
   ipyautoui.custom.workingdir.WorkingDirs
   ipyautoui.custom.workingdir.AnalysisDir
   ipyautoui.custom.workingdir.WorkingDirsUi



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.workingdir.get_projects
   ipyautoui.custom.workingdir.get_working_dirs
   ipyautoui.custom.workingdir.add_working_dir
   ipyautoui.custom.workingdir.is_templated_dir
   ipyautoui.custom.workingdir.make_dirs
   ipyautoui.custom.workingdir.return_fdir_status
   ipyautoui.custom.workingdir.create_folder_structure



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.workingdir.get_fpth_win
   ipyautoui.custom.workingdir.FDIR_PROJECTS_ROOT
   ipyautoui.custom.workingdir.FPTH_WORKING_DIRS
   ipyautoui.custom.workingdir.description
   ipyautoui.custom.workingdir.fix_attributes


.. py:data:: get_fpth_win

   

.. py:data:: FDIR_PROJECTS_ROOT

   

.. py:data:: FPTH_WORKING_DIRS

   

.. py:function:: get_projects()


.. py:class:: RibaStages

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

   .. py:attribute:: stage1
      :value: 'Stage1'

      

   .. py:attribute:: stage2
      :value: 'Stage2'

      

   .. py:attribute:: stage3
      :value: 'Stage3'

      

   .. py:attribute:: stage4
      :value: 'Stage4'

      

   .. py:attribute:: stage5
      :value: 'Stage5'

      

   .. py:attribute:: stage6
      :value: 'Stage6'

      

   .. py:attribute:: stage7
      :value: 'Stage7'

      


.. py:class:: ProcessSubType

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

   .. py:attribute:: wufi
      :value: 'WUFI'

      

   .. py:attribute:: tm52
      :value: 'TM52'

      

   .. py:attribute:: tm54
      :value: 'TM54'

      

   .. py:attribute:: tm59
      :value: 'TM59'

      

   .. py:attribute:: compliance
      :value: 'compliance'

      

   .. py:attribute:: compliance_london_plan
      :value: 'compliance_london_plan'

      


.. py:class:: Usage(**data: Any)

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


   .. py:attribute:: user
      :type: str

      

   .. py:attribute:: timestamp
      :type: datetime.datetime

      


.. py:class:: WorkingDir(**data: Any)

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


   .. py:attribute:: process_type
      :type: str

      

   .. py:attribute:: process_subtype
      :type: str

      

   .. py:attribute:: project_number
      :type: str

      

   .. py:attribute:: riba_stage
      :type: RibaStages

      

   .. py:attribute:: fdir
      :type: pathlib.Path

      

   .. py:attribute:: key
      :type: str

      

   .. py:attribute:: usage
      :type: List[Usage]

      

   .. py:attribute:: dir_model
      :type: str

      

   .. py:method:: _fdir(v, values)


   .. py:method:: _key(v, values)



.. py:data:: description
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """
        a list of all the active working directories used for jupyter / ipyrun based analyses / processes / workflows
        """

    .. raw:: html

        </details>

   

.. py:class:: WorkingDirs(**data: Any)

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
      :value: 'working dirs'

      

   .. py:attribute:: description
      :type: str

      

   .. py:attribute:: dirs
      :type: Dict[str, WorkingDir]

      


.. py:function:: get_working_dirs(path=FPTH_WORKING_DIRS)

   loads working dir from folder


.. py:class:: AnalysisDir(**data: Any)

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


   .. py:attribute:: fdir
      :type: pathlib.Path

      

   .. py:attribute:: reference
      :type: pathlib.Path

      

   .. py:attribute:: incoming
      :type: pathlib.Path

      

   .. py:attribute:: input_data
      :type: pathlib.Path

      

   .. py:attribute:: cad
      :type: pathlib.Path

      

   .. py:attribute:: images
      :type: pathlib.Path

      

   .. py:attribute:: calcs
      :type: pathlib.Path

      

   .. py:attribute:: models
      :type: pathlib.Path

      

   .. py:attribute:: outputs
      :type: pathlib.Path

      

   .. py:method:: _reference(v, values)


   .. py:method:: _incoming(v, values)


   .. py:method:: _input_data(v, values)


   .. py:method:: _cad(v, values)


   .. py:method:: _images(v, values)


   .. py:method:: _calcs(v, values)


   .. py:method:: _models(v, values)


   .. py:method:: _outputs(v, values)



.. py:function:: add_working_dir(wdir: Union[dict, WorkingDir], path: pathlib.Path = FPTH_WORKING_DIRS)

   add a working directory to global json log


.. py:function:: is_templated_dir(adir: Type[pydantic.BaseModel])


.. py:function:: make_dirs(adir)


.. py:function:: return_fdir_status(adir, display_message=True, map_dir=True)

   checks if a dir is already an analysis dir or not


.. py:function:: create_folder_structure(value, model_dirs=AnalysisDir)


.. py:class:: WorkingDirsUi(fn_onload: Union[Callable, List] = lambda value: print('fn_onload'), model_dirs: Type[pydantic.BaseModel] = AnalysisDir, fix_attributes={}, projects=None, fdir_projects_root=FDIR_PROJECTS_ROOT, fpth_working_dirs=FPTH_WORKING_DIRS)

   Bases: :py:obj:`ipywidgets.HBox`

   a programmable UI object to load new working directories for ipyrun.runshell # TODO: move to ipyrun

   .. py:property:: fdir_display


   .. py:property:: fn_onload


   .. py:property:: fix_attributes


   .. py:attribute:: value

      

   .. py:attribute:: setup

      

   .. py:attribute:: load

      

   .. py:attribute:: project_number

      

   .. py:attribute:: projects

      

   .. py:attribute:: process_type

      

   .. py:attribute:: process_subtype

      

   .. py:attribute:: riba_stage

      

   .. py:attribute:: key

      

   .. py:attribute:: fdir_win

      

   .. py:attribute:: fdir_win_proposed

      

   .. py:method:: _projects(change)


   .. py:method:: _observe_value_key(change)


   .. py:method:: _observe_value_fdir_win_proposed(change)


   .. py:method:: _update_value()


   .. py:method:: update_from_ui(change)


   .. py:method:: _init_controls()


   .. py:method:: _update_fdir_win()


   .. py:method:: _load(onchange)



.. py:data:: fix_attributes

   

