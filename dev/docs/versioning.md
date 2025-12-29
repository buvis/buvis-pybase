# Versioning

Uses [PEP 440](https://packaging.python.org/en/latest/discussions/versioning/) compliant versions.

`bmv` is an alias for `uv run bump-my-version`.

## Format

`MAJOR.MINOR.PATCH[.devN|rcN]`

Examples: `0.5.7`, `0.5.8.dev0`, `0.5.8rc1`

Stages: `.dev` → `rc` → final (no suffix)

## Workflows

### Direct Release

For hotfixes, small patches, or confident releases:

```bash
# Get current version
bmv show current_version

# Direct patch: 0.5.7 → 0.5.8
bmv bump --new-version "0.5.8"

# Direct minor: 0.5.7 → 0.6.0
bmv bump --new-version "0.6.0"

# Direct major: 0.5.7 → 1.0.0
bmv bump --new-version "1.0.0"
```

### Pre-release Workflow

For major features or breaking changes needing staged testing:

```bash
# Start pre-release cycle: 0.5.7 → 0.5.8.dev0
bmv bump patch

# Advance to RC: 0.5.8.dev0 → 0.5.8rc0
bmv bump pre_l

# Release: 0.5.8rc0 → 0.5.8
bmv bump pre_l
```

### Escape Pre-release

Jump from any pre-release directly to final:

```bash
# From 0.5.8.dev0 or 0.5.8rc1 → 0.5.8
bmv bump --new-version "0.5.8"
```

## CI Behavior

| Trigger | Destination | Notes |
|---------|-------------|-------|
| Push to master with version change | test.pypi.org | Any version bump |
| Push `v*` tag | pypi.org + GitHub Release | Production release |

Tags containing `alpha`, `beta`, or `rc` are marked as prerelease on GitHub.

## Common Commands

```bash
# Show what bumps are available
bmv show-bump

# Dry run (see what would happen)
bmv bump --dry-run --new-version "0.5.8"
```
