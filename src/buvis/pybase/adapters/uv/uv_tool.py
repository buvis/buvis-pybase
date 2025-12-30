import subprocess
import sys
from pathlib import Path

from buvis.pybase.adapters.console.console import console
from buvis.pybase.adapters.uv.uv import UvAdapter


class UvToolManager:
    @staticmethod
    def install_all(scripts_root: Path | None = None) -> None:
        """Install all projects in src/ as uv tools."""
        UvAdapter.ensure_uv()

        if scripts_root is None:
            scripts_root = Path.cwd()

        src_directory = scripts_root / "src"

        if src_directory.exists():
            for project_dir in src_directory.iterdir():
                if project_dir.is_dir() and (project_dir / "pyproject.toml").exists():
                    UvToolManager.install_tool(project_dir)

    @staticmethod
    def install_tool(project_path: Path) -> None:
        """Install a project as a uv tool."""
        pkg_name = project_path.name
        console.status(f"Installing {pkg_name} as uv tool...")

        try:
            subprocess.run(  # noqa: S603 - uv is trusted
                ["uv", "tool", "install", "--force", "--upgrade", str(project_path)],  # noqa: S607
                check=True,
                capture_output=True,
            )
            console.success(f"Installed {pkg_name}")
        except subprocess.CalledProcessError as e:
            console.failure(f"Failed to install {pkg_name}: {e}")

    @classmethod
    def run(cls, script_path: str, args: list[str] | None = None) -> None:
        """Run from local venv, project source, or installed tool."""
        UvAdapter.ensure_uv()

        if args is None:
            args = sys.argv[1:]

        script = Path(script_path).resolve()
        tool_cmd = script.stem
        pkg_name = tool_cmd.replace("-", "_")
        scripts_root = script.parent.parent
        project_dir = scripts_root / "src" / pkg_name

        cwd = Path.cwd().resolve()
        in_dev_mode = cwd == scripts_root or scripts_root in cwd.parents

        if in_dev_mode:
            venv_bin = project_dir / ".venv" / "bin" / tool_cmd

            if venv_bin.exists():
                result = subprocess.run([str(venv_bin), *args], check=False)  # noqa: S603
                sys.exit(result.returncode)

            if project_dir.exists() and (project_dir / "pyproject.toml").exists():
                result = subprocess.run(  # noqa: S603, S607
                    ["uv", "run", "--project", str(project_dir), "-m", pkg_name, *args],
                    check=False,
                )
                sys.exit(result.returncode)

            print(f"No venv or project found at {project_dir}", file=sys.stderr)
            sys.exit(1)

        result = subprocess.run(  # noqa: S603, S607
            ["uv", "tool", "run", tool_cmd, *args],
            check=False,
        )
        if result.returncode == 0:
            sys.exit(0)

        # Tool not found - try auto-install
        if project_dir.exists() and (project_dir / "pyproject.toml").exists():
            cls.install_tool(project_dir)
            result = subprocess.run(  # noqa: S603, S607
                ["uv", "tool", "run", tool_cmd, *args],
                check=False,
            )
            sys.exit(result.returncode)

        print(
            f"Tool '{tool_cmd}' not found and no project to install from.",
            file=sys.stderr,
        )
        sys.exit(1)
