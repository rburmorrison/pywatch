import os
import sys
import time
from argparse import ArgumentParser
from subprocess import Popen

from pyverifier import verify_file_path

parser = ArgumentParser(description='Monitors a python file for changes and auto-reloads it.')
parser.add_argument('file', help='the file to watch')
parser.add_argument('-c', '--clear', dest='clear', action='store_true', help='clears the terminal between each restart')
parser.add_argument('-l', '--python2', dest='python2', action='store_true',
                    help='runs files with the "python2" command')
parser.add_argument('-a', '--args', dest='args', action='store_true', help='add custom arguments to run your file with')
args = parser.parse_args()


def get_file_lines(file_path):
    file = open(file_path, 'r')
    lines = file.readlines()
    file.close()

    return lines


def get_file_contents(file_path):
    file = open(file_path, 'r')
    lines = file.read()
    file.close()

    return lines


def get_formatted_import_names(file_path):
    verify_file_path(file_path)

    import_names = []
    lines = get_file_lines(file_path)
    for line in lines:
        split_line = line.split(' ')
        if len(split_line) <= 1:
            continue

        # Check if it's an import
        if split_line[0] == 'import':
            formatted_name = os.path.sep.join(split_line[1].split('.'))
            import_names.append(formatted_name)
        elif split_line[0] == 'from':
            formatted_name = os.path.sep.join(split_line[1].split('.'))
            import_names.append(formatted_name)

            # Add all possible files
            additions = split_line[3:]
            for addition in additions:
                addition = addition.replace(',', '').strip()
                import_name = os.path.join(formatted_name, addition)
                if import_name not in import_names:
                    import_names.append(import_name)

    return import_names


def find_included_files(file_path):
    file_paths = []
    import_names = get_formatted_import_names(file_path)

    for name in import_names:
        name = name.strip()
        root_dir = os.path.sep.join(file_path.split(os.path.sep)[:-1])

        # Dress up name
        full_path = os.path.join(root_dir, name + '.py')

        try:
            verify_file_path(full_path)

            if full_path not in file_paths:
                file_paths.append(full_path)
        except Exception:
            continue

    for path in file_paths:
        file_paths += find_included_files(path)

    # Remove duplicates
    file_paths_set = set()
    for path in file_paths:
        file_paths_set.add(path)

    return list(file_paths_set)


def get_all_file_paths(full_path):
    included_files = find_included_files(full_path)
    included_files.append(full_path)
    return included_files


def clear_terminal():
    if args.clear:
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            os.system('cls')
        else:
            os.system('clear')


def start_watch_loop(root, paths_to_watch):
    # Get extra arguments if requested
    extra_args = []
    if args.args:
        args_input = input('> Add arguments, separated by spaces: ')
        extra_args = args_input.split(' ')

    # Check what python version is being used
    python_command = 'python'
    if args.python2:
        python_command = 'python2'

    try:
        process = Popen([python_command, root] + extra_args)
    except FileNotFoundError:
        print(
            'Python is not set up properly. '
            'Make sure python is accessible from the command line with "python" or "python2".'
        )
        sys.exit(0)

    clear_terminal()
    print('> Watching %s' % root.split(os.path.sep)[-1:][0])
    file_data = {}
    for path in paths_to_watch:
        file_data[path] = get_file_contents(path)

    # Start of loop
    try:
        while True:
            for path in paths_to_watch:
                # Something was changed
                if file_data[path] != get_file_contents(path):
                    clear_terminal()
                    print('> File %s changed. Refreshed.' % path.split(os.path.sep)[-1:][0])
                    paths_to_watch = get_all_file_paths(root)

                    # Refresh file data
                    for path in paths_to_watch:
                        file_data[path] = get_file_contents(path)

                    # Restart the process
                    try:
                        process.kill()
                        process = Popen([python_command, root] + extra_args)
                    except FileNotFoundError:
                        print(
                            'Python is not set up properly. '
                            'Make sure python is accessible from the command line with "python" or "python2".'
                        )
                        sys.exit(0)

            time.sleep(.100)
    except KeyboardInterrupt:
        print('\u001b[0m\nDone')
        process.kill()


def main():
    file_arg = args.file
    full_path = os.path.join(os.getcwd(), file_arg)
    verify_file_path(full_path)

    all_paths = get_all_file_paths(full_path)
    start_watch_loop(full_path, all_paths)


if __name__ == '__main__':
    main()
