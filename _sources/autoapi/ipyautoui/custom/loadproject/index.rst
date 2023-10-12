:py:mod:`ipyautoui.custom.loadproject`
======================================

.. py:module:: ipyautoui.custom.loadproject

.. autoapi-nested-parse::

   generic iterable object.



Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.loadproject.LoadProject



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.loadproject.fn_loadproject



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.custom.loadproject.LI_PROJECTS
   ipyautoui.custom.loadproject.load_project


.. py:function:: fn_loadproject(project_number)


.. py:data:: LI_PROJECTS
   :value: ['J0001', 'J0352', 'J0354', 'J0373', 'J0378', 'J0385', 'J0521', 'J0612', 'J1074', 'J1146']

   

.. py:class:: LoadProject(project_number='J5001', example_project='J5001', example_project_tooltip='load job. NOTE. RED BORDER INDICATES THE ENGINEERING STANDARDS EXAMPLE JOB IS SELECTED', pattern='J[0-9][0-9][0-9][0-9]', li_projects=LI_PROJECTS, fn_loadproject=lambda project_number: print(f'load project: {project_number}'))

   Bases: :py:obj:`ipywidgets.HBox`, :py:obj:`traitlets.HasTraits`

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

   .. py:attribute:: value

      

   .. py:method:: _valid_value(proposal)


   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: _project_load(on_click)


   .. py:method:: _highlight_example_job()



.. py:data:: load_project

   

