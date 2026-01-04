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
