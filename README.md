# buvis-pybase

Foundation of BUVIS python projects

**Type:** Library

## Dependency Strategy

- Dependencies use SemVer ranges (`>=x.y.z,<next-major`) for consumer compatibility
- `uv.lock` committed for CI/dev reproducibility (consumers ignore it)
- Renovate: `widen` for majors (manual), `update-lockfile` for minor/patch (automerge)
