import importlib
import runpy
import subprocess
import sys
from pathlib import Path


class PoetryAdapter:
    @staticmethod
    def run_script(launcher: Path, arguments: list) -> None:
        pkg_name = Path(launcher).stem.replace("-", "_")
        pkg_src = Path(launcher, "../../src/", pkg_name).resolve()

        sys.path.insert(0, str(pkg_src))

        subprocess.run(  # noqa: S603
            ["poetry", "--directory", pkg_src, "install"],  # noqa: S607
            capture_output=True,
            check=False,
        )
        subprocess.run(  # noqa: S603
            ["poetry", "--directory", pkg_src, "update"],  # noqa: S607
            capture_output=True,
            check=False,
        )
        venv_activator = PoetryAdapter.get_activator_path(pkg_src)

        if venv_activator.is_file():
            # Activate package's virtual environment
            runpy.run_path(str(venv_activator))

            launcher_module = importlib.import_module(f"{pkg_name}.cli")
            launcher_module.cli(arguments)
        else:
            print(
                f"Script preparation failed. Make sure `poetry install` can complete successfully in {pkg_src}.",
            )

    @staticmethod
    def get_activator_path(directory: Path) -> Path:
        venv_dir_stdout = subprocess.run(  # noqa: S603
            ["poetry", "--directory", directory, "env", "info", "--path"],  # noqa: S607
            stdout=subprocess.PIPE,
            check=False,
        )
        venv_dir = Path(venv_dir_stdout.stdout.decode("utf-8").strip())
        activator_posix = Path(venv_dir, "bin", "activate_this.py")
        activator_win = Path(venv_dir, "Scripts", "activate_this.py")

        if activator_posix.is_file():
            return activator_posix

        if activator_win.is_file():
            return activator_win

        return Path.cwd()
