import ntpath
import os


def verify_file_path(file_path):
    """Throws an exception if a file path does not point to a valid python file."""
    basename = ntpath.basename(file_path)

    # Full path checks
    if not os.path.exists(file_path):
        raise Exception('File path does not exist')

    if not os.path.isfile(file_path):
        raise Exception('File path does not point to a file')

    # Basename checks
    split_basename = basename.split('.')

    if len(split_basename) == 1:
        raise Exception('File has no extension')

    # Check for extra periods in basename
    for part in split_basename:
        if part.strip() == '':
            raise Exception('Unnecessary periods in file name')

    extension = split_basename[-1:][0]

    if extension != 'py':
        raise Exception('File does not have a supported python extension')
