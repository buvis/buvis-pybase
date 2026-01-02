# PRD-00005: Nested ENV Variables (Double Underscore)

## Problem

Flat env var names can't represent nested config structures. `BUVIS_PAYROLL_DATABASE_POOL_MIN_SIZE` is ambiguous - is it `database_pool.min_size` or `database.pool_min_size`?

## Solution

Double underscore `__` marks nesting boundaries. Single `_` separates words within a level.

## Rules

```
Single _  = word separator within one level
Double __ = descent into nested model
```

## Examples

| YAML Path | ENV Variable | Explanation |
|-----------|--------------|-------------|
| `payroll.database.url` | `BUVIS_PAYROLL_DATABASE_URL` | No nesting into `url` (it's a scalar) |
| `payroll.database.pool.min_size` | `BUVIS_PAYROLL_DATABASE_POOL__MIN_SIZE` | `__` before `MIN_SIZE` because `pool` is a nested model |
| `payroll.database.pool.max_size` | `BUVIS_PAYROLL_DATABASE_POOL__MAX_SIZE` | Same - field inside nested `pool` model |

## Visual Breakdown

```
BUVIS_PAYROLL_DATABASE_POOL__MIN_SIZE
     │       │        │    │   └── field in nested model
     │       │        │    └── nesting delimiter
     │       │        └── nested model name
     │       └── section
     └── tool
```

## Implementation

```python
class PoolSettings(BaseModel):
    min_size: int = 5
    max_size: int = 20

class DatabaseSettings(BaseModel):
    url: str = ""
    pool: PoolSettings = Field(default_factory=PoolSettings)

class PayrollSettings(BaseSettings):
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    model_config = SettingsConfigDict(
        env_prefix="BUVIS_PAYROLL_",
        env_nested_delimiter="__",  # This enables the __ behavior
    )
```

## When NOT to Use `__`

```bash
# CORRECT - url is a direct field, not a nested model
BUVIS_PAYROLL_DATABASE_URL=postgresql://localhost/db

# WRONG - url is not inside a nested model
BUVIS_PAYROLL_DATABASE__URL=postgresql://localhost/db
```

## Security Constraints

- **Validate depth**: Reject unreasonably deep nesting (>5 levels)
- **No injection via nesting**: Field names from env vars must match model fields exactly

## Anti-patterns

- Don't use `__` for word separation (that's what `_` is for)
- Don't use `__` for top-level fields (no nesting)
- Don't guess - look at the Pydantic model to know if field is nested

## Tests

1. `BUVIS_PAYROLL_DATABASE_POOL__MIN_SIZE=10` -> `settings.payroll.database.pool.min_size == 10`
2. `BUVIS_PAYROLL_DATABASE_URL=foo` -> `settings.payroll.database.url == "foo"`
3. `BUVIS_PAYROLL_DATABASE__URL=foo` -> ignored (no such nesting)
4. Mixed: `POOL__IDLE_TIMEOUT` correctly parses both nesting and underscore word sep
