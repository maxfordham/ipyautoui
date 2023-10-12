:py:mod:`ipyautoui.custom.decision_branch`
==========================================

.. py:module:: ipyautoui.custom.decision_branch

.. autoapi-nested-parse::

   a UI element that loads a folder for data caching, whilst storing a record of folders in use



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.decision_branch.TreeModel
   ipyautoui.custom.decision_branch.DecisionUi



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.decision_branch.gen_widget



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.decision_branch.PROJECTS


.. py:class:: TreeModel(**data: Any)

   Bases: :py:obj:`pydantic.BaseModel`

   generic tree model.

   .. py:attribute:: title
      :type: str

      

   .. py:attribute:: description
      :type: str
      :value: ''

      

   .. py:attribute:: options
      :type: list

      

   .. py:attribute:: value
      :type: Union[str, float, int]

      

   .. py:attribute:: children
      :type: ty.ForwardRef('TreeModel')

      

   .. py:attribute:: disabled
      :type: bool
      :value: False

      

   .. py:attribute:: placeholder
      :type: str
      :value: ''

      

   .. py:attribute:: model_config

      


.. py:function:: gen_widget(di, widgets=[])


.. py:class:: DecisionUi(config: TreeModel, value=None)

   Bases: :py:obj:`ipywidgets.HBox`

   Displays multiple widgets horizontally using the flexible box model.

   Parameters
   ----------
   {box_params}

   Examples
   --------
   >>> import ipywidgets as widgets
   >>> title_widget = widgets.HTML('<em>Horizontal Box Example</em>')
   >>> slider = widgets.IntSlider()
   >>> widgets.HBox([title_widget, slider])

   .. py:property:: disabled


   .. py:property:: value


   .. py:attribute:: config

      

   .. py:attribute:: _value

      

   .. py:method:: _valid_config(proposal)


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: _update_value(change)



.. py:data:: PROJECTS
   :value: ['J5001', 'J5002']

   

