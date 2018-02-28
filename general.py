from os import listdir, path
from re import search
from glob import glob


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


def find_file(dir_path, filename_patterns, file_ext):
    job_opt_files_all = glob(dir_path + '/*' + file_ext)
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

    if len(job_opt_files) == 0:
        raise FileNotFoundError(
            'Did not find any files in the directory, that'
            ' match your requested pattern.\n'
            'directory: ' + dir_path + '\n'
            'patterns: ' + str(filename_patterns) + '\n'
            'file ext: ' + str(file_ext) + '\n'
            'Please double check your request.')
    return_index = 0
    if len(job_opt_files) > 1:
        return_index = -1
        print("Multiple job option templates found in this directory!")
        for jopopttemp in job_opt_files:
            print(str(job_opt_files.index(jopopttemp)) + ': ' + jopopttemp)
        return_index = -1
        while return_index not in range(0, len(job_opt_files)):
            return_index = input('Please enter a number corresponding'
                                 ' to the template you want to use: ')
            try:
                return_index = int(return_index)
            except ValueError:
                return_index = -1

    return job_opt_files[return_index]


def find_files(dir_path, filename_patterns, file_ext):
    files_all = glob(dir_path + '/*' + file_ext)
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

    if len(files) == 0:
        raise FileNotFoundError(
            'Did not find any files in the directory, that'
            ' match your requested pattern.\n'
            'directory: ' + dir_path + '\n'
            'patterns: ' + str(filename_patterns) + '\n'
            'file ext: ' + str(file_ext) + '\n'
            'Please double check your request.')

    return files


def find_dir(dir_path, subdir_name_patterns):
    dirs_all = listdir(dir_path)
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

    if len(dirs) == 0:
        raise FileNotFoundError(
            'Did not find any directory which matches your requested'
            ' patterns.\n'
            'directory: ' + dir_path + '\n'
            'patterns: ' + str(subdir_name_patterns) + '\n'
            'Please double check your request.')
    return_index = 0
    if len(dirs) > 1:
        return_index = -1
        print("Multiple directories match the search patterns!")
        for i in dirs:
            print(str(dirs.index(i)) + ': ' + i)
        return_index = -1
        while return_index not in range(0, len(dirs)):
            return_index = input('Please enter a number corresponding'
                                 ' to the directory you want to use: ')
            try:
                return_index = int(return_index)
            except ValueError:
                return_index = -1

    return dirs[return_index]


def create_file_chunks(file_list, chunk_size):
    file_chunks = []
    # now group files in bundles of chunk size
    for i in range(0, len(file_list), chunk_size):
        file_chunks.append(file_list[i:i + chunk_size])

    # if last job got below the total number of jobs
    # then redistribute
    if len(file_chunks[-1]) < len(file_chunks):
        last_chunk = file_chunks.pop()
        for i in last_chunk:
            file_chunks[last_chunk.index(i)].append(i)

    return file_chunks
