#!/usr/bin/python3

import os

import argparse
import json

import himster
from general import find_file


# you do not have to touch this line unless you rename the script
script_name = 'run_boss_sim.sh'

json_file = open('config.json')
config_data = json.loads(json_file.read())
simreco_config = config_data['simreco']
job_option_file_ext = simreco_config['job_option_file_ext']
dec_file_ext = simreco_config['dec_file_ext']
job_option_filename_index_delimiter = simreco_config['job_option_filename_index_delimiter']
general_config = config_data['general']
datadir = os.environ[general_config['boss_data_envname']]
workarea = os.environ[general_config['boss_workarea_envname']]


parser = argparse.ArgumentParser(
    description='Script for submission of Boss simuation and reconstruction jobs',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('Ecms', type=int, nargs=1,
                    help='CMS energy in MeV')
parser.add_argument('events_per_job', type=int, nargs=1,
                    help='events per job')
parser.add_argument('number_of_jobs', metavar='number_of_jobs',
                    type=int, nargs=1,
                    help='number of jobs per decay file')
parser.add_argument('dec_files', metavar='dec_files', type=str, nargs='+',
                    help='list of decay files')

parser.add_argument('--start_job_index', metavar='start_job_index',
                    type=int, default=1,
                    help='index of the first job, which is used in filenames'
                    ' and the seed (default = 1)')
parser.add_argument('--task_type',
                    type=int,
                    choices=range(1, 4),
                    default=3,
                    help='Type of task:'
                    '\n1 -- simulation only'
                    '\n2 -- reconstruction only'
                    '\n3 -- both (default)')

parser.add_argument('--dec_file_dir',
                    type=str,
                    default='',
                    help='Name of directory containing the boss decay files'
                    ' used for the simulation.\nNote that this has to be the'
                    ' full path of the directory!\n'
                    )
parser.add_argument('--sim_job_option_dir',
                    type=str,
                    default='',
                    help='Name of directory containing the template boss job'
                    ' option txt files for the simulation.\nNote'
                    ' that this has to be the full path of the directory!\n'
                    )
parser.add_argument('--rec_job_option_dir',
                    type=str,
                    default='',
                    help='Name of directory containing the template boss job'
                    ' option txt files for the reconstruction.\nNote'
                    ' that this has to be the full path of the directory!\n'
                    )
parser.add_argument('--gen_job_option_filename_pattern',
                    type=str,
                    default='',
                    help='Specify a general filename pattern of the job'
                    ' option files,\nwhich is used to filter for specific'
                    ' simulation and reconstruction files.')
parser.add_argument('--sim_job_option_filename_pattern',
                    type=str,
                    default='',
                    help='Specify an additional filename pattern of the'
                    ' simulation job option files,\nwhich is used to filter'
                    ' for specific files.')
parser.add_argument('--rec_job_option_filename_pattern',
                    type=str,
                    default='',
                    help='Specify an additional filename pattern of the'
                    ' reconstruction job option files,\nwhich is used to'
                    ' filter for specific files.')

parser.add_argument('--isr', default=False,
                    action='store_true',
                    help='Use top job option file with ISR correction enabled.'
                    '\nFor this option to work, there has to be a template job'
                    '\noption file with \"_isr_\" in the name.'
                    '\nThe default template should have ISR correction '
                    'disabled\nin KKMC (otherwise this option is useless).')
parser.add_argument('--background', default=False,
                    action='store_true',
                    help='Use this flag to direct the output into the '
                    ' inclusive mc data subdirectory!')

args = parser.parse_args()

Ecms = args.Ecms[0]

sim_job_option_dir = args.sim_job_option_dir
rec_job_option_dir = args.rec_job_option_dir
dec_file_dir = args.dec_file_dir
if dec_file_dir is '':
    dec_file_dir = os.path.join(
        workarea, simreco_config['dec_file_subdir'])
dec_file_list = args.dec_files
digi_root_dir = ''
dst_output_dir = ''
sim_job_option_filename = ''
rec_job_option_filename = ''

pdt_table_path = ''
# scans directories for job option template files
# and selects correct one
if args.task_type == 1 or args.task_type == 3:
    # set directories correctly
    if sim_job_option_dir is '':
        sim_job_option_dir = os.path.join(
            workarea, simreco_config['job_opt_template_subdir'])
    pdt_table_path = os.path.join(
        workarea, simreco_config['pdt_table_subpath'])

    mc_dirname = simreco_config['mc_subdir']
    if args.background:
        mc_dirname = simreco_config['inclmc_subdir']
    digi_root_dir = os.path.join(
        datadir, mc_dirname + '/' + simreco_config['digi_root_subdir'])

    if not os.path.exists(digi_root_dir):
        os.makedirs(digi_root_dir)

    patterns = ['sim']
    if args.gen_job_option_filename_pattern != '':
        patterns.append(args.gen_job_option_filename_pattern)
    if args.sim_job_option_filename_pattern != '':
        patterns.append(args.sim_job_option_filename_pattern)
    sim_job_option_filename = find_file(
        sim_job_option_dir, patterns, job_option_file_ext)

if args.task_type == 2 or args.task_type == 3:
    if rec_job_option_dir is '':
        rec_job_option_dir = os.path.join(
            workarea, simreco_config['job_opt_template_subdir'])

    dst_output_dir = os.path.join(
        datadir, mc_dirname + '/' + simreco_config['dst_output_subdir'])
    use_energy_subdir_for_dsts = simreco_config['use_energy_subdir_for_dsts']
    if use_energy_subdir_for_dsts:
        dst_output_dir = os.path.join(dst_output_dir, str(Ecms))

    if not os.path.exists(dst_output_dir):
        os.makedirs(dst_output_dir)

    patterns = ['rec']
    if args.gen_job_option_filename_pattern != '':
        patterns.append(args.gen_job_option_filename_pattern)
    if args.rec_job_option_filename_pattern != '':
        patterns.append(args.rec_job_option_filename_pattern)
    rec_job_option_filename = find_file(
        rec_job_option_dir, patterns, job_option_file_ext)


low_index_used = args.start_job_index
high_index_used = args.start_job_index + args.number_of_jobs[0] - 1
print("using job array size of [" +
      str(low_index_used) + " - " + str(high_index_used) + "]")


joblist = []

# resource request of the job
job_walltime_in_minutes = 1 * 60
resource_request = himster.JobResourceRequest(job_walltime_in_minutes)
resource_request.number_of_nodes = 1
resource_request.processors_per_node = 1
resource_request.memory_in_mb = 2000
resource_request.virtual_memory_in_mb = 2000
resource_request.node_scratch_filesize_in_mb = 0

# get full path of the executable
script_fullpath = himster.get_exe_path(script_name)
script_home_path = os.path.abspath(os.path.dirname(script_fullpath))

for dec_file in dec_file_list:
    base = os.path.splitext(dec_file)[0]

    rtraw_filepath_base = digi_root_dir + "/" + base + "_" + \
        str(Ecms) + "-"
    dst_filepath_base = dst_output_dir + "/" + base
    if not use_energy_subdir_for_dsts:
        dst_filepath_base = dst_filepath_base + "_" + str(Ecms)
    dst_filepath_base = dst_filepath_base + "-"

    # create a himster job
    # set variables from config file
    application_path = simreco_config['application_path']
    job_name = simreco_config['job_name'] + base
    log_file_url = os.path.join(
        datadir, simreco_config['logfile_subdir'] +
        '/' + base + '_' + str(Ecms) + '/'
        + simreco_config['log_filename'])
    log_file_dirname = os.path.dirname(log_file_url)
    if not os.path.exists(log_file_dirname):
        os.makedirs(log_file_dirname)
    job = himster.Job(resource_request, script_fullpath,
                      job_name, log_file_url)

    job.set_job_array_size(low_index_used, high_index_used)

    job.add_exported_user_variable('script_home_path',
                                   script_home_path)
    job.add_exported_user_variable('application_path',
                                   application_path)
    if args.task_type == 1 or args.task_type == 3:
        job.add_exported_user_variable('sim_job_option_template_path',
                                       os.path.join(sim_job_option_dir,
                                                    sim_job_option_filename))
        dec_file_path = find_file(dec_file_dir, dec_file, dec_file_ext)
        job.add_exported_user_variable('dec_file_path', dec_file_path)
        job.add_exported_user_variable('pdt_table_path', pdt_table_path)
    job.add_exported_user_variable('rtraw_filepath_base',
                                   rtraw_filepath_base)
    if args.task_type == 2 or args.task_type == 3:
        job.add_exported_user_variable('rec_job_option_template_path',
                                       os.path.join(rec_job_option_dir,
                                                    rec_job_option_filename))
        job.add_exported_user_variable('dst_filepath_base',
                                       dst_filepath_base)
    job.add_exported_user_variable('task_type',
                                   args.task_type)
    job.add_exported_user_variable('Ecms',
                                   Ecms)
    job.add_exported_user_variable('events_per_job',
                                   args.events_per_job[0])

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
