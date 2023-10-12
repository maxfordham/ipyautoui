:py:mod:`ipyautoui.autoform`
============================

.. py:module:: ipyautoui.autoform


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.autoform.AutoObjectFormLayout
   ipyautoui.autoform.TestForm



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.autoform.show_hide_widget
   ipyautoui.autoform.make_bold
   ipyautoui.autoform.demo_autoobject_form



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.autoform.ui
   ipyautoui.autoform.form


.. py:function:: show_hide_widget(widget, show: bool)


.. py:function:: make_bold(s: str) -> str


.. py:class:: AutoObjectFormLayout(**kwargs)

   Bases: :py:obj:`traitlets.HasTraits`

   UI container for autoui form

   :ivar title: form title
   :vartype title: str
   :ivar description: form description
   :vartype description: str
   :ivar show_description: show the description. Defaults to True.
   :vartype show_description: bool, optional
   :ivar show_title: show the title. Defaults to True.
   :vartype show_title: bool, optional
   :ivar show_savebuttonbar: show the savebuttonbar. Defaults to True.
   :vartype show_savebuttonbar: bool, optional
   :ivar show_raw: show the raw json. Defaults to False.
   :vartype show_raw: bool, optional
   :ivar fn_onshowraw: do not edit
   :vartype fn_onshowraw: callable
   :ivar fn_onhideraw: do not edit
   :vartype fn_onhideraw: callable
   :ivar fns_onsave: additional functions to be called on save
   :vartype fns_onsave: callable
   :ivar fns_onrevert: additional functions to be called on revert

   :vartype fns_onrevert: callable

   .. py:property:: json


   .. py:attribute:: title

      

   .. py:attribute:: description

      

   .. py:attribute:: show_description

      

   .. py:attribute:: show_title

      

   .. py:attribute:: show_savebuttonbar

      

   .. py:attribute:: show_raw

      

   .. py:attribute:: fn_onshowraw

      

   .. py:attribute:: fn_onhideraw

      

   .. py:attribute:: fns_onsave

      

   .. py:attribute:: fns_onrevert

      

   .. py:method:: _observe_title(change)


   .. py:method:: _observe_description(change)


   .. py:method:: _observe_show_raw(change)


   .. py:method:: _observe_show_description(change)


   .. py:method:: _observe_show_title(change)


   .. py:method:: _observe_show_savebuttonbar(change)


   .. py:method:: _observe_fns_onsave(change)

      NOTE: this observer will alway append actions.
      to delete actions use
          `self.savebuttonbar.fns_onsave = []`
      then set with
          `self.fns_onsave = [lambda: print('save-funcy')]`


   .. py:method:: _observe_fns_onrevert(change)

      NOTE: this observer will alway append actions.
      to delete actions use
          `self.savebuttonbar.fns_onsave = []`
      then set with
          `self.fns_onrevert = [lambda: print('revert-funcy')]`


   .. py:method:: _default_fn_onshowraw()


   .. py:method:: _default_fn_onhideraw()


   .. py:method:: _default_fns_onsave()


   .. py:method:: _default_fns_onrevert()


   .. py:method:: _init_autoform(**kwargs)


   .. py:method:: _init_form()


   .. py:method:: _init_bn_showraw()


   .. py:method:: _init_bn_showraw_controls()


   .. py:method:: _bn_showraw(onchange)


   .. py:method:: display_ui()


   .. py:method:: display_showraw()



.. py:data:: ui

   

.. py:class:: TestForm(**kwargs)

   Bases: :py:obj:`AutoObjectFormLayout`, :py:obj:`ipywidgets.VBox`

   UI container for autoui form

   :ivar title: form title
   :vartype title: str
   :ivar description: form description
   :vartype description: str
   :ivar show_description: show the description. Defaults to True.
   :vartype show_description: bool, optional
   :ivar show_title: show the title. Defaults to True.
   :vartype show_title: bool, optional
   :ivar show_savebuttonbar: show the savebuttonbar. Defaults to True.
   :vartype show_savebuttonbar: bool, optional
   :ivar show_raw: show the raw json. Defaults to False.
   :vartype show_raw: bool, optional
   :ivar fn_onshowraw: do not edit
   :vartype fn_onshowraw: callable
   :ivar fn_onhideraw: do not edit
   :vartype fn_onhideraw: callable
   :ivar fns_onsave: additional functions to be called on save
   :vartype fns_onsave: callable
   :ivar fns_onrevert: additional functions to be called on revert

   :vartype fns_onrevert: callable


.. py:function:: demo_autoobject_form(title='test', description='a description of the title')

   for docs and testing only...


.. py:data:: form

   

