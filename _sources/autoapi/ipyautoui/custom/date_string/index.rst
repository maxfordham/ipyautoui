:py:mod:`ipyautoui.custom.date_string`
======================================

.. py:module:: ipyautoui.custom.date_string


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.date_string.DatePickerString
   ipyautoui.custom.date_string.NaiveDatetimePickerString




.. py:class:: DatePickerString(*args, **kwargs)

   Bases: :py:obj:`ipywidgets.DatePicker`

   extends DatePicker to save a jsonable string _value

   .. py:attribute:: _value

      

   .. py:attribute:: strftime_format

      

   .. py:method:: _update_value_string(on_change)


   .. py:method:: _validate_value(proposal)

      Cap and floor value



.. py:class:: NaiveDatetimePickerString(*args, **kwargs)

   Bases: :py:obj:`ipywidgets.NaiveDatetimePicker`

   extends DatetimePicker to save a jsonable string _value

   .. py:attribute:: _value

      

   .. py:attribute:: strftime_format

      

   .. py:method:: _validate_value(proposal)

      Cap and floor value


   .. py:method:: _update_value_string(on_change)



