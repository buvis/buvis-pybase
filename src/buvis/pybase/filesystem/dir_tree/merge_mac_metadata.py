from pathlib import Path

import xattr


def merge_mac_metadata(directory: Path) -> None:
    """
    Clean Mac metadata by merging extended attributes and removing ._ files.

    This function attempts to mimic the behavior of 'dot_clean -mn':
    - For each ._ file, it tries to merge its contents into the corresponding data file.
    - If merging is successful, it removes the ._ file.
    - If there's no corresponding data file, it removes the ._ file.

    :param directory: Path to the directory to process
    :type directory: :class:`Path`
    :return: None. The function modifies the <directory> in place.
    """
    directory = Path(directory)
    for file_path in directory.rglob("._*"):
        if file_path.is_file():
            data_file = file_path.with_name(file_path.name[2:])
            if data_file.exists():
                try:
                    # Read the resource fork from the ._ file
                    with open(file_path, "rb") as f:
                        resource_fork = f.read()

                    # Set the resource fork as an extended attribute on the data file
                    xattr.setxattr(
                        str(data_file), "com.apple.ResourceFork", resource_fork
                    )

                    # Remove the ._ file
                    file_path.unlink()
                except OSError as _:
                    pass
            else:
                # If there's no corresponding data file, just remove the ._ file
                try:
                    file_path.unlink()
                except OSError as _:
                    pass
