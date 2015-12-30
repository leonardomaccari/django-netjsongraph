django-netjsongraph
===================

Modified `django_netjsongraph <https://github.com/interop-dev/django-netjsongraph>`_ to store a history of saved graphs. Please see that project for all the features and options.

Settings
--------

This fork adds one configuration parameter to the existent ones.

+--------------------------------------+-------------------------------------+---------------------------------------------------------------------------------------------------+
| Setting                              | Default value                       | Description                                                                                       |
+======================================+=====================================+===================================================================================================+
| ``NETJSONGRAPH_PARSERS``             | ``[]``                              | List with additional custom `netdiff parsers <https://github.com/ninuxorg/netdiff#parsers>`_      |
+--------------------------------------+-------------------------------------+---------------------------------------------------------------------------------------------------+
| ``NETJSONGRAPH_SIGNALS``             | ``None``                            | String representing python module to import on initialization.                                    |
|                                      |                                     | Useful for loading django signals or to define custom behaviour.                                  |
+--------------------------------------+-------------------------------------+---------------------------------------------------------------------------------------------------+
| ``NETJSONGRAPH_UPDATE_HISTORY_LEN``  | ``0``                               | Number of snapshots that the app will store, 0 means the snapshot is always rewritten             |
+--------------------------------------+-------------------------------------+---------------------------------------------------------------------------------------------------+

.. _PEP8, Style Guide for Python Code: http://www.python.org/dev/peps/pep-0008/
.. _ninux-dev mailing list: http://ml.ninux.org/mailman/listinfo/ninux-dev
