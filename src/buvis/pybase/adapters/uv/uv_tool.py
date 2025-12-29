import shutil
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
    def run(cls, script_path: str, args: list[str]) -> None:
        """Run a tool via its installed uv tool command."""
        UvAdapter.ensure_uv()
        script_file = Path(script_path)
        tool_cmd = script_file.stem

        if shutil.which(tool_cmd):
            result = subprocess.run(  # noqa: S603, S607 - tool command is trusted
                [tool_cmd, *args],
                check=False,
            )
            sys.exit(result.returncode)

        # Tool not installed - try to install it first
        pkg_name = tool_cmd.replace("-", "_")
        scripts_root = script_file.parent.parent
        project_dir = scripts_root / "src" / pkg_name

        if project_dir.exists() and (project_dir / "pyproject.toml").exists():
            cls.install_tool(project_dir)
            result = subprocess.run(  # noqa: S603, S607
                [tool_cmd, *args],
                check=False,
            )
            sys.exit(result.returncode)

        print(
            f"Tool '{tool_cmd}' not found and no project to install from.",
            file=sys.stderr,
        )
        sys.exit(1)
