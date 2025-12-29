import importlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class UvAdapter:
    @staticmethod
    def ensure_uv() -> None:
        """Ensure uv is installed and available in PATH."""
        if shutil.which("uv"):
            return

        print("uv not found. Installing...", file=sys.stderr)
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.check_call(
                    [  # noqa: S607 - trusted installer
                        "powershell",
                        "-ExecutionPolicy",
                        "ByPass",
                        "-c",
                        "irm https://astral.sh/uv/install.ps1 | iex",
                    ],
                )
                user_profile = Path(os.environ.get("USERPROFILE", ""))
                possible_paths = [
                    user_profile / ".cargo" / "bin",
                    user_profile / "AppData" / "Local" / "uv",
                ]
            else:
                subprocess.check_call(  # noqa: S602 - trusted installer
                    "curl -LsSf https://astral.sh/uv/install.sh | sh",  # noqa: S607
                    shell=True,
                )
                home = Path(os.environ.get("HOME", ""))
                possible_paths = [
                    home / ".cargo" / "bin",
                    home / ".local" / "bin",
                ]

            for p in possible_paths:
                if p.exists():
                    os.environ["PATH"] += os.pathsep + str(p)

        except subprocess.CalledProcessError as e:
            print(f"Failed to install uv: {e}", file=sys.stderr)
            sys.exit(1)

    @classmethod
    def run_script(cls, script_path: str, args: list[str]) -> None:
        """Run a script, using its own uv virtual environment if available."""
        cls.ensure_uv()
        script_file = Path(script_path)
        pkg_name = script_file.stem.replace("-", "_")
        scripts_root = script_file.parent.parent
        project_dir = scripts_root / "src" / pkg_name

        if project_dir.exists() and (project_dir / "pyproject.toml").exists():
            cmd = ["uv", "run", "python", "-m", f"{pkg_name}.cli", *args]
            env = os.environ.copy()
            env.pop("VIRTUAL_ENV", None)
            result = subprocess.run(  # noqa: S603 - uv is trusted
                cmd,
                cwd=project_dir,
                check=False,
                env=env,
            )
            sys.exit(result.returncode)
        else:
            launcher_module = importlib.import_module(f"{pkg_name}.cli")
            launcher_module.main(args)

    @classmethod
    def update_script(cls, script_path: str) -> None:
        """Update dependencies for a script's project."""
        cls.ensure_uv()
        script_file = Path(script_path)
        pkg_name = script_file.stem.replace("-", "_")
        scripts_root = script_file.parent.parent
        project_dir = scripts_root / "src" / pkg_name

        if project_dir.exists() and (project_dir / "pyproject.toml").exists():
            cls._update_uv_project(project_dir)

    @classmethod
    def update_all_scripts(cls, scripts_root: Path | None = None) -> None:
        """Update all scripts in bin/ and all uv projects in src/."""
        cls.ensure_uv()
        if scripts_root is None:
            scripts_root = Path.cwd()

        bin_directory = scripts_root / "bin"
        if bin_directory.exists():
            for file_path in bin_directory.iterdir():
                if file_path.is_file() and cls._contains_uv_adapter(file_path):
                    cls.update_script(str(file_path))

        src_directory = scripts_root / "src"
        if src_directory.exists():
            for project_dir in src_directory.iterdir():
                if project_dir.is_dir() and (project_dir / "pyproject.toml").exists():
                    cls._update_uv_project(project_dir)

    @staticmethod
    def _contains_uv_adapter(file_path: Path) -> bool:
        try:
            return "from buvis.pybase.adapters import UvAdapter" in file_path.read_text(
                encoding="utf-8",
            )
        except UnicodeDecodeError:
            return False

    @staticmethod
    def _update_uv_project(project_path: Path) -> None:
        """Update dependencies for a uv project."""
        try:
            subprocess.run(
                ["uv", "lock", "--upgrade"],  # noqa: S607
                cwd=project_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["uv", "sync"],  # noqa: S607
                cwd=project_path,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            pass
