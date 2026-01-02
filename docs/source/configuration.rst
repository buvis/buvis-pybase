Configuration
=============

This module provides unified configuration management for BUVIS tools with
automatic precedence handling across multiple sources.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

The configuration system loads settings from multiple sources with clear
precedence rules:

1. **CLI arguments** (highest priority)
2. **Environment variables** (``BUVIS_*`` prefix)
3. **YAML config files** (auto-discovered)
4. **Model defaults** (lowest priority)

This means a ``--debug`` flag always wins over ``BUVIS_DEBUG=false`` in the
environment, which wins over ``debug: false`` in a YAML file.

Quick Start
-----------

For Click-based CLI tools, use the ``buvis_options`` decorator:

.. code-block:: python

    import click
    from buvis.pybase.configuration import get_settings, buvis_options

    @click.command()
    @buvis_options
    @click.pass_context
    def main(ctx):
        settings = get_settings(ctx)
        if settings.debug:
            click.echo("Debug mode enabled")
        click.echo(f"Log level: {settings.log_level}")

    if __name__ == "__main__":
        main()

This automatically adds ``--debug``, ``--log-level``, ``--config-dir``, and
``--config`` options to your CLI.

YAML Configuration
------------------

File Locations
~~~~~~~~~~~~~~

Config files are discovered in order (first found wins):

1. ``$BUVIS_CONFIG_DIR/buvis.yaml`` (if env var set)
2. ``$XDG_CONFIG_HOME/buvis/buvis.yaml`` (or ``~/.config/buvis/buvis.yaml``)
3. ``~/.buvis/buvis.yaml`` (legacy)
4. ``./buvis.yaml`` (current directory)

For tool-specific config, files named ``buvis-{tool}.yaml`` are also checked.

File Format
~~~~~~~~~~~

.. code-block:: yaml

    # ~/.config/buvis/buvis.yaml
    debug: false
    log_level: INFO
    output_format: text

    # Tool-specific sections
    payroll:
      enabled: true
      batch_size: 1000

Environment Variable Substitution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

YAML files support environment variable interpolation:

.. code-block:: yaml

    database:
      host: ${DB_HOST}                    # Required - fails if not set
      port: ${DB_PORT:-5432}              # Optional with default
      password: ${DB_PASSWORD}
      connection_string: $${NOT_EXPANDED} # Escaped - becomes literal ${NOT_EXPANDED}

To enable substitution, initialize with ``enable_env_substitution=True``:

.. code-block:: python

    from buvis.pybase.configuration import Configuration

    cfg = Configuration(enable_env_substitution=True)

Environment Variables
---------------------

All environment variables use the ``BUVIS_`` prefix in SCREAMING_SNAKE_CASE:

.. code-block:: bash

    export BUVIS_DEBUG=true
    export BUVIS_LOG_LEVEL=DEBUG
    export BUVIS_OUTPUT_FORMAT=json

For nested settings, use double underscore as delimiter:

.. code-block:: bash

    export BUVIS_PAYROLL__ENABLED=true
    export BUVIS_PAYROLL__BATCH_SIZE=500

Custom Settings Classes
-----------------------

Extend ``GlobalSettings`` for tool-specific configuration:

.. code-block:: python

    from typing import Literal
    from buvis.pybase.configuration import GlobalSettings, ToolSettings

    class PayrollSettings(ToolSettings):
        batch_size: int = 1000
        output_dir: str = "/tmp/payroll"

    class MyToolSettings(GlobalSettings):
        payroll: PayrollSettings = PayrollSettings()

Or use the factory for simple cases:

.. code-block:: python

    from buvis.pybase.configuration import create_tool_settings_class

    PayrollSettings = create_tool_settings_class(
        "PAYROLL",
        batch_size=(int, 1000),
        output_dir=(str, "/tmp/payroll"),
    )

    # Reads from BUVIS_PAYROLL_BATCH_SIZE, BUVIS_PAYROLL_OUTPUT_DIR
    settings = PayrollSettings()

Using ConfigResolver Directly
-----------------------------

For non-Click applications or custom resolution:

.. code-block:: python

    from buvis.pybase.configuration import ConfigResolver, GlobalSettings

    resolver = ConfigResolver(tool_name="mytool")
    settings = resolver.resolve(
        GlobalSettings,
        cli_overrides={"debug": True},  # Simulate CLI args
    )

    # Check where each value came from
    print(resolver.sources)  # {"debug": ConfigSource.CLI, "log_level": ConfigSource.DEFAULT}

Configuration Class
-------------------

The ``Configuration`` class provides dict-style access for simple scripts:

.. code-block:: python

    from buvis.pybase.configuration import Configuration

    config = Configuration()  # Auto-discovers config file

    # Get values
    hostname = config.get_configuration_item("hostname")
    timeout = config.get_configuration_item_or_default("timeout", 30)

    # Set values at runtime
    config.set_configuration_item("custom_key", "value")

.. note::

    The ``Configuration`` class doesn't support precedence handling.
    Use ``ConfigResolver`` with ``get_settings()`` for CLI tools.

Migration from cfg Singleton
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If migrating from the legacy ``cfg`` singleton:

.. code-block:: python

    # Old
    from buvis.pybase.configuration import cfg
    value = cfg.get_configuration_item("key")

    # New
    from buvis.pybase.configuration import Configuration
    config = Configuration()
    value = config.get_configuration_item("key")

Security Considerations
-----------------------

Sensitive Fields
~~~~~~~~~~~~~~~~

Fields matching patterns like ``password``, ``token``, ``api_key``, ``secret``
are automatically:

- Masked in ``__repr__`` output (shows ``***``)
- Logged at INFO level (vs DEBUG for normal fields)
- Hidden in validation error messages

.. code-block:: python

    from buvis.pybase.configuration import SafeLoggingMixin
    from pydantic_settings import BaseSettings

    class SecureSettings(SafeLoggingMixin, BaseSettings):
        api_key: str
        password: str

    s = SecureSettings(api_key="secret123", password="hunter2")
    print(s)  # SecureSettings(api_key='***', password='***')

JSON Size Limits
~~~~~~~~~~~~~~~~

Environment variables containing JSON are limited to 64KB to prevent DoS:

.. code-block:: python

    from buvis.pybase.configuration import SecureSettingsMixin
    from pydantic_settings import BaseSettings

    class MySettings(SecureSettingsMixin, BaseSettings):
        model_config = {"env_prefix": "MYAPP_"}
        complex_config: dict = {}

    # Raises ValueError if MYAPP_COMPLEX_CONFIG exceeds 64KB

Error Handling
--------------

.. code-block:: python

    from buvis.pybase.configuration import (
        ConfigResolver,
        ConfigurationError,
        MissingEnvVarError,
        GlobalSettings,
    )

    try:
        resolver = ConfigResolver()
        settings = resolver.resolve(GlobalSettings)
    except MissingEnvVarError as e:
        print(f"Missing required env vars: {e.var_names}")
    except ConfigurationError as e:
        print(f"Config error: {e}")

--------------

API Reference
=============

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
