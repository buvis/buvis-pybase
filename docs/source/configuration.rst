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

Define a tool-specific settings class that inherits from ``GlobalSettings`` and
register it with the Click decorator:

.. code-block:: python

    from typing import Literal
    import click
    from buvis.pybase.configuration import (
        buvis_options,
        get_settings,
        GlobalSettings,
        ToolSettings,
    )
    from pydantic_settings import SettingsConfigDict

    class MusicSettings(ToolSettings):
        normalize: bool = True
        bitrate: int = 320

    class PhotoSettings(GlobalSettings):
        model_config = SettingsConfigDict(
            env_prefix="BUVIS_PHOTO_",
            env_nested_delimiter="__",
        )
        watermark: bool = False
        default_album: str = "camera-roll"
        resolution: Literal["low", "medium", "high"] = "high"
        music: MusicSettings = MusicSettings()

    @click.command()
    @buvis_options(settings_class=PhotoSettings)
    @click.pass_context
    def main(ctx: click.Context) -> None:
        photo_settings = get_settings(ctx, PhotoSettings)
        if photo_settings.watermark:
            click.echo("Watermark enabled")
        click.echo(f"Saving to {photo_settings.default_album} at {photo_settings.resolution} quality")

    if __name__ == "__main__":
        main()

This automatically adds ``--debug``, ``--log-level``, ``--config-dir``, and
``--config`` options, then resolves ``PhotoSettings`` from CLI, environment, and
YAML files. The ``get_settings(ctx, PhotoSettings)`` call returns the typed
settings you registered with ``buvis_options(settings_class=PhotoSettings)``.
Using ``@buvis_options`` without arguments resolves ``GlobalSettings``; retrieve
it with ``get_settings(ctx)`` for backward compatibility.

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
    photo:
      watermark: true
      default_album: shared
    music:
      normalize: true
      bitrate: 320

Environment Variable Substitution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

YAML files support environment variable interpolation:

.. code-block:: yaml

    database:
      host: ${DB_HOST}                    # Required - fails if not set
      port: ${DB_PORT:-5432}              # Optional with default
      password: ${DB_PASSWORD}
      connection_string: $${NOT_EXPANDED} # Escaped - becomes literal ${NOT_EXPANDED}

Substitution is applied automatically by ``ConfigResolver`` when it loads YAML:

.. code-block:: python

    from buvis.pybase.configuration import ConfigResolver
    from myapp.settings import PhotoSettings

    resolver = ConfigResolver()
    settings = resolver.resolve(PhotoSettings)

Environment Variables
---------------------

The ``GlobalSettings`` base class uses the ``BUVIS_`` prefix in
SCREAMING_SNAKE_CASE. Override ``env_prefix`` on your settings class (as shown
in ``PhotoSettings`` above) to scope variables per tool:

.. code-block:: bash

    export BUVIS_PHOTO_DEBUG=true
    export BUVIS_PHOTO_LOG_LEVEL=DEBUG
    export BUVIS_PHOTO_OUTPUT_FORMAT=json

For nested fields, use double underscores:

.. code-block:: bash

    export BUVIS_PHOTO__MUSIC__NORMALIZE=true
    export BUVIS_PHOTO__MUSIC__BITRATE=256

Custom Settings Classes
-----------------------

Model tool namespaces with ``ToolSettings`` and compose them into your root
``GlobalSettings`` subclass:

.. code-block:: python

    from typing import Literal
    from buvis.pybase.configuration import GlobalSettings, ToolSettings
    from pydantic_settings import SettingsConfigDict

    class MusicSettings(ToolSettings):
        normalize: bool = True
        bitrate: int = 320

    class PhotoSettings(GlobalSettings):
        model_config = SettingsConfigDict(
            env_prefix="BUVIS_PHOTO_",
            env_nested_delimiter="__",
        )
        resolution: Literal["low", "medium", "high"] = "high"
        watermark: bool = False
        music: MusicSettings = MusicSettings()

Nested environment variables map to these namespaces (for example,
``BUVIS_PHOTO__RESOLUTION=medium`` or ``BUVIS_PHOTO__MUSIC__BITRATE=256``).

Using ConfigResolver Directly
-----------------------------

For non-Click applications or custom resolution:

.. code-block:: python

    from buvis.pybase.configuration import ConfigResolver
    from myapp.settings import PhotoSettings

    resolver = ConfigResolver()
    settings = resolver.resolve(
        PhotoSettings,
        cli_overrides={"debug": True},  # Simulate CLI args
    )

    # Check where each value came from
    print(resolver.sources)  # {"debug": ConfigSource.CLI, "log_level": ConfigSource.DEFAULT}

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
    )
    from myapp.settings import PhotoSettings

    try:
        resolver = ConfigResolver()
        settings = resolver.resolve(PhotoSettings)
    except MissingEnvVarError as e:
        print(f"Missing required env vars: {e.var_names}")
    except ConfigurationError as e:
        print(f"Config error: {e}")

--------------

API Reference
=============

Core Classes
------------

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

.. autofunction:: buvis.pybase.configuration.validate_nesting_depth

.. autofunction:: buvis.pybase.configuration.validate_json_env_size

.. autofunction:: buvis.pybase.configuration.get_model_depth

.. autofunction:: buvis.pybase.configuration.is_sensitive_field

Constants
---------

.. autodata:: buvis.pybase.configuration.MAX_NESTING_DEPTH

.. autodata:: buvis.pybase.configuration.MAX_JSON_ENV_SIZE
