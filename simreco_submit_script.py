#!/usr/bin/env python3

import os
import argparse
import json

import himster2
from general import find_file, get_missing_job_indices


# you do not have to touch this line unless you rename the script
script_name = 'run_boss_sim.sh'
# get full path of the executable
script_fullpath = himster2.get_exe_path(script_name)
script_home_path = os.path.abspath(os.path.dirname(script_fullpath))


json_file = open(script_home_path + '/config.json')
config_data = json.loads(json_file.read())
simreco_config = config_data['simreco']
job_option_file_ext = simreco_config['job_option_file_ext']
dec_file_ext = simreco_config['dec_file_ext']
general_config = config_data['general']
datadir = os.environ[general_config['boss_data_envname']]
workarea = os.environ[general_config['boss_workarea_envname']]


parser = argparse.ArgumentParser(
    description='Script for submission of Boss simuation and reconstruction'
    ' jobs',
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

parser.add_argument('--random_seed', type=int, default=1234,
                    help='Global initial random seed. The random seed for each'
                    ' job is calculated as the sum of\nthe global initial'
                    ' random seed and the array id.')

parser.add_argument('--extra_file', type=str, default='',
                    help='Path to a file, which will be copied on the node '
                    'scratch directory to work with in the simulation.')

parser.add_argument('--force', default=False, action='store_true',
                    help='Forces the simulation and/or reconstruction,'
                    ' even if the output files already exist')

parser.add_argument('--dump_job_options', default=False, action='store_true',
                    help='Instead of performing the sim/reco, the Boss options'
                    ' of the job with the lowest job array id are dumped.')

args = parser.parse_args()

# check if extra file exists
if args.extra_file != '':
    if os.path.isfile(args.extra_file) is not True:
        raise FileNotFoundError("Requested extra file not found.")

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
use_energy_subdirs = general_config['use_energy_and_dec_filename_data_subdirs']

mc_dirname = simreco_config['mc_subdir']
if args.background:
    mc_dirname = simreco_config['inclmc_subdir']
digi_root_dir = os.path.join(
    datadir, mc_dirname + '/' + simreco_config['digi_root_subdir'])
if use_energy_subdirs:
    digi_root_dir = os.path.join(digi_root_dir, str(Ecms))

if not os.path.exists(digi_root_dir):
    os.makedirs(digi_root_dir)

# scans directories for job option template files
# and selects correct one
if args.task_type == 1 or args.task_type == 3:
    # set directories correctly
    if sim_job_option_dir is '':
        sim_job_option_dir = os.path.join(
            workarea, simreco_config['job_opt_template_subdir'])
    if simreco_config['use_own_pdt_table']:
        pdt_table_path = os.path.join(
            workarea, simreco_config['pdt_table_subpath'])

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
    if use_energy_subdirs:
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
job_res_config = simreco_config['job_resource_request']
job_walltime_in_minutes = int(60 * job_res_config['walltime_in_hours'])
resource_request = himster2.JobResourceRequest(job_walltime_in_minutes)
resource_request.number_of_nodes = 1
resource_request.processors_per_node = 1
resource_request.memory_in_mb = int(job_res_config['memory_in_mb'])
resource_request.virtual_memory_in_mb = int(
    job_res_config['virtual_memory_in_mb'])
resource_request.node_scratch_filesize_in_mb = int(
    job_res_config['node_scratch_filesize_in_mb'])


for dec_file in dec_file_list:
    dec_file_path = find_file(dec_file_dir, [dec_file], dec_file_ext)
    base = os.path.splitext(os.path.split(dec_file_path)[1])[0]

    rtraw_dir = digi_root_dir + "/"
    rtraw_filename_base = ''
    if use_energy_subdirs:
        rtraw_dir += base + "/"
        rtraw_filename_base = 'digi'
    else:
        rtraw_filename_base = base + '_' + str(Ecms)
    rtraw_filepath_base = rtraw_dir + rtraw_filename_base + '-'
    if not os.path.exists(rtraw_dir):
        os.makedirs(rtraw_dir)

    dst_dir = dst_output_dir + "/"
    dst_filename_base = ''
    if use_energy_subdirs:
        dst_dir += base + "/"
        dst_filename_base = 'digi'
    else:
        dst_filename_base = base + '_' + str(Ecms)
    dst_filepath_base = dst_dir + dst_filename_base + '-'
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    job_array_range = {}
    # remove array jobs for which the output files are already existent
    # and have a file size above the minimum
    if args.dump_job_options:
        job_array_range = {args.task_type: [low_index_used]}
    elif not args.force:
        num_events = args.events_per_job[0]
        sim_missing = []
        reco_missing = []
        if args.task_type == 1 or args.task_type == 3:
            sim_missing = get_missing_job_indices(
                rtraw_dir, rtraw_filename_base,
                low_index_used, high_index_used,
                num_events * simreco_config['sim_min_filesize_per_event_in_kb'])
        if args.task_type == 2 or args.task_type == 3:
            reco_missing = get_missing_job_indices(
                dst_dir, dst_filename_base, low_index_used, high_index_used,
                num_events * simreco_config['reco_min_filesize_per_event_in_kb'])

        missing_tasks = {}
        for x in sim_missing:
            missing_tasks[x] = 1
        for x in reco_missing:
            if x in missing_tasks:
                missing_tasks[x] = 3
            else:
                missing_tasks[x] = 2

        for index, task_type in missing_tasks.items():
            if task_type not in job_array_range:
                job_array_range[task_type] = []
            job_array_range[task_type].append(index)
    else:
        job_array_range = {args.task_type: list(range(
            low_index_used, high_index_used + 1))}

    # create a himster job
    # set variables from config file
    application_path = simreco_config['application_path']
    job_name = simreco_config['job_name'] + base
    log_file_url = os.path.join(
        datadir, general_config['logfile_subdir'])
    logfile_suffix = os.path.splitext(simreco_config['log_filename'])
    if use_energy_subdirs:
        log_file_url += '/' + str(Ecms) + '/' + base + \
            '/' + logfile_suffix[0] + '-%a' + logfile_suffix[1]
    else:
        log_file_url += '/' + base + '_' + \
            str(Ecms) + '_' + logfile_suffix[0] + '-%a' + logfile_suffix[1]

    log_file_dirname = os.path.dirname(log_file_url)
    if not os.path.exists(log_file_dirname):
        os.makedirs(log_file_dirname)

    for task_type, array_indices in job_array_range.items():
        if len(array_indices) == 0:
            continue

        job = himster2.Job(resource_request, script_fullpath, job_name,
                           log_file_url)
        array_indices.sort()
        job.set_job_array_indices(array_indices)
        if args.dump_job_options:
            job.add_exported_user_variable('dump_job_options',
                                           1)
        job.add_exported_user_variable('script_home_path',
                                       script_home_path)
        job.add_exported_user_variable('application_path',
                                       application_path)
        if task_type == 1 or task_type == 3:
            job.add_exported_user_variable(
                'sim_job_option_template_path',
                os.path.join(sim_job_option_dir, sim_job_option_filename))
            job.add_exported_user_variable('dec_file_path', dec_file_path)
            job.add_exported_user_variable('pdt_table_path', pdt_table_path)
        job.add_exported_user_variable('rtraw_filepath_base',
                                       rtraw_filepath_base)
        if task_type == 2 or task_type == 3:
            job.add_exported_user_variable(
                'rec_job_option_template_path',
                os.path.join(rec_job_option_dir, rec_job_option_filename))
            job.add_exported_user_variable('dst_filepath_base',
                                           dst_filepath_base)
            job.add_exported_user_variable(
                'himster2_randomtrg_path',
                simreco_config['himster2_randomtrg_path'])
        job.add_exported_user_variable('task_type',
                                       task_type)
        job.add_exported_user_variable('Ecms',
                                       Ecms)
        job.add_exported_user_variable('events_per_job',
                                       args.events_per_job[0])
        job.add_exported_user_variable('random_seed',
                                       args.random_seed)
        if args.extra_file != '':
            job.add_exported_user_variable('extra_file',
                                           args.extra_file)

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
