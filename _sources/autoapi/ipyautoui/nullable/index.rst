:py:mod:`ipyautoui.nullable`
============================

.. py:module:: ipyautoui.nullable


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui.nullable.Nullable



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui.nullable._get_value_trait
   ipyautoui.nullable.is_null
   ipyautoui.nullable.nullable



Attributes
~~~~~~~~~~

.. autoapisummary::

   ipyautoui.nullable.SHOW_NONE_KWARGS


.. py:data:: SHOW_NONE_KWARGS

   

.. py:function:: _get_value_trait(obj_with_traits)

   gets the trait type for a given object
   (looks for "_value" and "value" allowing use of setters and getters)
   :param obj_with_traits: obj with traits
   :type obj_with_traits: traitlets.Type

   :raises ValueError: if "value" trait not exist

   :returns: trait type of traitlet
   :rtype: typing.Type


.. py:function:: is_null(value)

   .. rubric:: Example

   >>> [is_null(value) for value in [math.nan, np.nan, None, pd.NA, 3.3, "adsf"]]
   [True, True, True, True, False, False]


.. py:class:: Nullable(widget_type, *args, **kwargs)

   Bases: :py:obj:`ipywidgets.HBox`

   class to allow widgets to be nullable. The widget that is extended is accessed
   using `self.widget`

   .. py:property:: value


   .. py:attribute:: disabled

      

   .. py:attribute:: nullable

      

   .. py:method:: observe_disabled(on_change)

      If disabled, ensure that the widget is disabled and the button is also.


   .. py:method:: _init_trait()


   .. py:method:: update_value(value)


   .. py:method:: _init_controls()


   .. py:method:: _observe_nullable(onchange)


   .. py:method:: _update(onchange, name='_value')


   .. py:method:: _toggle_none(onchange)



.. py:function:: nullable(fn, **kwargs)

   extend a simple widget to allow None

   :param fn: e.g. w.IntText
   :type fn: widget_type

   :returns: a HBox that contains a the widget `widget`.
   :rtype: Nullable


