# Versioning

Uses [PEP 440](https://packaging.python.org/en/latest/discussions/versioning/) compliant versions.

`bmv` is a wrapper script at `dev/bin/bmv`.

## Format

`MAJOR.MINOR.PATCH[.devN|rcN]`

Examples: `0.5.7`, `0.5.8.dev0`, `0.5.8rc1`

## Direct Release

Default workflow - bumps go straight to final version:

```bash
bmv bump patch   # 0.5.7 → 0.5.8
bmv bump minor   # 0.5.7 → 0.6.0
bmv bump major   # 0.5.7 → 1.0.0
```

## Pre-release Workflow

For staged releases needing dev/rc phases:

```bash
# Start pre-release
bmv bump pre_patch   # 0.5.7 → 0.5.8.dev0
bmv bump pre_minor   # 0.5.7 → 0.6.0.dev0
bmv bump pre_major   # 0.5.7 → 1.0.0.dev0

# Advance stages
bmv bump pre_l       # 0.5.8.dev0 → 0.5.8rc0
bmv bump pre_l       # 0.5.8rc0 → 0.5.8

# Escape to final (skip remaining stages)
bmv bump --new-version "0.5.8"
```

## Tagging

Pre-releases (`dev`, `rc`) don't create git tags. Only final releases are tagged.

| Command | Tags? |
|---------|-------|
| `pre_minor/major/patch` | No |
| `pre_l` (dev→rc) | No |
| `pre_l` (rc→final) | Yes |
| `pre_n` | No |
| `patch/minor/major` | Yes |

## CI Behavior

| Trigger | Destination |
|---------|-------------|
| Push to master with version change | test.pypi.org |
| Push `v*` tag | pypi.org + GitHub Release |

Tags with `rc` → marked as prerelease on GitHub.

## Useful Commands

```bash
bmv show-bump                    # Show available bumps
bmv show current_version         # Current version
bmv bump --dry-run patch         # Preview change
```
