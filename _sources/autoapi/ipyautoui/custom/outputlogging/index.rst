:py:mod:`ipyautoui.custom.outputlogging`
========================================

.. py:module:: ipyautoui.custom.outputlogging

.. autoapi-nested-parse::

   simple set-up of outputting logging messages to widgets output.



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.outputlogging.Output
   ipyautoui.custom.outputlogging.LoggingUiBase
   ipyautoui.custom.outputlogging.LoggingAccordion



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.outputlogging.div
   ipyautoui.custom.outputlogging.div



.. py:class:: Output(**kwargs)

   Bases: :py:obj:`ipywidgets.Output`

   Widget used as a context manager to display output.

   This widget can capture and display stdout, stderr, and rich output.  To use
   it, create an instance of it and display it.

   You can then use the widget as a context manager: any output produced while in the
   context will be captured and displayed in the widget instead of the standard output
   area.

   You can also use the .capture() method to decorate a function or a method. Any output
   produced by the function will then go to the output widget. This is useful for
   debugging widget callbacks, for example.

   Example::
       import ipywidgets as widgets
       from IPython.display import display
       out = widgets.Output()
       display(out)

       print('prints to output area')

       with out:
           print('prints to output widget')

       @out.capture()
       def func():
           print('prints to output widget')

   .. py:method:: register_logger(logger, *args, **kwargs)

      Registers a handler to given logger to send output to output widget

      .. rubric:: References

      https://github.com/jupyter-widgets/ipywidgets/pull/2268/files



.. py:class:: LoggingUiBase(loggers=None, logging_format=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'), title='Execution Log', clearable_logs=True)

   Bases: :py:obj:`traitlets.HasTraits`

   The base class for all classes that have descriptors.

   .. py:attribute:: clearable_logs

      

   .. py:method:: _clearable_logs(on_change)


   .. py:method:: _init_clearable_logs()


   .. py:method:: _call_clear_logs(on_click)


   .. py:method:: clear_logs()



.. py:class:: LoggingAccordion(loggers=None, logging_format=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'), title='Execution Log', **kwargs)

   Bases: :py:obj:`ipywidgets.Accordion`

   Displays children each on a separate accordion page.

   .. py:method:: _init_controls()


   .. py:method:: clear_logs(on_click)



.. py:function:: div(a, b)


.. py:function:: div(a, b)


