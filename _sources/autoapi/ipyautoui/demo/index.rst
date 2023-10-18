:py:mod:`ipyautoui.demo`
========================

.. py:module:: ipyautoui.demo


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.demo.Demo
   ipyautoui.demo.DemoReel



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.demo.get_classes
   ipyautoui.demo.get_order
   ipyautoui.demo.demo



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.demo.pycall


.. py:function:: get_classes(member=demo_schemas) -> List[Type[pydantic.BaseModel]]


.. py:function:: get_order()


.. py:data:: pycall
   :value: Multiline-String

    .. raw:: html

        <details><summary>Show Value</summary>

    .. code-block:: python

        """# copy code below into your notebook to try demo
        from ipyautoui import AutoUi
        from ipyautoui.demo_schemas import {name}
        AutoUi({name})
        """

    .. raw:: html

        </details>

   

.. py:class:: Demo(pydantic_model=CoreIpywidgets)

   Bases: :py:obj:`ipywidgets.Tab`, :py:obj:`traitlets.HasTraits`

   Displays children each on a separate accordion tab.

   .. py:attribute:: pydantic_model

      

   .. py:attribute:: python_file

      

   .. py:method:: _observe_pydantic_model(change)


   .. py:method:: _observe_selected_index(change)


   .. py:method:: _update_pycall()


   .. py:method:: _update_autoui()


   .. py:method:: _update_pydantic()


   .. py:method:: _update_jsonschema()


   .. py:method:: _update_jsonschema_caller()


   .. py:method:: _update_value()



.. py:class:: DemoReel(pydantic_models: List[Type[pydantic.BaseModel]] = get_classes(member=demo_schemas))

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

   .. py:attribute:: pydantic_models

      

   .. py:method:: _observe_pydantic_models(onchange)


   .. py:method:: _init_controls()


   .. py:method:: _update_demo(on_change)



.. py:function:: demo()


