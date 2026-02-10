# Reusing the Release TUI in Other Projects

The `dev/bin/release` script is portable. Here's how to deploy it elsewhere.

## Prerequisites

- [mise](https://mise.jdx.dev/) for tool management
- `gh` CLI authenticated with your GitHub account
- A `workflow_dispatch` release workflow in the target repo

## Steps

1. Copy `dev/bin/release` to the target project's `dev/bin/`
2. Make it executable: `chmod +x dev/bin/release`
3. Add `gum = "latest"` to the target's `mise.toml` under `[tools]`
4. Ensure `_.path = ["./dev/bin"]` exists in `mise.toml` under `[env]`
5. If the workflow filename differs from `release.yml`, update the `WORKFLOW` variable at the top of the script
6. Run `mise install` to install gum
