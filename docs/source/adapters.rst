Adapters
========

The adapters module wraps external tools and APIs behind consistent Python interfaces.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

- Wrap subprocess calls, COM automation, or REST APIs.
- Return tuple[str, str] as (stderr, stdout) for shell operations.
- Handle platform-specific differences internally.
- Log operations via the standard logging module.

Return Convention
~~~~~~~~~~~~~~~~~

.. code-block:: python

    stderr, stdout = adapter.exe("command", working_dir)
    if stderr:
        # Handle error
    # Process stdout

API Reference
-------------

ShellAdapter
~~~~~~~~~~~~
Subprocess execution with alias and environment variable expansion.

.. autoclass:: buvis.pybase.adapters.ShellAdapter
   :members:
   :undoc-members:
   :show-inheritance:

ConsoleAdapter
~~~~~~~~~~~~~~~
Rich console output wrapper for styled terminal messages.

.. autoclass:: buvis.pybase.adapters.console.console.ConsoleAdapter
   :members:
   :undoc-members:
   :show-inheritance:

`console` singleton instance exposes the adapter for quick access.

.. autofunction:: buvis.pybase.adapters.logging_to_console

UvAdapter
~~~~~~~~~
Fast Python package manager integration with auto-installation.

.. autoclass:: buvis.pybase.adapters.UvAdapter
   :members:
   :undoc-members:
   :show-inheritance:

UvToolManager
~~~~~~~~~~~~~
Manage and run CLI tools installed via uv.

.. autoclass:: buvis.pybase.adapters.UvToolManager
   :members:
   :undoc-members:
   :show-inheritance:

PoetryAdapter
~~~~~~~~~~~~~
Poetry project management for legacy projects.

.. autoclass:: buvis.pybase.adapters.PoetryAdapter
   :members:
   :undoc-members:
   :show-inheritance:

JiraAdapter
~~~~~~~~~~~
JIRA REST API adapter for issue creation.

.. autoclass:: buvis.pybase.adapters.JiraAdapter
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: buvis.pybase.adapters.jira.domain.JiraIssueDTO
   :members:
   :undoc-members:
   :show-inheritance:

Platform-Specific Adapters
~~~~~~~~~~~~~~~~~~~~~~~~~~

OutlookLocalAdapter
^^^^^^^^^^^^^^^^^^^

Windows-only adapter for local Outlook COM automation. Requires ``pywin32``
and a local Outlook installation. Only available when ``os.name == "nt"``.

.. code-block:: python

    # Windows only
    from buvis.pybase.adapters import OutlookLocalAdapter

    adapter = OutlookLocalAdapter()
    adapter.create_appointment(subject="Meeting", start=dt, end=dt)
