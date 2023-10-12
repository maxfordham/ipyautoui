:py:mod:`ipyautoui.demo_schemas.complex_serialization`
======================================================

.. py:module:: ipyautoui.demo_schemas.complex_serialization


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo_schemas.complex_serialization.ComplexSerialisation




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

      


