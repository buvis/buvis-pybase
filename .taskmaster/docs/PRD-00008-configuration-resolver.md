# PRD-00008: Configuration Resolver

## Problem

Loading config requires orchestrating file discovery, YAML parsing, ENV loading, and CLI overrides. Each tool shouldn't reimplement this.

## Solution

Single `ConfigResolver` class that handles everything. One method call returns validated settings.

## API

```python
from buvis.pybase.configuration import ConfigResolver

# Simple usage
resolver = ConfigResolver()
settings = resolver.resolve()

# With tool-specific config
resolver = ConfigResolver(tool_name="payroll")
settings = resolver.resolve()

# With CLI overrides from Click
resolver = ConfigResolver()
settings = resolver.resolve(cli_overrides={"debug": True, "log_level": "DEBUG"})

# With custom config directory
settings = resolver.resolve(config_dir="/etc/buvis")
```

## Implementation

```python
class ConfigResolver:
    def __init__(self, tool_name: str | None = None) -> None:
        self.tool_name = tool_name
        self.loader = ConfigurationLoader()

    def resolve(
        self,
        config_dir: str | None = None,
        cli_overrides: dict[str, Any] | None = None,
    ) -> GlobalSettings:
        """Load configuration with precedence: CLI > ENV > YAML > Defaults."""

        # Set config dir override if provided
        if config_dir:
            os.environ["BUVIS_CONFIG_DIR"] = config_dir

        # Find and load YAML files
        yaml_files = self.loader.find_config_files(tool_name=self.tool_name)
        merged_yaml: dict[str, Any] = {}
        for path in yaml_files:
            file_config = self.loader.load_yaml(path)
            merged_yaml = self.loader.merge_configs(merged_yaml, file_config)

        # Create settings (YAML as base, Pydantic loads ENV)
        settings = GlobalSettings(**merged_yaml)

        # Apply CLI overrides
        if cli_overrides:
            for key, value in cli_overrides.items():
                if value is not None and hasattr(settings, key):
                    setattr(settings, key, value)

        return settings
```

## Error Handling

| Error | Behavior |
|-------|----------|
| YAML syntax error | Raise with file path and line number |
| Missing required env var | Raise with var name |
| Type validation failure | Raise with field path and expected type |
| Permission denied on file | Skip file, continue loading |

```python
try:
    settings = resolver.resolve()
except ConfigurationError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)
```

## Security Constraints

- **Single load point**: All config flows through resolver (auditable)
- **Fail fast**: Validate immediately, don't defer to use time
- **No reload**: Settings immutable after resolve() returns
- **Mask secrets in errors**: Don't include secret values in error messages

## Anti-patterns

- Don't call resolve() multiple times per process
- Don't modify settings after resolution
- Don't bypass resolver to load config directly

## Tests

1. No config files -> defaults only
2. YAML exists -> values loaded
3. YAML + ENV -> ENV overrides YAML
4. YAML + ENV + CLI -> CLI overrides all
5. Tool-specific YAML merged on top of base
6. Invalid YAML -> clear error with file path
7. Missing required field -> ValidationError
