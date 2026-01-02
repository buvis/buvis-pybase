# PRD-00001: Pydantic Settings Base Models

## Problem

BUVIS tools lack unified, type-safe configuration. Ad-hoc loading causes runtime errors, inconsistent behavior, and debugging waste.

## Solution

Pydantic v2 BaseSettings models with strict typing, validation at startup, and nested tool namespaces.

## Requirements

### Global Settings
- `debug: bool = False` - Debug mode toggle
- `log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"`
- `output_format: Literal["text", "json", "yaml"] = "text"`

### Tool Namespaces
- Each tool gets a nested model: `settings.payroll`, `settings.hcm`
- Tool models inherit from `BaseModel` (not `BaseSettings` - parent handles ENV)
- Each tool has `enabled: bool = True`

## Implementation

```
src/buvis/pybase/configuration/settings.py
```

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class ToolSettings(BaseModel):
    """Base for tool-specific settings."""
    enabled: bool = True

class GlobalSettings(BaseSettings):
    debug: bool = False
    log_level: str = "INFO"
    # Tool namespaces added by consumers

    model_config = SettingsConfigDict(
        env_prefix="BUVIS_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )
```

## Security Constraints

- **No secrets in defaults**: Never put API keys, passwords, or tokens as field defaults
- **Validate early**: All settings validated at startup, not at use time
- **Immutable after load**: Settings should not be modified after initial resolution

## Anti-patterns

- Don't use `Optional[str]` for required secrets - use validators that fail if empty
- Don't log full settings objects (may contain secrets)
- Don't use `extra="allow"` - reject unknown fields

## Dependencies

- `pydantic>=2.0`
- `pydantic-settings>=2.0`

## Tests

1. Instantiate with no args, verify defaults
2. Invalid log_level raises ValidationError
3. Nested tool access works: `settings.payroll.enabled`
4. Unknown field rejected with clear error
