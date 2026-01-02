# PRD-00004: ENV Variable Naming Convention

## Problem

Inconsistent env var names make configuration unpredictable. Users can't guess the right variable for a setting.

## Solution

Strict naming convention: `BUVIS_{TOOL}_{FIELD}` in SCREAMING_SNAKE_CASE.

## Naming Rules

| Layer | Pattern | Example |
|-------|---------|---------|
| Global | `BUVIS_{FIELD}` | `BUVIS_DEBUG`, `BUVIS_LOG_LEVEL` |
| Tool | `BUVIS_{TOOL}_{FIELD}` | `BUVIS_PAYROLL_BATCH_SIZE` |
| Nested | `BUVIS_{TOOL}_{SECTION}_{FIELD}` | `BUVIS_PAYROLL_DATABASE_URL` |

### Mapping Examples

| YAML Path | ENV Variable | Python |
|-----------|--------------|--------|
| `debug` | `BUVIS_DEBUG` | `settings.debug` |
| `log_level` | `BUVIS_LOG_LEVEL` | `settings.log_level` |
| `payroll.batch_size` | `BUVIS_PAYROLL_BATCH_SIZE` | `settings.payroll.batch_size` |
| `payroll.database.url` | `BUVIS_PAYROLL_DATABASE_URL` | `settings.payroll.database.url` |

## Implementation

Pydantic handles this via `env_prefix`:

```python
class PayrollSettings(BaseSettings):
    batch_size: int = 1000
    database_url: str = ""

    model_config = SettingsConfigDict(
        env_prefix="BUVIS_PAYROLL_",
        case_sensitive=False,
    )
```

## Security Constraints

- **Prefix required**: All BUVIS vars must start with `BUVIS_` - prevents namespace pollution
- **Case insensitive**: Accept `buvis_debug` and `BUVIS_DEBUG` (reduce user frustration)
- **No hyphens**: Env vars can't contain `-`, use `_` only

## Anti-patterns

- Don't create vars without BUVIS_ prefix
- Don't use lowercase in documentation (convention is uppercase)
- Don't abbreviate unless obvious (`DB` ok, `DTBS` not ok)

## Tests

1. `BUVIS_DEBUG=true` -> `settings.debug == True`
2. `buvis_debug=true` (lowercase) -> works
3. `DEBUG=true` (no prefix) -> ignored
4. `BUVIS_PAYROLL_BATCH_SIZE=500` -> `settings.payroll.batch_size == 500`
