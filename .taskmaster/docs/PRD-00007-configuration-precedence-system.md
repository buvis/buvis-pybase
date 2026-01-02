# PRD-00007: Configuration Precedence System

## Problem

Multiple config sources create ambiguity. When YAML says `debug: false` and ENV says `BUVIS_DEBUG=true`, which wins?

## Solution

Single, absolute rule:

```
CLI > ENV > YAML > Defaults
```

Higher sources always override lower sources. No exceptions.

## Precedence Table

| Priority | Source | Example | When Used |
|----------|--------|---------|-----------|
| 1 (highest) | CLI | `--debug` | Temporary override |
| 2 | ENV | `BUVIS_DEBUG=true` | Deployment config |
| 3 | YAML | `debug: true` in buvis.yaml | Persistent config |
| 4 (lowest) | Default | `debug: bool = False` | Fallback |

## Examples

```bash
# YAML: debug: false
# ENV: BUVIS_DEBUG=true
# CLI: (not provided)
# Result: debug=true (ENV wins over YAML)

# YAML: debug: false
# ENV: BUVIS_DEBUG=true
# CLI: --no-debug
# Result: debug=false (CLI wins over everything)
```

## Implementation

```python
class ConfigResolver:
    def resolve(
        self,
        cli_overrides: dict[str, Any] | None = None,
    ) -> GlobalSettings:
        # 1. Load YAML (becomes constructor kwargs)
        yaml_config = self._load_yaml_files()

        # 2. Create settings (Pydantic applies ENV automatically)
        settings = GlobalSettings(**yaml_config)

        # 3. Apply CLI overrides (highest priority)
        if cli_overrides:
            for key, value in cli_overrides.items():
                if value is not None:
                    setattr(settings, key, value)

        return settings
```

## Why This Order

| Source | Persistence | Scope | Use Case |
|--------|-------------|-------|----------|
| Defaults | Permanent | Universal | Safe fallbacks |
| YAML | Persistent | User/project | Documented config |
| ENV | Ephemeral | Process | Deployment secrets |
| CLI | Ephemeral | Invocation | Debugging, one-offs |

## Security Constraints

- **No silent overrides**: Log which source provided each value (at DEBUG level, without values)
- **Validate all sources**: Don't trust CLI more than YAML - validate everything
- **Audit trail**: In production, log config source for security-sensitive settings

## Anti-patterns

- Don't allow YAML to override CLI (breaks mental model)
- Don't merge complex types across sources (replace, don't merge)
- Don't have "super sources" that bypass precedence

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| CLI value is None | Fall through to ENV |
| ENV value is empty string "" | Use empty string (not default) |
| YAML key absent | Use default |
| Required field missing everywhere | ValidationError at startup |

## Tests

1. Same setting in CLI, ENV, YAML, default -> CLI wins
2. Same setting in ENV, YAML, default (no CLI) -> ENV wins
3. Same setting in YAML, default (no CLI/ENV) -> YAML wins
4. Only default exists -> default used
5. CLI=None -> falls through to ENV
