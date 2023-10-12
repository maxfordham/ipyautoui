:py:mod:`ipyautoui.automapschema`
=================================

.. py:module:: ipyautoui.automapschema


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.automapschema.WidgetMapper
   ipyautoui.automapschema.WidgetCaller
   ipyautoui.automapschema.AutoPlaceholder



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.automapschema._init_model_schema
   ipyautoui.automapschema.is_allowed_type
   ipyautoui.automapschema.flatten_allOf
   ipyautoui.automapschema.handle_null_or_unknown_types
   ipyautoui.automapschema.is_anyof_widget
   ipyautoui.automapschema.is_Nullable
   ipyautoui.automapschema.is_AnyOf
   ipyautoui.automapschema.is_IntText
   ipyautoui.automapschema.is_IntSlider
   ipyautoui.automapschema.is_FloatText
   ipyautoui.automapschema.is_FloatSlider
   ipyautoui.automapschema.is_range
   ipyautoui.automapschema.is_IntRangeSlider
   ipyautoui.automapschema.is_FloatRangeSlider
   ipyautoui.automapschema.is_Date
   ipyautoui.automapschema.is_Datetime
   ipyautoui.automapschema.is_Color
   ipyautoui.automapschema.is_Path
   ipyautoui.automapschema.is_anyof_combobox
   ipyautoui.automapschema.is_Combobox
   ipyautoui.automapschema.is_Dropdown
   ipyautoui.automapschema.is_Markdown
   ipyautoui.automapschema.isnot_Text
   ipyautoui.automapschema.is_Text
   ipyautoui.automapschema.is_Textarea
   ipyautoui.automapschema.is_SelectMultiple
   ipyautoui.automapschema.is_Checkbox
   ipyautoui.automapschema.is_AutoOveride
   ipyautoui.automapschema.is_Object
   ipyautoui.automapschema.is_DataFrame
   ipyautoui.automapschema.is_Array
   ipyautoui.automapschema.update_keys
   ipyautoui.automapschema.remove_title_and_description
   ipyautoui.automapschema.create_widget_caller
   ipyautoui.automapschema.flatten_type_and_nullable
   ipyautoui.automapschema.add_schema_key
   ipyautoui.automapschema.add_max_layout
   ipyautoui.automapschema.widgetcaller
   ipyautoui.automapschema.update_widgets_map
   ipyautoui.automapschema.get_range_min_and_max
   ipyautoui.automapschema.dropdown_drop_null_value
   ipyautoui.automapschema.get_widgets_map
   ipyautoui.automapschema.get_autooveride
   ipyautoui.automapschema.map_widget
   ipyautoui.automapschema.get_widget
   ipyautoui.automapschema.from_schema_method
   ipyautoui.automapschema.from_model_method



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.automapschema.logger
   ipyautoui.automapschema.di


.. py:data:: logger

   

.. py:function:: _init_model_schema(schema, by_alias=False) -> tuple[Optional[Type[pydantic.BaseModel]], dict]


.. py:function:: is_allowed_type(di: dict) -> bool


.. py:function:: flatten_allOf(di: dict) -> dict


.. py:function:: handle_null_or_unknown_types(fn, di: dict) -> tuple[bool, bool]


.. py:function:: is_anyof_widget(fn)


.. py:function:: is_Nullable(fn: Callable, di: dict) -> tuple[bool, bool]


.. py:function:: is_AnyOf(di: dict, allow_none=False, checked_nullable=False)

   ```py
   from ipyautoui.automapschema import is_AnyOf

   print(is_AnyOf({'title': 'Int Text', "anyOf": [{'default': 1, 'type': 'integer'}, {"type": "string"}]}))
   #> (True, False)
   ```


.. py:function:: is_IntText(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_IntText

   is_IntText({'title': 'Int Text', 'default': 1, 'type': 'integer'})
   (True, False)
   is_IntText({'title': 'Int Text', 'default': 1, 'type': 'number'})
   (False, False)
   is_IntText({'title': 'floater', 'default': 1.33, 'type': 'number'})
   (False, False)
   is_IntText({'title': 'floater', 'default':1, 'anyOf': [{'type': 'integer'},{'type': 'null'}]})
   (True, True)
   ```


.. py:function:: is_IntSlider(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_IntSlider

   print(is_IntSlider({'title': 'int', 'default': 1, 'type': 'number'}))
   #> (False, False)
   print(is_IntSlider({'title': 'int', 'default': 1, 'type': 'integer'}))
   #> (False, False)
   print(is_IntSlider({'title': 'int', 'default': 1, 'type': 'integer', "minimum": 0, "maximum": 3}))
   #> (True, False)
   print(is_IntSlider({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3}))
   #> (False, False)
   print(is_IntSlider({'title': 'int', 'default': 1, 'anyOf': [{'type': 'integer', "minimum": 0, "maximum": 3}, {'type': 'null'}]}))
   #> (True, True)
   ```


.. py:function:: is_FloatText(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_FloatText

   print(is_FloatText({'title': 'floater', 'default': 1.33, 'type': 'number'}))
   #> (True, False)
   print(is_FloatText({'title': 'floater', 'default': 1, 'type': 'integer'}))
   #> (False, False)
   print(is_FloatText({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3}))
   #> (False, False)
   ```


.. py:function:: is_FloatSlider(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_FloatSlider

   print(is_FloatSlider({'title': 'floater', 'default': 1.33, 'type': 'number'}))
   #> (False, False)
   print(is_FloatSlider({'title': 'floater', 'default': 1, 'type': 'integer'}))
   #> (False, False)
   print(is_FloatSlider({'title': 'floater', 'default': 1, 'type': 'integer', "minimum": 0, "maximum": 3}))
   #> (False, False)
   print(is_FloatSlider({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3}))
   #> (True, False)
   ```


.. py:function:: is_range(di, is_type='numeric')

   finds numeric range within schema properties. a range in json must satisfy these criteria:
   - check1: array length == 2
   - check2: minimum and maximum values must be given
   - check3: check numeric typ given (i.e. integer or number or numeric)


.. py:function:: is_IntRangeSlider(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   Example:
   ```py
   from ipyautoui.automapschema import is_IntRangeSlider
   di = {'default': [0, 3],
       'maxItems': 2,
       'minItems': 2,
       'prefixItems': [{'maximum': 4, 'minimum': 0, 'type': 'integer'},
           {'maximum': 4, 'minimum': 0, 'type': 'integer'}],
       'title': 'Int Range Slider',
       'type': 'array'}
   print(is_IntRangeSlider(di))
   #> (True, False)
   di["anyOf"] = [{"type": "array"}, {"type": "null"}]
   del di["type"]
   print(is_IntRangeSlider(di))
   #> (True, True)
   ```


.. py:function:: is_FloatRangeSlider(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   Example:
   ```py
   from ipyautoui.automapschema import is_FloatRangeSlider
   di = {'default': [0.5, 3.4],
       'maxItems': 2,
       'minItems': 2,
       'prefixItems': [{'maximum': 4, 'minimum': 0, 'type': 'number'},
           {'maximum': 4, 'minimum': 0, 'type': 'number'}],
       'title': 'Float Range Slider',
       'type': 'array'}
   print(is_FloatRangeSlider(di))
   #> (True, False)
   di["anyOf"] = [{"type": "array"}, {"type": "null"}]
   del di["type"]
   print(is_FloatRangeSlider(di))
   #> (True, True)
   ```


.. py:function:: is_Date(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_Date# , is_Text
   di = {"title": "Date Picker", "default": "2022-04-28", "type": "string", "format": "date"}
   is_Date(di)
   #> print(True)
   # is_Text(di)
   # #> print(False)
   ```


.. py:function:: is_Datetime(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_Datetime, is_Date
   di = {"title": "Datetime Picker", "type": "string", "format": "date-time"}
   is_Datetime(di)
   #> print(True)
   is_Date(di)
   #> print(False)
   # is_Text(di)
   #> print(False)
   ```


.. py:function:: is_Color(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   check if schema object is a color

   :param di: schema object
   :type di: dict

   :returns: is the object a color
   :rtype: bool

   .. rubric:: Example

   ```py
   from ipyautoui.automapschema import is_Color# , is_Text
   di = {"title": "Color Picker Ipywidgets", "default": "#f5f595","type": "string", "format": "hexcolor"}
   print(is_Color(di))
   #> (True, False)
   di = {"title": "Path", "default": ".", "type": "string", "format": "path"}
   print(is_Color(di))
   #> (False, False)
   ```


.. py:function:: is_Path(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   check if schema object is a path

   :param di: schema object
   :type di: dict

   :returns: is the object a color
   :rtype: bool

   .. rubric:: Example

   ```py
   from ipyautoui.automapschema import is_Path
   di = {"title": "Path", "default": ".", "type": "string", "format": "path"}
   print(is_Path(di))
   #> (True, False)
   ```


.. py:function:: is_anyof_combobox(di: dict) -> bool


.. py:function:: is_Combobox(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_Combobox
   di = {'anyOf': [{'enum': ['a', 'b'],
       'title': 'TestEnum',
       'type': 'string'},
       {'type': 'string'}],
   'default': 'a'}
   print(is_Combobox(di))
   #> (True, False)
   ```


.. py:function:: is_Dropdown(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_Dropdown
   di = {"title": "Dropdown", "enum": [1,2], "type": "integer"}
   print(is_Dropdown(di))
   #> (True, False)
   di = {"title": "Dropdown", "enum": [1,2], "anyOf":[ {"type": "integer"}, {"type": "null"}]}
   print(is_Dropdown(di))
   #> (True, True)
   ```


.. py:function:: is_Markdown(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_Markdown
   di = {'title': 'Markdown', 'type': 'string', 'format': 'markdown'}
   print(is_Markdown(di))
   #> (True, False)
   ```


.. py:function:: isnot_Text(di: dict) -> bool


.. py:function:: is_Text(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   check if schema object is a Text

   :param di: schema object
   :type di: dict

   :returns: is the object a Text
   :rtype: bool

   ```py
   from ipyautoui.automapschema import is_Text
   di = {"title": "Text", "default": "default string","type": "string"}
   print(is_Text(di))
   #> (True, False)
   di = {"title": "Text", "default": 210*"s", "type": "string", "maxLength":210}
   print(is_Text(di))
   #> (False, False)
   di = {"title": "Text", "default": 199*"s", "anyOf": [{"type":"string"}, {"type":"null"}]}
   print(is_Text(di))
   #> (True, True)
   ```


.. py:function:: is_Textarea(di: dict, max_length=200, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   check if schema object is a is_Textarea

   :param di: schema object
   :type di: dict

   :returns: is the object a is_Textarea
   :rtype: bool

   ```py
   from ipyautoui.automapschema import is_Textarea
   di = {"title": "Text", "default": 210*"s", "type": "string", "maxLength":210}
   print(is_Textarea(di))
   #> (True, False)
   d = 210*"s"
   di = {"title": "Text",  "anyOf": [{"type":"string", "maxLength":210, "default": d}, {"type":"null"}]}
   print(is_Textarea(di))
   #> (True, True)
   ```


.. py:function:: is_SelectMultiple(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_SelectMultiple
   di = {"title": "Dropdown", "enum": [1,2], "type": "array"}
   print(is_SelectMultiple(di))
   #> (True, False)
   ```


.. py:function:: is_Checkbox(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_Checkbox
   di = {"title": "Checkbox", "type": "boolean"}
   print(is_Checkbox(di))
   #> (True, False)
   ```


.. py:function:: is_AutoOveride(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]


.. py:function:: is_Object(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_Object
   di = {"title": "Checkbox", "type": "object"}
   print(is_Object(di))
   #> (True, False)
   ```


.. py:function:: is_DataFrame(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_DataFrame
   di = {"title": "Checkbox", "type": "array", "format": "dataframe"}
   print(is_DataFrame(di))
   #> (True, False)
   ```


.. py:function:: is_Array(di: dict, allow_none=False, checked_nullable=False) -> tuple[bool, bool]

   ```py
   from ipyautoui.automapschema import is_Array
   di = {"title": "is_Array", "type": "array"}
   print(is_Array(di))
   #> (True, False)
   ```


.. py:function:: update_keys(di, di_map=MAP_JSONSCHEMA_TO_IPYWIDGET)


.. py:function:: remove_title_and_description(di)


.. py:function:: create_widget_caller(schema, calling=None, remove_title=True)

   creates a "caller" object from the schema.
   this renames schema keys as follows to match ipywidgets:
       ```
       {
           'minimum': 'min',
           'maximum': 'max',
           'enum': 'options',
           'default': 'value',
           'description': 'autoui_description'
       }
       ```


   :param schema: dict, json schema
   :param calling: the class that will be called by the
                   returned "caller" object. if not None, args not present in the class
                   are removed from "caller"
   :param default=None: the class that will be called by the
                        returned "caller" object. if not None, args not present in the class
                        are removed from "caller"

   :returns:

             dict, object that is passed the "calling" widget
                 initialised like ```calling(**caller)```
   :rtype: caller


.. py:function:: flatten_type_and_nullable(di: dict, fn=None) -> dict


.. py:function:: add_schema_key(di: dict, wi=None) -> dict


.. py:function:: add_max_layout(di: dict, wi=None) -> dict


.. py:class:: WidgetMapper(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   defines a filter function and associated widget. the "fn_filt" is used to search the
   json schema to find appropriate objects, the objects are then passed to the "widget" for the ui

   .. py:attribute:: fn_filt
      :type: Callable

      

   .. py:attribute:: li_fn_modify
      :type: list[Callable[[dict, Callable], dict]]

      

   .. py:attribute:: widget
      :type: Callable

      


.. py:class:: WidgetCaller(**data: Any)

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


   .. py:attribute:: schema_
      :type: Dict

      

   .. py:attribute:: autoui
      :type: Callable

      

   .. py:attribute:: allow_none
      :type: bool
      :value: False

      

   .. py:attribute:: args
      :type: List

      

   .. py:attribute:: kwargs
      :type: Dict

      

   .. py:attribute:: kwargs_box
      :type: Dict

      


.. py:function:: widgetcaller(caller: WidgetCaller, show_errors=True)

   returns widget from widget caller object
   :param caller: WidgetCaller

   :returns: widget of some kind


.. py:function:: update_widgets_map(widgets_map, di_update=None)

   update the widget mapper frozen object

   :param widgets_map: _description_
   :type widgets_map: dict of WidgetMappers
   :param di_update: _description_. Defaults to None.
   :type di_update: _type_, optional


.. py:function:: get_range_min_and_max(schema, call=None)


.. py:function:: dropdown_drop_null_value(kwargs, call=None)


.. py:class:: AutoPlaceholder(**kwargs)

   Bases: :py:obj:`ipywidgets.Textarea`

   Multiline text area widget.


.. py:function:: get_widgets_map(di_update=None)


.. py:function:: get_autooveride(schema)


.. py:function:: map_widget(di: dict, widgets_map: ipyautoui._utils.frozenmap = None, fail_on_error: bool = False) -> WidgetCaller

   map_widget maps a json schema to a widget. it uses the widgets_map to find the correct widget.
   Example:
   ```py
   from ipyautoui.automapschema import is_FloatText
   print(is_FloatText({'title': 'floater', 'default': 1.33, 'type': 'number'}))
   #> (True, False)
   print(is_FloatText({'title': 'floater', 'default': 1, 'type': 'integer'}))
   #> (False, False)
   print(is_FloatText({'title': 'floater', 'default': 1, 'type': 'number', "minimum": 0, "maximum": 3}))
   #> (False, False)
   ```


.. py:function:: get_widget(di)


.. py:data:: di

   

.. py:function:: from_schema_method(cls, schema: Union[Type[pydantic.BaseModel], dict], value: Optional[dict] = None)


.. py:function:: from_model_method(cls, model: Type[pydantic.BaseModel], value: Optional[dict] = None)


