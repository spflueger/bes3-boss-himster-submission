#!/usr/bin/python3

import argparse

import himster
from general import (check_index_range_for_directory,
                     get_job_option_base_filename)


# you do not have to touch this line unless you rename the script
script_name = 'run_boss.sh'

# -------- user defined variables --------
# set these according to your needs
job_name = 'boss-ana'
job_option_file_ext = '.txt'
job_option_filename_index_delimiter = '-'
application_path = '/path/to/your/boss.exe'
log_filename = 'boss_ana.log'
# ----------------------------------------


parser = argparse.ArgumentParser(
    description='Script for submission of Boss analysis jobs',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('job_options_dir_path',
                    metavar='job_options_dir_path',
                    type=str,
                    nargs=1,
                    help='Name of directory containing the boss job option'
                    ' txt files.\n Note that this has to be the full path of'
                    ' the directory!\n'
                    )

parser.add_argument('--job_option_filename_pattern',
                    metavar='job_option_filename_pattern',
                    type=str,
                    default='',
                    help='Specify a filename pattern of the job option files'
                    ' which can be used to filter for specific files')

parser.add_argument('--low_index', metavar='low_index', type=int, default=-1,
                    help='Lowest index of boss job option file which is '
                    ' supposed to be used in the simulation.\nDefault setting'
                    ' is -1, which will take the lowest found index.')
parser.add_argument('--high_index', metavar='high_index', type=int, default=-1,
                    help='Highest index of boss job option file which is '
                    'supposed to be used in the simulation.\nDefault setting'
                    ' is -1 which will take the highest found index.')


args = parser.parse_args()

joblist = []

# scans the directory for a set of job option files
# and retrieves the filename base
job_option_filename_base = get_job_option_base_filename(
    args.job_options_dir_path[0], args.job_option_filename_pattern,
    job_option_filename_index_delimiter, job_option_file_ext)

# determine the job array index range,
# either given by user or calculate automatically
[low_index_used, high_index_used] = check_index_range_for_directory(
    args.job_options_dir_path[0],
    job_option_filename_index_delimiter + '(\d+)' + job_option_file_ext + '$')
if args.low_index >= 0:
    low_index_used = args.low_index
if args.high_index >= 0 and args.high_index >= args.low_index:
    high_index_used = args.high_index

# resource request of the job
job_walltime_in_minutes = 20 * 60
resource_request = himster.JobResourceRequest(job_walltime_in_minutes)
resource_request.number_of_nodes = 1
resource_request.processors_per_node = 1
resource_request.memory_in_mb = 2000
resource_request.virtual_memory_in_mb = 2000
resource_request.node_scratch_filesize_in_mb = 0

# get full path of the executable
script_fullpath = himster.get_exe_path(script_name)

# create a himster job
log_file_url = args.job_options_dir_path[0] + '/' + log_filename
job = himster.Job(resource_request, script_fullpath, job_name, log_file_url)
print("using job array size of [" +
      str(low_index_used) + " - " + str(high_index_used) + "]")
job.set_job_array_size(low_index_used, high_index_used)

job.add_exported_user_variable('application_path',
                               application_path)
job.add_exported_user_variable('job_option_dir',
                               args.job_options_dir_path[0])
job.add_exported_user_variable('job_option_filename',
                               job_option_filename_base)
job.add_exported_user_variable('job_option_filename_index_delimiter',
                               job_option_filename_index_delimiter)
job.add_exported_user_variable('job_option_file_ext',
                               job_option_file_ext)

# add the job to the joblist which we pass to the job manager later
joblist.append(job)

# job threshold of and waittime if threshold is reached
# (this can be used to moderate the load on himster)
himster_overload_waittime_in_seconds = 3600
concurrent_job_threshold = 1000
job_manager = himster.HimsterJobManager(concurrent_job_threshold,
                                        himster_overload_waittime_in_seconds)

# now pass the joblist to the manager and let him do this thing
job_manager.submit_jobs_to_himster(joblist)
job_manager.manage_jobs()
