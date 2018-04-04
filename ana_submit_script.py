#!/usr/bin/python3

import os
import json
import argparse

import himster2

# you do not have to touch this line unless you rename the script
script_name = 'run_boss_ana.sh'
script_fullpath = himster2.get_exe_path(script_name)
script_dir = os.path.abspath(os.path.dirname(script_fullpath))

# get runtime configs
json_file = open(script_dir + '/config.json')
config_data = json.loads(json_file.read())
general_config = config_data['general']
analysis_config = config_data['analysis']

workarea = os.environ[general_config['boss_workarea_envname']]
default_job_opt_dir = os.path.join(
    workarea, analysis_config['job_opt_template_subdir'])
job_option_file_ext = analysis_config['job_option_file_ext']

parser = argparse.ArgumentParser(
    description='Script for submission of Boss analysis jobs',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('job_config_file_path', type=str, nargs=1,
                    help='Path to job config file')
parser.add_argument('--force', default=False,
                    action='store_true',
                    help='Rerun this job completely, even if files already'
                    ' exist. Warning: this will overwrite existing files!')

args = parser.parse_args()


# load job config
job_json_file = open(args.job_config_file_path[0])
job_config_data = json.loads(job_json_file.read())


joblist = []

# resource request of the job
job_res_config = analysis_config['job_resource_request']
job_walltime_in_minutes = int(60 * job_res_config['walltime_in_hours'])
resource_request = himster2.JobResourceRequest(job_walltime_in_minutes)
resource_request.number_of_nodes = int(job_res_config['number_of_nodes'])
resource_request.processors_per_node = int(
    job_res_config['processors_per_node'])
resource_request.memory_in_mb = int(job_res_config['memory_in_mb'])
resource_request.virtual_memory_in_mb = int(
    job_res_config['virtual_memory_in_mb'])
resource_request.node_scratch_filesize_in_mb = int(
    job_res_config['node_scratch_filesize_in_mb'])

# create a himster job
log_filename = analysis_config['log_filename']
job_name = analysis_config['job_name']

log_file_dir = os.path.dirname(job_config_data['log_file_url'])
if not os.path.exists(log_file_dir):
    os.makedirs(log_file_dir)
job = himster2.Job(resource_request, script_fullpath,
                   job_name, job_config_data['log_file_url'])

# TODO: at this point we have to determine which jobs to send out
low_index_used = job_config_data['job_array_start_index']
high_index_used = job_config_data['job_array_last_index']
print("using job array size of [" +
      str(low_index_used) + " - " + str(high_index_used) + "]")
job.set_job_array_size(low_index_used, high_index_used)

job.add_exported_user_variable('application_path',
                               job_config_data['boss_exe_path'])
job.add_exported_user_variable('dst_chunk_file_path',
                               job_config_data['dst_chunk_file_path'])
job.add_exported_user_variable('ana_job_option_template_path',
                               job_config_data['ana_job_option_template_path'])
job.add_exported_user_variable('output_dir',
                               job_config_data['output_dir'])
job.add_exported_user_variable('root_filename_base',
                               job_config_data['root_filename_base'])

# add the job to the joblist which we pass to the job manager later
joblist.append(job)

# job threshold of and waittime if threshold is reached
# (this can be used to moderate the load on himster)
himster_overload_waittime_in_seconds = 3600
concurrent_job_threshold = 1000
job_manager = himster2.HimsterJobManager(concurrent_job_threshold,
                                         himster_overload_waittime_in_seconds)

# now pass the joblist to the manager and let him do this thing
job_manager.submit_jobs_to_himster(joblist)
job_manager.manage_jobs()
