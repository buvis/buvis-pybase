Filesystem
==========

Utilities for directory traversal, file metadata, and batch operations.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

`DirTree` and `FileMetadataReader` are static utility classes under
`buvis.pybase.filesystem`. Each exposes class-level helpers—no
instantiation is required—to inspect directory depth, prune files, or read
timestamps. DirTree bundles cleanup routines (counting files, normalizing
extensions, removing empty folders, and merging Mac metadata), while
FileMetadataReader surfaces creation and first-commit datetimes with
platform-aware fallbacks.

Quick Start
-----------

.. code-block:: python

    from pathlib import Path
    from buvis.pybase.filesystem import DirTree, FileMetadataReader

    project_root = Path(__file__).resolve().parent

    # Static utilities: no DirTree() or FileMetadataReader() instantiation.
    total_files = DirTree.count_files(project_root / "src")
    creation_dt = FileMetadataReader.get_creation_datetime(project_root / "pyproject.toml")
    first_commit = FileMetadataReader.get_first_commit_datetime(project_root / "pyproject.toml")

    print(total_files, creation_dt, first_commit)

API Reference
-------------

DirTree
~~~~~~~

.. autoclass:: buvis.pybase.filesystem.DirTree
   :members:
   :undoc-members:
   :show-inheritance:

FileMetadataReader
~~~~~~~~~~~~~~~~~~

.. autoclass:: buvis.pybase.filesystem.FileMetadataReader
   :members:
   :undoc-members:
   :show-inheritance:
