:py:mod:`ipyautoui.custom.modelrun`
===================================

.. py:module:: ipyautoui.custom.modelrun


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.modelrun.RunNameInputs
   ipyautoui.custom.modelrun.RunName




Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.modelrun.run


.. py:class:: RunNameInputs

   .. py:attribute:: index
      :type: int
      :value: 1

      

   .. py:attribute:: disabled_index
      :type: bool
      :value: False

      

   .. py:attribute:: zfill
      :type: int
      :value: 2

      

   .. py:attribute:: enum
      :type: List

      

   .. py:attribute:: delimiter
      :type: str
      :value: '-'

      

   .. py:attribute:: description_length
      :type: int

      

   .. py:attribute:: allow_spaces
      :type: bool
      :value: False

      

   .. py:attribute:: order
      :type: tuple
      :value: ('index', 'enum', 'description')

      

   .. py:attribute:: pattern
      :type: str

      

   .. py:method:: __post_init__()



.. py:class:: RunName(value=None, index: int = 1, disabled_index: bool = True, zfill: int = 2, enum: List = ['lean', 'clean', 'green'], delimiter: str = '-', description_length: int = 30, allow_spaces: bool = False, order=('index', 'enum', 'description'))

   Bases: :py:obj:`ipywidgets.HBox`

   widget for creating an modelling iteration name to a defined format from component parts

   .. rubric:: Example

   value = '000-lean-short_description_of_model-run'
   enum = ['lean', 'clean', 'green']
   zfill = 2

   .. py:property:: value


   .. py:property:: get_options


   .. py:attribute:: _value

      

   .. py:method:: _valid_value(proposal)


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: update_name(on_change)


   .. py:method:: _set_value()



.. py:data:: run

   

