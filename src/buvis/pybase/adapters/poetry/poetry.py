import importlib
import subprocess
import sys
from pathlib import Path


class PoetryAdapter:
    """Poetry virtual environment and script management.

    Discovers and runs scripts using their associated Poetry projects,
    with fallback to direct module import.

    Expected directory structure::

        scripts_root/
        ├── bin/
        │   └── my-tool         # Launcher script
        └── src/
            └── my_tool/        # Project directory
                ├── pyproject.toml
                └── my_tool/
                    └── cli.py  # Module with main()
    """

    @classmethod
    def run_script(cls, script_path: str, args: list[str]) -> None:
        """Run a script using its Poetry virtual environment.

        Discovery logic:
            1. Derive package name from script: my-tool -> my_tool
            2. Look for src/{pkg}/pyproject.toml relative to script parent
            3. If found: run via poetry run python -m {pkg}.cli
            4. If not found: import {pkg}.cli and call main(args)

        Args:
            script_path: Path to the launcher script in bin/.
            args: Arguments to pass to the script main().

        Note:
            Exits with Poetry return code when running via Poetry.
        """
        script_file = Path(script_path)
        pkg_name = script_file.stem.replace("-", "_")
        scripts_root = script_file.parent.parent
        project_dir = scripts_root / "src" / pkg_name

        if project_dir.exists() and (project_dir / "pyproject.toml").exists():
            cmd = ["poetry", "run", "python", "-m", f"{pkg_name}.cli", *args]
            result = subprocess.run(cmd, cwd=project_dir, check=False)
            sys.exit(result.returncode)
        else:
            launcher_module = importlib.import_module(f"{pkg_name}.cli")
            launcher_module.main(args)

    @classmethod
    def update_script(cls, script_path: str) -> None:
        """Update dependencies for a script's project."""
        script_file = Path(script_path)
        pkg_name = script_file.stem.replace("-", "_")
        scripts_root = script_file.parent.parent
        project_dir = scripts_root / "src" / pkg_name

        if project_dir.exists() and (project_dir / "pyproject.toml").exists():
            cls._update_poetry_project(project_dir)

    @classmethod
    def update_all_scripts(cls, scripts_root: Path | None = None) -> None:
        """Update all scripts in bin/ and all Poetry projects in src/."""
        if scripts_root is None:
            scripts_root = Path.cwd()

        bin_directory = scripts_root / "bin"
        if bin_directory.exists():
            for file_path in bin_directory.iterdir():
                if file_path.is_file() and cls._contains_poetry_adapter(file_path):
                    cls.update_script(str(file_path))

        src_directory = scripts_root / "src"
        if src_directory.exists():
            for project_dir in src_directory.iterdir():
                if project_dir.is_dir() and (project_dir / "pyproject.toml").exists():
                    cls._update_poetry_project(project_dir)

    @staticmethod
    def _contains_poetry_adapter(file_path: Path) -> bool:
        try:
            return (
                "from buvis.pybase.adapters import PoetryAdapter"
                in file_path.read_text(encoding="utf-8")
            )
        except UnicodeDecodeError:
            return False

    @staticmethod
    def _update_poetry_project(project_path: Path) -> None:
        """Update dependencies for a Poetry project."""
        try:
            lock_file = project_path / "poetry.lock"
            if lock_file.exists():
                lock_file.unlink()

            subprocess.run(
                ["poetry", "lock"],
                cwd=project_path,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["poetry", "install"],
                cwd=project_path,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            pass
