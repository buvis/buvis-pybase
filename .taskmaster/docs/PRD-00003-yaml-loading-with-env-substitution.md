# PRD-00003: YAML Loading with ENV Substitution

## Problem

Config files need to reference secrets without storing them in plain text. Users want `${DB_PASSWORD}` syntax to inject runtime values.

## Solution

Load YAML with safe_load only. Substitute `${VAR}` patterns before parsing. Deep merge multiple configs.

## Substitution Syntax

```yaml
database:
  password: "${DB_PASSWORD}"           # Required - fails if unset
  host: "${DB_HOST:-localhost}"        # With default
  port: "${DB_PORT:-5432}"
```

## Implementation

```
src/buvis/pybase/configuration/loader.py
```

```python
import re
import yaml

_ENV_PATTERN = re.compile(r'\$\{([^}:]+)(?::-([^}]*))?\}')

class ConfigurationLoader:
    @staticmethod
    def load_yaml(file_path: Path) -> dict[str, Any]:
        """Load YAML with env substitution. Raises on missing required vars."""
        content = file_path.read_text(encoding="utf-8")

        missing = []
        def substitute(match: re.Match) -> str:
            var_name, default = match.group(1), match.group(2)
            value = os.environ.get(var_name)
            if value is None:
                if default is not None:
                    return default
                missing.append(var_name)
                return match.group(0)  # Keep original for error message
            return value

        content = _ENV_PATTERN.sub(substitute, content)

        if missing:
            raise ValueError(f"Missing required env vars: {', '.join(missing)}")

        return yaml.safe_load(content) or {}

    @staticmethod
    def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
        """Deep merge dicts. Later values override earlier."""
        result: dict[str, Any] = {}
        for cfg in configs:
            _deep_merge(result, cfg)
        return result

def _deep_merge(target: dict, source: dict) -> None:
    for k, v in source.items():
        if k in target and isinstance(target[k], dict) and isinstance(v, dict):
            _deep_merge(target[k], v)
        else:
            target[k] = v
```

## Security Constraints

- **safe_load only**: Never use yaml.load() or yaml.unsafe_load()
- **Fail on missing**: Required env vars must fail loudly, not silently default
- **No recursive substitution**: Don't re-substitute values from env vars (prevents injection)
- **Escape syntax**: Support `$${VAR}` for literal `${VAR}` in output

## Anti-patterns

- Don't use yaml.load() with Loader - always safe_load()
- Don't substitute after parsing (values already typed)
- Don't allow env vars to contain YAML syntax (injection risk)
- Don't log substituted content (may contain secrets)

## Edge Cases

- Empty file: return `{}`
- Invalid YAML: raise yaml.YAMLError with line number
- Env var value contains `${`: no recursive substitution
- Circular defaults: not supported, fail clearly

## Tests

1. `${VAR}` with VAR set -> substituted
2. `${VAR}` with VAR unset -> ValueError with var name
3. `${VAR:-default}` with VAR unset -> uses default
4. `$${VAR}` -> literal `${VAR}` in output
5. Empty file -> `{}`
6. Invalid YAML -> yaml.YAMLError
7. Merge two dicts with nested overlap -> deep merged
