# PRD-00002: YAML File Discovery

## Problem

Users shouldn't specify exact config paths. BUVIS needs automatic discovery following XDG conventions and supporting project-local overrides.

## Solution

Search 4 locations in priority order, return all existing files for merge.

## Search Order (first has highest priority for override)

```
1. $BUVIS_CONFIG_DIR/buvis.yaml       # Explicit override
2. $XDG_CONFIG_HOME/buvis/buvis.yaml  # XDG standard (~/.config/buvis/)
3. ~/.buvis/buvis.yaml                # Legacy home directory
4. ./buvis.yaml                       # Project-local
```

Tool-specific files searched in parallel:
```
buvis-{tool}.yaml  # e.g., buvis-payroll.yaml
```

## Implementation

```
src/buvis/pybase/configuration/loader.py
```

```python
from pathlib import Path
import os

class ConfigurationLoader:
    @staticmethod
    def find_config_files(tool_name: str | None = None) -> list[Path]:
        """Return existing config files in priority order."""
        candidates: list[Path] = []

        # Build search paths
        paths = []
        if env_dir := os.getenv("BUVIS_CONFIG_DIR"):
            paths.append(Path(env_dir).expanduser())

        xdg = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser() / "buvis"
        paths.append(xdg)
        paths.append(Path.home() / ".buvis")
        paths.append(Path.cwd())

        # Check each path for base and tool-specific configs
        for base in paths:
            candidates.append(base / "buvis.yaml")
            if tool_name:
                candidates.append(base / f"buvis-{tool_name}.yaml")

        return [p for p in candidates if p.is_file()]
```

## Security Constraints

- **Validate paths**: Reject symlinks pointing outside expected directories (prevent symlink attacks)
- **No world-writable**: Warn or fail if config file is world-writable
- **Resolve before read**: Use `.resolve()` to canonicalize paths before operations

## Anti-patterns

- Don't follow symlinks blindly - resolve and verify target
- Don't search parent directories recursively (security risk)
- Don't cache paths across process invocations (stale)

## Edge Cases

- Empty BUVIS_CONFIG_DIR: treat as unset
- XDG_CONFIG_HOME empty string: use default ~/.config
- No files exist: return empty list (use defaults)
- Permission denied: skip file, continue search

## Tests

1. XDG_CONFIG_HOME set, file exists -> returned
2. No files anywhere -> empty list
3. Multiple files exist -> all returned in order
4. BUVIS_CONFIG_DIR overrides XDG
5. Tool-specific files included when tool_name provided
