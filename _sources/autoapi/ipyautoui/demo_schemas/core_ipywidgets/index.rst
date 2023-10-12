:py:mod:`ipyautoui.demo_schemas.core_ipywidgets`
================================================

.. py:module:: ipyautoui.demo_schemas.core_ipywidgets

.. autoapi-nested-parse::

   An example schema definition that demonstrates the current capability of the AutoUi class



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.core_ipywidgets.FruitEnum
   ipyautoui.demo_schemas.core_ipywidgets.Number
   ipyautoui.demo_schemas.core_ipywidgets.CoreIpywidgets




.. py:class:: FruitEnum

   Bases: :py:obj:`str`, :py:obj:`enum.Enum`

   fruit example.

   .. py:attribute:: apple
      :value: 'apple'

      

   .. py:attribute:: pear
      :value: 'pear'

      

   .. py:attribute:: banana
      :value: 'banana'

      

   .. py:attribute:: orange
      :value: 'orange'

      


.. py:class:: Number

   Bases: :py:obj:`enum.IntEnum`

   Enum where members are also (and must be) ints

   .. py:attribute:: ONE
      :value: 1

      

   .. py:attribute:: TWO
      :value: 2

      

   .. py:attribute:: THREE
      :value: 3

      


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

      


