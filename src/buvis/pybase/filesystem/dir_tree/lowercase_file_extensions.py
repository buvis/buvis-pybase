from pathlib import Path


def lowercase_file_extensions(directory: Path) -> None:
    """
    Convert all file extensions to lowercase in the given directory.

    :param directory: Path to the directory to process
    :type directory: :class:`Path`
    :return: None. The function modifies the <directory> in place.
    """
    for file_path in directory.rglob("*"):
        if file_path.is_file():
            lowercase_ext = file_path.suffix.lower()
            new_name = file_path.with_name(file_path.stem + lowercase_ext)
            if new_name != file_path:
                file_path.rename(new_name)