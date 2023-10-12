:py:mod:`ipyautoui.custom`
==========================

.. py:module:: ipyautoui.custom


Submodules
----------
.. toctree::
   :titlesonly:
   :maxdepth: 1

   autogrid/index.rst
   buttonbars/index.rst
   date_string/index.rst
   decision_branch/index.rst
   editgrid/index.rst
   filechooser/index.rst
   filesindir/index.rst
   fileupload/index.rst
   halo_decorator/index.rst
   iterable/index.rst
   loadproject/index.rst
   markdown_widget/index.rst
   modelrun/index.rst
   multi_toggle_buttons/index.rst
   multiselect_search/index.rst
   outputlogging/index.rst
   selectandclick/index.rst
   selectdir/index.rst
   showhide/index.rst
   showopenurl/index.rst
   title_description/index.rst
   urlimagelink/index.rst
   widgetcaller_error/index.rst
   workingdir/index.rst


Package Contents
----------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.custom.FileChooser
   ipyautoui.custom.MultiSelectSearch
   ipyautoui.custom.AutoArray
   ipyautoui.custom.Array
   ipyautoui.custom.LoadProject
   ipyautoui.custom.SaveButtonBar




.. py:class:: FileChooser(value: pathlib.Path = None, **kwargs)

   Bases: :py:obj:`ipyfilechooser.FileChooser`

   inherits ipyfilechooster.FileChooser but initialises
   with a value= kwarg and adds a fc.value property. this
   follows the same convention as ipywidgets and therefore integrates
   better wiht ipyautoui

   Reference:
       https://github.com/crahan/ipyfilechooser

   .. py:property:: value

      Get selected value.

   .. py:attribute:: _value

      

   .. py:method:: _default_value()


   .. py:method:: _init_controls()


   .. py:method:: _set_value(onchange)



.. py:class:: MultiSelectSearch(options=[], value=[])

   Bases: :py:obj:`ipywidgets.VBox`

   multi-checkbox select widget with search

   Reference:
       multi-select widget:
           https://gist.github.com/MattJBritton/9dc26109acb4dfe17820cf72d82f1e6f

   .. py:property:: options


   .. py:property:: value


   .. py:attribute:: _options

      

   .. py:attribute:: _value

      

   .. py:method:: _init_controls()


   .. py:method:: _check_all(onchange)


   .. py:method:: _uncheck_all(onchange)


   .. py:method:: _delete_checked(onchange)


   .. py:method:: multi_checkbox_widget(options_dict)

      Widget with a search field and lots of checkboxes



.. py:class:: AutoArray(**kwargs)

   Bases: :py:obj:`Array`

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

   .. py:property:: value


   .. py:attribute:: allOf

      

   .. py:attribute:: items

      

   .. py:attribute:: prefix_items

      

   .. py:method:: _allOf(on_change)


   .. py:method:: _items(on_change)


   .. py:method:: from_schema(schema, value=None)
      :classmethod:



.. py:class:: Array(**kwargs)

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

   .. py:property:: value


   .. py:attribute:: _value

      

   .. py:attribute:: fn_add

      

   .. py:attribute:: fn_remove

      

   .. py:attribute:: sort_on_index

      

   .. py:attribute:: length

      

   .. py:attribute:: add_remove_controls

      

   .. py:attribute:: align_horizontal

      

   .. py:attribute:: min_items

      

   .. py:attribute:: max_items

      

   .. py:attribute:: type

      

   .. py:method:: _type(proposal)


   .. py:method:: _length(on_change)


   .. py:method:: _valid_fn_remove(proposal)


   .. py:method:: _add_remove_controls(on_change)


   .. py:method:: _align_horizontal(on_change)


   .. py:method:: display_bn_add_from_zero(display: bool)


   .. py:method:: _init_controls()


   .. py:method:: get_length(on_change)


   .. py:method:: _get_attribute(key, get)


   .. py:method:: _init_row_controls(key=None)


   .. py:method:: _sort_boxes()


   .. py:method:: _update_value(on_change)


   .. py:method:: _update_boxes()


   .. py:method:: _append_row(onclick)


   .. py:method:: _add_row(onclick, key=None)


   .. py:method:: add_row(key=None, new_key=None, add_kwargs=None, widget=None)

      add row to array after key. if key=None then append to end


   .. py:method:: _remove_rows(onclick, key=None)


   .. py:method:: remove_row(key=None, fn_onremove=None)



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



.. py:class:: SaveButtonBar(**kwargs)

   Bases: :py:obj:`SaveActions`, :py:obj:`ipywidgets.HBox`

   The base class for all classes that have descriptors.

   .. py:method:: _init_form()


   .. py:method:: _init_controls()


   .. py:method:: _save(click)


   .. py:method:: _revert(click)


   .. py:method:: _observe_unsaved_changes(onchange)


   .. py:method:: _observe_tgl_unsaved_changes(onchange)



