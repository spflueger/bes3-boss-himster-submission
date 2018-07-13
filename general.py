from os import listdir, path, environ, pathsep, getcwd, access, X_OK, makedirs
from re import search
from glob import glob
from argparse import ArgumentDefaultsHelpFormatter, RawTextHelpFormatter
import sys


# remove stacktrace from thrown exceptions (nicer for user)
def exception_handler(exception_type, exception, traceback):
    # All your trace are belong to us!
    # your format
    print(exception_type.__name__, ":", exception)


sys.excepthook = exception_handler


class SmartFormatter(ArgumentDefaultsHelpFormatter):
    def _split_lines(self, text, width):
        return RawTextHelpFormatter._split_lines(self, text, width)


def get_exe_path(exe_name):
    exe_url = ''
    found = False
    for path_dir in environ["PATH"].split(pathsep):
        path_dir = path_dir.strip('"')
        exe_url = path.join(path_dir, exe_name)
        if path.isfile(exe_url):
            found = True
            break
    if not found:
        exe_url = path.join(getcwd(), exe_name)
        if not path.isfile(exe_url):
            raise FileNotFoundError(
                'Could not find executable ' + str(exe_name))
    if not access(exe_url, X_OK):
        raise PermissionError(
            'Please give ' + str(exe_url) + ' execute permission!')

    return exe_url


def check_index_range_for_directory(dir_path, regex_pattern):
    # check for the index range in the specified folder
    first = 1
    lowest_index = -1
    highest_index = -1

    dircontent = listdir(dir_path)

    for file in dircontent:
        result = search(regex_pattern, file)
        if result:
            if first:
                lowest_index = int(result.group(1))
                highest_index = int(result.group(1))
                first = 0
            else:
                if int(result.group(1)) < lowest_index:
                    lowest_index = int(result.group(1))
                elif int(result.group(1)) > highest_index:
                    highest_index = int(result.group(1))

    return [lowest_index, highest_index]


def create_directory_structure(base_dir, forced_subdir_list,
                               optional_subdir_list, use_optional_subdirs):
    output_dir = base_dir
    for subdir in forced_subdir_list:
        output_dir = path.join(output_dir, subdir)
    if use_optional_subdirs:
        for subdir in optional_subdir_list:
            output_dir = path.join(output_dir, subdir)

    if not path.exists(output_dir):
        makedirs(output_dir)
    return output_dir


def create_filename_base(filename_base_start, base_suffixes, use_subdirs):
    filename_base = filename_base_start
    if not use_subdirs:
        for suffix in base_suffixes:
            filename_base += '_' + suffix

    return filename_base


def find_file(dir_path, filename_patterns, file_ext):
    print("searching for file with patterns",
          filename_patterns, "in directory", dir_path)
    job_opt_files_all = glob(dir_path + '/*' + file_ext)
    if not job_opt_files_all:
        raise FileNotFoundError(
            'Did not find any files with the requested file extension in the'
            ' specified directory.\n'
            'directory: ' + dir_path + '\n'
            'file ext: ' + str(file_ext) + '\n'
            'Please double check your request.')
    job_opt_files = []
    # filter for patterns
    for job_opt_file in job_opt_files_all:
        filename = path.split(job_opt_file)[1]
        skip = False
        for pattern in filename_patterns:
            if pattern not in filename:
                skip = True
                break
        if not skip:
            job_opt_files.append(job_opt_file)

    if not job_opt_files:
        raise FileNotFoundError(
            'Did not find any files in the directory, that'
            ' match your requested pattern.\n'
            'directory: ' + dir_path + '\n'
            'patterns: ' + str(filename_patterns) + '\n'
            'Please double check your request.')
    return_index = 0
    if len(job_opt_files) > 1:
        print("Multiple job option templates found in this directory!")
        return_index = select_item(job_opt_files)

    return job_opt_files[return_index]


def find_files(dir_path, filename_patterns, file_ext='',
               forbid_no_results=True):
    print("searching for files with patterns",
          filename_patterns, "in directory", dir_path)
    files_all = glob(dir_path + '/*' + file_ext)
    if not files_all and forbid_no_results:
        raise FileNotFoundError(
            'Did not find any files with the requested file extension in the'
            ' specified directory.\n'
            'directory: ' + dir_path + '\n'
            'file ext: ' + str(file_ext) + '\n'
            'Please double check your request.')
    files = []
    # filter for patterns
    for file in files_all:
        filename = path.split(file)[1]
        skip = False
        for pattern in filename_patterns:
            if pattern not in filename:
                skip = True
                break
        if not skip:
            files.append(file)

    if not files and forbid_no_results:
        raise FileNotFoundError(
            'Did not find any files in the directory, that'
            ' match your requested pattern.\n'
            'directory: ' + dir_path + '\n'
            'patterns: ' + str(filename_patterns) + '\n'
            'file ext: ' + str(file_ext) + '\n'
            'Please double check your request.')

    return files


def find_dir(dir_path, subdir_name_patterns):
    print("searching for sub-directories with patterns",
          subdir_name_patterns, "in directory", dir_path)
    dirs_all = listdir(dir_path)
    if not dirs_all:
        raise FileNotFoundError(
            'Did not find any sub-directories in the specified directory!')
    dirs = []
    # filter for patterns
    for dirname in dirs_all:
        skip = False
        for pattern in subdir_name_patterns:
            if pattern not in dirname:
                skip = True
                break
        if not skip:
            dirs.append(dirname)

    if not dirs:
        raise FileNotFoundError(
            'Did not find any directory which matches your requested'
            ' patterns.\n'
            'directory: ' + dir_path + '\n'
            'patterns: ' + str(subdir_name_patterns) + '\n'
            'Please double check your request.')
    return_index = 0
    if len(dirs) > 1:
        print("Multiple directories match the search patterns!")
        return_index = select_item(dirs)

    return dirs[return_index]


def select_item(list_of_items):
    return_index = -1

    for i in list_of_items:
        print(str(list_of_items.index(i)) + ': ' + i)
    return_index = -1
    while return_index not in range(0, len(list_of_items)):
        return_index = input('Please enter a number corresponding'
                             ' to the item you want to use: ')
        try:
            return_index = int(return_index)
        except ValueError:
            return_index = -1

    return return_index


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' "
                  "(or 'y' or 'n').\n")


def get_missing_job_indices(directory, filename_patterns,
                            low_job_index, high_job_index, min_file_size):
    all_files = find_files(directory, filename_patterns, '', False)
    indices_to_resimulate = list(range(low_job_index, high_job_index + 1))
    for file_path in all_files:
        if path.getsize(file_path) / 1000 > min_file_size:
            filename = path.splitext(path.split(file_path)[1])[0]
            result = search("^.*-(\d*)$", filename)
            if not result:
                raise ValueError("Found file " + filename + " does not have"
                                 " job index at the end.")
            else:
                file_index = int(result.group(1))
                if (file_index <= high_job_index
                        and file_index >= low_job_index):
                    del indices_to_resimulate[
                        indices_to_resimulate.index(file_index)]
    return indices_to_resimulate


def create_file_chunks(file_list, chunk_size, redistribution_threshold):
    if not isinstance(redistribution_threshold, float):
        raise TypeError("The redistribution threshold should be of type float"
                        " (Given: " + str(redistribution_threshold) + ")")
    if redistribution_threshold < 0.0 or redistribution_threshold > 1.0:
        raise ValueError("Warning: the redistribution threshold for the file"
                         " bunching should be a number between 0 and 1!"
                         " (Given: " + str(redistribution_threshold) + ")")
    file_chunks = []
    # now group files in bundles of chunk size
    for i in range(0, len(file_list), chunk_size):
        file_chunks.append(file_list[i:i + chunk_size])

    # if last job got below the total number of jobs
    # then redistribute
    if (len(file_chunks) > 1 and
            len(file_chunks[-1]) < redistribution_threshold * chunk_size):
        last_chunk = file_chunks.pop()
        for i in last_chunk:
            file_chunks[last_chunk.index(i)].append(i)

    return file_chunks
