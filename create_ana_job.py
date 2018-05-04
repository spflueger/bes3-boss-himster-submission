#!/usr/bin/python3
import os
import argparse
import json

import himster2
from general import find_file, find_files, find_dir, create_file_chunks


# get full path of the executable
script_fullpath = himster2.get_exe_path('create_ana_job.py')
script_dir = os.path.abspath(os.path.dirname(script_fullpath))

json_file = open(script_dir + '/config.json')
config_data = json.loads(json_file.read())
analysis_config = config_data['analysis']
# set some global variables from config file
job_option_file_ext = analysis_config['job_option_file_ext']
application_path = analysis_config['application_path']
general_config = config_data['general']
datadir = os.environ[general_config['boss_data_envname']]
workarea = os.environ[general_config['boss_workarea_envname']]
use_energy_subdirs = general_config['use_energy_and_dec_filename_data_subdirs']


def create_analysis_job_config(ecms, task_type, algorithm, job_opt_dir,
                               job_opt_pattern, dst_dir_pattern, dst_file_subdir,
                               dst_file_pattern, files_per_job, root_file_dir):
    ana_job_config = {}
    ana_job_config['boss_exe_path'] = application_path

    task_pattern = ''
    dst_type_subdir = ''
    if task_type == 1:
        task_pattern = 'data'
        dst_type_subdir = config_data['simreco']['data_subdir']
    elif task_type == 2:
        task_pattern = 'inclMc'
        dst_type_subdir = config_data['simreco']['inclmc_subdir']
    else:
        task_pattern = 'mc'
        dst_type_subdir = config_data['simreco']['mc_subdir']

    # find the analysis job option template file
    ana_job_option_dir = os.path.join(
        workarea, analysis_config['job_opt_template_subdir'])
    if job_opt_dir != '':
        ana_job_option_dir = job_opt_dir

    ana_job_option_patterns = ['ana', task_pattern]
    if algorithm != '':
        ana_job_option_patterns.append(algorithm)
    if job_opt_pattern != '':
        ana_job_option_patterns = [job_opt_pattern]
    ana_job_config['ana_job_option_template_path'] = find_file(
        ana_job_option_dir, ana_job_option_patterns, job_option_file_ext)
    ana_job_option_base = os.path.splitext(os.path.split(
        ana_job_config['ana_job_option_template_path'])[1])[0]
    ana_job_option_base = ana_job_option_base.replace('ana', '')
    ana_job_option_base = ana_job_option_base.replace(task_pattern, '')
    ana_job_option_base = ana_job_option_base.rstrip(
        '-').rstrip('_').lstrip('-').lstrip('_')

    # Search for dst files in the our data dir
    if dst_file_subdir == '':
        dst_file_subdir = config_data['simreco']['dst_output_subdir']
    dst_file_subdir = dst_type_subdir + '/' + dst_file_subdir
    if use_energy_subdirs:
        dst_file_subdir += '/' + str(Ecms) + '/'
    dst_file_dir = os.path.join(datadir, dst_file_subdir)
    dst_decsubdir_name = find_dir(dst_file_dir, dst_dir_pattern)
    dst_file_dir = os.path.join(
        dst_file_dir, dst_decsubdir_name)
    dst_file_patterns = []
    if dst_file_pattern != '':
        dst_file_patterns.append(dst_file_pattern)
    dst_data_files = find_files(dst_file_dir, dst_file_patterns, '.dst')

    dst_file_chunks = create_file_chunks(dst_data_files, files_per_job)

    ana_job_config['job_array_start_index'] = 1
    ana_job_config['job_array_last_index'] = len(dst_file_chunks)

    root_file_dir = os.path.join(
        root_file_dir, dst_type_subdir + '/'
        + analysis_config['root_output_subdir'])
    if use_energy_subdirs:
        subdir = str(Ecms) + '/' + ana_job_option_base + \
            '/' + dst_decsubdir_name
        root_file_subdir_order = analysis_config['root_output_dir_subdir_order']
        if root_file_subdir_order == 'decayname/algorithm':
            subdir = str(Ecms) + '/' + dst_decsubdir_name + \
                '/' + ana_job_option_base
        root_file_dir = os.path.join(root_file_dir, subdir)

    if not os.path.exists(root_file_dir):
        os.makedirs(root_file_dir)

    ana_job_config['output_dir'] = root_file_dir
    root_filename_base = ana_job_option_base + '-' + dst_decsubdir_name + '-'
    if use_energy_subdirs:
        root_filename_base = 'ana-'
    ana_job_config['root_filename_base'] = root_filename_base

    # write dst chunks file
    dst_chunk_file_path = os.path.join(root_file_dir, 'dst_chunks.txt')
    print('creating dst chunk file: ' + dst_chunk_file_path)
    with open(dst_chunk_file_path, "w") as outfile:
        index = 0
        for chunk in dst_file_chunks:
            index = index + 1
            string = str(index) + ': {' + chunk[0]
            for dstfile in chunk[1:]:
                string = string + ', ' + dstfile
            string = string + '}\n'
            outfile.write(string)
        outfile.close()
    ana_job_config['dst_chunk_file_path'] = dst_chunk_file_path

    log_file_url = ana_job_config['output_dir']
    if general_config['use_separate_log_dir']:
        log_file_url = os.path.join(
            datadir, general_config['logfile_subdir'])
    logfile_suffix = os.path.splitext(analysis_config['log_filename'])
    if use_energy_subdirs:
        log_file_url += '/' + str(Ecms) + '/' + dst_decsubdir_name + \
            '/' + ana_job_option_base + '/' + \
            logfile_suffix[0] + '-%a' + logfile_suffix[1]
    else:
        log_file_url += '/' + ana_job_option_base + '_' + \
            str(Ecms) + '_' + logfile_suffix[0] + '-%a' + logfile_suffix[1]
    ana_job_config['log_file_url'] = log_file_url

    ana_job_config_path = os.path.join(root_file_dir, 'ana_job_config.json')
    print('creating ana job config file: ' + ana_job_config_path)
    with open(ana_job_config_path, 'w') as outfile:
        json.dump(ana_job_config, outfile, indent=4)
        outfile.close()

    return ana_job_config_path


parser = argparse.ArgumentParser(
    description='Script for submission of Boss analysis jobs',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('Ecms', metavar='Ecms', type=int, nargs=1)
parser.add_argument('dst_dirname_pattern', type=str, nargs=1)
parser.add_argument('--files_per_job', metavar='files_per_job',
                    type=int, default=analysis_config['dst_files_per_job'])
parser.add_argument('--task_type',
                    type=int,
                    nargs='+',
                    choices=range(1, 4),
                    default=[3],
                    help='Type of task:'
                    '\n1 -- data only'
                    '\n2 -- inclusive MC only'
                    '\n3 -- MC only')
parser.add_argument('--algorithm', metavar='algorithm',
                    type=str, default=analysis_config['default_algorithm'])
parser.add_argument('--data_dir', metavar='data_dir',
                    type=str, default='')
parser.add_argument('--dst_file_subdir', metavar='dst_file_subdir',
                    type=str, default='')
parser.add_argument('--dst_file_pattern',
                    metavar='filter', type=str, default='')
parser.add_argument('--job_options_dir',
                    type=str,
                    default='',
                    help='Name of directory containing the boss job option'
                    ' txt files.\n Note that this has to be the full path of'
                    ' the directory!\n'
                    )
parser.add_argument('--job_option_filename_pattern',
                    type=str,
                    default='',
                    help='Specify a filename pattern of the job option'
                    ' template file.')

args = parser.parse_args()

Ecms = args.Ecms[0]

task_list = list(set(args.task_type))

if args.data_dir != '':
    datadir = args.data_dir
if not os.path.exists(datadir):
    raise FileNotFoundError("Did not find directory " + str(datadir))


ana_job_option_dir = args.job_options_dir
# scans directories for job option template files
if ana_job_option_dir is '':
    ana_job_option_dir = os.path.join(
        workarea, analysis_config['job_opt_template_subdir'])
root_file_dir = datadir


analysis_job_config_paths = []
for i in task_list:
    analysis_job_config_paths.append(
        create_analysis_job_config(Ecms, i, args.algorithm,
                                   ana_job_option_dir,
                                   args.job_option_filename_pattern,
                                   args.dst_dirname_pattern,
                                   args.dst_file_subdir,
                                   args.dst_file_pattern,
                                   args.files_per_job,
                                   root_file_dir
                                   )
    )


for ana_job_config_path in analysis_job_config_paths:
    os.system('python3 ' + os.path.join(script_dir, 'ana_submit_script.py') +
              " " + ana_job_config_path)
