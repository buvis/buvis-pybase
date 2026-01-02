# PRD-00009: Click CLI Integration

## Problem

BUVIS tools use Click. Each tool reinvents config loading, leading to inconsistent `--debug` and `--log-level` behavior.

## Solution

Decorators that add standard options and inject resolved settings into Click context.

## Usage

```python
import click
from buvis.pybase.configuration import buvis_options, get_settings

@click.group()
@buvis_options  # Adds --debug, --log-level, --config-dir
@click.pass_context
def cli(ctx):
    """My BUVIS tool."""
    pass

@cli.command()
@click.pass_context
def process(ctx):
    settings = get_settings(ctx)
    if settings.debug:
        click.echo("Debug mode enabled")
```

## Standard Options

| Option | Type | Default | Maps To |
|--------|------|---------|---------|
| `--debug/--no-debug` | bool | None | `settings.debug` |
| `--log-level` | str | None | `settings.log_level` |
| `--config-dir` | path | None | `BUVIS_CONFIG_DIR` |
| `--config` | path | None | Additional YAML file |

## Implementation

```python
import functools
import click

def buvis_options(f):
    """Add standard BUVIS options to a Click command."""
    @click.option("--debug/--no-debug", default=None, help="Enable debug mode")
    @click.option("--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]))
    @click.option("--config-dir", type=click.Path(exists=True), help="Config directory")
    @click.pass_context
    @functools.wraps(f)
    def wrapper(ctx, debug, log_level, config_dir, *args, **kwargs):
        cli_overrides = {
            k: v for k, v in {"debug": debug, "log_level": log_level}.items()
            if v is not None
        }
        resolver = ConfigResolver()
        settings = resolver.resolve(config_dir=config_dir, cli_overrides=cli_overrides)
        ctx.ensure_object(dict)
        ctx.obj["settings"] = settings
        return ctx.invoke(f, *args, **kwargs)
    return wrapper

def get_settings(ctx: click.Context) -> GlobalSettings:
    """Get settings from Click context."""
    return ctx.obj["settings"]
```

## Tool-Specific Options

```python
@cli.group()
@click.option("--batch-size", type=int, help="Override batch size")
@click.pass_context
def payroll(ctx, batch_size):
    """Payroll commands."""
    settings = get_settings(ctx)
    if batch_size is not None:
        settings.payroll.batch_size = batch_size
```

## Naming Convention

| Python Field | CLI Option | Reason |
|--------------|------------|--------|
| `log_level` | `--log-level` | Click uses kebab-case |
| `batch_size` | `--batch-size` | Consistent with CLI conventions |
| `debug` | `--debug` | Boolean flag |

## Security Constraints

- **Don't echo secrets**: Never print resolved settings with secrets
- **Validate paths**: `--config-dir` and `--config` must exist
- **No shell expansion**: Use Click's path handling, not manual expansion

## Anti-patterns

- Don't use `default=False` for boolean options (prevents ENV override)
- Don't duplicate standard options in tool commands
- Don't store settings in global variables (use context)

## Tests

1. `--debug` -> `settings.debug == True`
2. No `--debug` + `BUVIS_DEBUG=true` -> `settings.debug == True`
3. `--no-debug` + `BUVIS_DEBUG=true` -> `settings.debug == False` (CLI wins)
4. `--log-level=DEBUG` -> `settings.log_level == "DEBUG"`
5. `--config-dir=/etc/buvis` -> loads from that directory
6. `get_settings(ctx)` returns same object across commands
