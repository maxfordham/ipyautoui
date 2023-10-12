:py:mod:`ipyautoui._utils_debounce`
===================================

.. py:module:: ipyautoui._utils_debounce


Module Contents
---------------

Classes
~~~~~~~

.. autoapisummary::

   ipyautoui._utils_debounce.Timer



Functions
~~~~~~~~~

.. autoapisummary::

   ipyautoui._utils_debounce.debounce



.. py:class:: Timer(timeout, callback)

   .. py:method:: _job()
      :async:


   .. py:method:: start()


   .. py:method:: cancel()



.. py:function:: debounce(wait)

   Decorator that will postpone a function's
   execution until after `wait` seconds
   have elapsed since the last time it was invoked.


