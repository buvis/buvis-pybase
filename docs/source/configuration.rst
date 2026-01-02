Configuration
=============

This module provides configuration management with precedence: CLI > ENV > YAML > Defaults.

Quick Start
-----------

.. code-block:: python

    from buvis.pybase.configuration import get_settings, buvis_options

    @click.command()
    @buvis_options
    @click.pass_context
    def main(ctx):
        settings = get_settings(ctx)
        if settings.debug:
            ...

Core Classes
------------

Configuration
~~~~~~~~~~~~~

.. autoclass:: buvis.pybase.configuration.Configuration
   :members:
   :undoc-members:
   :show-inheritance:

BuvisSettings
~~~~~~~~~~~~~

.. autoclass:: buvis.pybase.configuration.BuvisSettings
   :members:
   :undoc-members:
   :show-inheritance:

GlobalSettings
~~~~~~~~~~~~~~

.. autoclass:: buvis.pybase.configuration.GlobalSettings
   :members:
   :undoc-members:
   :show-inheritance:

ToolSettings
~~~~~~~~~~~~

.. autoclass:: buvis.pybase.configuration.ToolSettings
   :members:
   :undoc-members:
   :show-inheritance:

ConfigurationLoader
~~~~~~~~~~~~~~~~~~~

.. autoclass:: buvis.pybase.configuration.ConfigurationLoader
   :members:
   :undoc-members:
   :show-inheritance:

ConfigResolver
~~~~~~~~~~~~~~

.. autoclass:: buvis.pybase.configuration.ConfigResolver
   :members:
   :undoc-members:
   :show-inheritance:

ConfigSource
~~~~~~~~~~~~

.. autoclass:: buvis.pybase.configuration.ConfigSource
   :members:
   :undoc-members:
   :show-inheritance:

Mixins
------

SafeLoggingMixin
~~~~~~~~~~~~~~~~

.. autoclass:: buvis.pybase.configuration.SafeLoggingMixin
   :members:
   :undoc-members:
   :show-inheritance:

SecureSettingsMixin
~~~~~~~~~~~~~~~~~~~

.. autoclass:: buvis.pybase.configuration.SecureSettingsMixin
   :members:
   :undoc-members:
   :show-inheritance:

Click Integration
-----------------

.. autofunction:: buvis.pybase.configuration.buvis_options

.. autofunction:: buvis.pybase.configuration.get_settings

Exceptions
----------

.. autoexception:: buvis.pybase.configuration.ConfigurationError
   :members:
   :show-inheritance:

.. autoexception:: buvis.pybase.configuration.ConfigurationKeyNotFoundError
   :members:
   :show-inheritance:

.. autoexception:: buvis.pybase.configuration.MissingEnvVarError
   :members:
   :show-inheritance:

Validators
----------

.. autofunction:: buvis.pybase.configuration.validate_env_var_name

.. autofunction:: buvis.pybase.configuration.assert_valid_env_var_name

.. autofunction:: buvis.pybase.configuration.validate_tool_name

.. autofunction:: buvis.pybase.configuration.validate_nesting_depth

.. autofunction:: buvis.pybase.configuration.validate_json_env_size

.. autofunction:: buvis.pybase.configuration.get_model_depth

.. autofunction:: buvis.pybase.configuration.is_sensitive_field

Factory Functions
-----------------

.. autofunction:: buvis.pybase.configuration.create_tool_settings_class

Constants
---------

.. autodata:: buvis.pybase.configuration.MAX_NESTING_DEPTH

.. autodata:: buvis.pybase.configuration.MAX_JSON_ENV_SIZE

.. autodata:: buvis.pybase.configuration.cfg
