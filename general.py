from os import listdir, path, sys
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


def get_job_option_base_filename(dir_path, filename_pattern,
                                 delimiter, file_ext):
    job_opt_files = glob(dir_path + '/*' + filename_pattern + '*' + file_ext)

    filename_dict = {}

    for file in job_opt_files:
        filename = path.basename(file)
        m = search('(.*)' + delimiter + '(\d+).txt', filename)
        if m:
            base_filename = m.group(1)
            if base_filename in filename_dict:
                filename_dict[base_filename] = filename_dict[base_filename] + 1
            else:
                filename_dict[base_filename] = 1

    if len(filename_dict) > 1:
        print("found multiple filename patterns in this directory."
              "\nPlease use the filename_pattern parameter to "
              "filter out one set!")
        print("found file patterns with corresponding file count are:")
        print(filename_dict)
        sys.exit(1)

    elif len(filename_dict) == 0:
        print("Did not find any files in the directory, that match "
              "your requested pattern.\nPlease double check your request.")
        sys.exit(1)

    return next(iter(filename_dict))
