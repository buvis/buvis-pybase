# buvis-pybase

Foundation library for BUVIS Python projects. Provides configuration management, filesystem utilities, adapters for external tools, and string manipulation.

## Install

```bash
pip install buvis-pybase
```

## Features

- **Configuration** - YAML-based config with singleton access (`cfg`)
- **Adapters** - Shell, UV, Poetry, JIRA, Console wrappers
- **Filesystem** - Cross-platform file metadata, directory operations
- **Formatting** - String slugify, abbreviations, case conversion

## Usage

```python
from buvis.pybase.configuration import Configuration
from buvis.pybase.adapters import ShellAdapter, ConsoleAdapter
from buvis.pybase.filesystem import DirTree
from buvis.pybase.formatting import StringOperator

# Config (reads ~/.config/buvis/config.yaml)
config = Configuration()
value = config.get_configuration_item("some.key", default="fallback")

# Shell commands
shell = ShellAdapter()
stderr, stdout = shell.exe("ls -la")

# Console output
console = ConsoleAdapter()
console.success("Done")

# Filesystem
DirTree.remove_empty_directories("/path/to/clean")

# Strings
slug = StringOperator.slugify("Hello World!")  # "hello-world"
```

## Development

```bash
uv sync --all-groups    # install deps
pre-commit install      # setup hooks
uv run pytest           # run tests
```

## Release

```bash
./dev/bin/bmv bump patch  # bumps version, tags, pushes
```

Tags trigger PyPI publish via GitHub Actions.

## License

MIT
