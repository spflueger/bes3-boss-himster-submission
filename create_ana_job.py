#!/usr/bin/env python3

import os
import argparse
import json
from re import search
from sys import exit

from general import (find_file, find_files, find_dir, create_file_chunks,
                     get_exe_path, create_directory_structure,
                     create_filename_base, query_yes_no, SmartFormatter)


# get full path of the executable
script_fullpath = get_exe_path('create_ana_job.py')
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
                               job_opt_pattern, dst_dir_pattern,
                               dst_file_subdir, dst_file_pattern,
                               files_per_job, analysis_file_output_dir):
    ana_job_config = {}
    ana_job_config['boss_exe_path'] = application_path

    dst_type_subdir = ''
    if task_type == 1:
        dst_type_subdir = general_config['data_subdir']
    elif task_type == 2:
        dst_type_subdir = general_config['inclmc_subdir']
    else:
        dst_type_subdir = general_config['mc_subdir']

    # find the analysis job option template file
    ana_job_option_dir = os.path.join(
        workarea, analysis_config['job_opt_template_subdir'])
    if job_opt_dir != '':
        ana_job_option_dir = job_opt_dir

    analysis_output_filename_base = analysis_config[
        'analysis_output_filename_base']

    ana_job_option_patterns = [analysis_output_filename_base]
    if job_opt_pattern != '':
        ana_job_option_patterns = [job_opt_pattern]
    print("Trying to find analysis job option template file...")
    ana_job_config['ana_job_option_template_path'] = find_file(
        ana_job_option_dir, ana_job_option_patterns, job_option_file_ext)

    # now try to parse algorithm name from analysis job option file
    algorithm_name = find_algorithm_name(ana_job_config)
    if algorithm != '' and algorithm not in algorithm_name:
        if not query_yes_no("Your specified algorithm name differs from the"
                            " found algorithm name in the jop option file:\n"
                            + str(algorithm) + " != " + algorithm_name +
                            "\nDo you want to continue?"):
            exit(0)

    # Search for dst files in the our data dir
    if dst_file_subdir == '':
        dst_file_subdir = config_data['simreco']['reco_output_subdir']
    dst_file_dir = create_directory_structure(
        datadir, [dst_type_subdir, dst_file_subdir], [str(Ecms)],
        use_energy_subdirs
    )
    print("Trying to find subdirectory containing dst files...")
    dst_decsubdir_name = find_dir(dst_file_dir, dst_dir_pattern)
    dst_file_dir = os.path.join(dst_file_dir, dst_decsubdir_name)
    dst_file_patterns = []
    if dst_file_pattern != '':
        dst_file_patterns.append(dst_file_pattern)

    # create output directory structure
    ana_subdir_order = analysis_config['analysis_output_dir_subdir_order']
    opt_ana_subdirs = []
    for opt in ana_subdir_order:
        if opt == "energy":
            opt_ana_subdirs.append(str(Ecms))
        elif opt == "algorithm":
            opt_ana_subdirs.append(algorithm_name)
        elif opt == "decayname":
            opt_ana_subdirs.append(dst_decsubdir_name)
    ana_output_dir = create_directory_structure(
        analysis_file_output_dir,
        [dst_type_subdir, analysis_config['analysis_output_subdir']],
        opt_ana_subdirs, use_energy_subdirs
    )
    ana_job_config['output_dir'] = ana_output_dir
    # now determine output filename
    analysis_filename_base = algorithm_name + '-' + dst_decsubdir_name
    if use_energy_subdirs:
        analysis_filename_base = analysis_output_filename_base
    ana_job_config['analysis_filename_base'] = analysis_filename_base

    create_reco_file_chunks(ana_job_config, dst_file_dir,
                            dst_file_patterns, files_per_job)

    ana_job_config['log_file_url'] = create_log_file_url(
        datadir, [dst_type_subdir],
        [str(Ecms), dst_decsubdir_name, algorithm_name]
    )

    ana_job_config_path = os.path.join(ana_output_dir, 'ana_job_config.json')
    print('creating ana job config file: ' + ana_job_config_path)
    with open(ana_job_config_path, 'w') as outfile:
        json.dump(ana_job_config, outfile, indent=4)
        outfile.close()

    return ana_job_config_path


def find_algorithm_name(ana_job_config):
    ana_jop_opt_file = ana_job_config['ana_job_option_template_path']
    with open(ana_jop_opt_file) as f:
        content = f.readlines()
        # now try to parse algorithm name from analysis job option file
        reg_exp = "^\s*ApplicationMgr.TopAlg\s*\+=\s*{\s*\"\s*(.*?)\s*\"\s*}\s*;\s*$"
        for line in content:
            result = search(reg_exp, line)
            if result:
                return result.group(1)
        raise ValueError(
            "Could not find algorithm statement ApplicationMgr.TopAlg += "
            "{...}; inside analysis job option file!"
        )


def create_reco_file_chunks(ana_job_config, rec_file_dir, rec_file_patterns,
                            files_per_job):
    print("Trying to find dst data files...")
    dst_data_files = find_files(rec_file_dir, rec_file_patterns, '.dst')

    redistribution_threshold = analysis_config[
        'chunk_redistribution_threshold']
    dst_file_chunks = create_file_chunks(dst_data_files, files_per_job,
                                         redistribution_threshold)

    ana_job_config['job_array_start_index'] = 1
    ana_job_config['job_array_last_index'] = len(dst_file_chunks)

    reco_chunk_file_path = os.path.join(ana_job_config['output_dir'],
                                        "dst_chunks.txt")
    write_dst_chunk_file(dst_file_chunks, ana_job_config, reco_chunk_file_path)


def write_dst_chunk_file(file_chunks, ana_job_config, reco_chunk_file_path):
    # write dst chunks file
    print('creating dst chunk file: ' + reco_chunk_file_path)
    with open(reco_chunk_file_path, "w") as outfile:
        index = 0
        for chunk in file_chunks:
            index = index + 1
            string = str(index) + ': {"' + chunk[0]
            for dstfile in chunk[1:]:
                string += '", "' + dstfile
            string += '"}\n'
            outfile.write(string)
        outfile.close()
    ana_job_config['reco_chunk_file_path'] = reco_chunk_file_path


def create_log_file_url(base_path, subdirs, opt_subdirs):
    new_subdirs = []
    if general_config['use_separate_log_dir']:
        new_subdirs.append(general_config['logfile_subdir'])
    new_subdirs.extend(subdirs)
    log_file_url = create_directory_structure(
        base_path, new_subdirs, opt_subdirs, use_energy_subdirs)
    log_filename = os.path.splitext(analysis_config['log_filename'])
    log_filename_base = create_filename_base(log_filename[0],
                                             opt_subdirs,
                                             use_energy_subdirs)
    log_file_url += '/' + log_filename_base + '-%a' + log_filename[1]
    return log_file_url


parser = argparse.ArgumentParser(
    description='Script for submission of Boss analysis jobs',
    formatter_class=SmartFormatter)

parser.add_argument('Ecms', metavar='Ecms', type=int, nargs=1)
parser.add_argument('--dst_dirname_pattern', metavar='dst_dirname_pattern',
                    type=str, default='')
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
                    '\n3 -- MC only\n')
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
                    ' the directory!'
                    )
parser.add_argument('--job_option_filename_pattern',
                    type=str,
                    default='',
                    help='Specify a filename pattern of the job option'
                    ' template file.')
parser.add_argument('--dump_job_options', default=False, action='store_true',
                    help='Instead of performing the analysis, the Boss options'
                    ' of the job with the\nlowest job array id are dumped.')
parser.add_argument('--testrun', default=False, action='store_true',
                    help='Submits job to development queue for test purposes.'
                    ' Your resource request will be ignored and a minimal set'
                    ' will be used.')

args = parser.parse_args()

Ecms = args.Ecms[0]

task_list = list(set(args.task_type))

if args.data_dir != '':
    datadir = args.data_dir
if not os.path.exists(datadir):
    raise FileNotFoundError("Did not find directory " + str(datadir))

analysis_job_config_paths = []
for i in task_list:
    analysis_job_config_paths.append(
        create_analysis_job_config(Ecms, i, args.algorithm,
                                   args.job_options_dir,
                                   args.job_option_filename_pattern,
                                   args.dst_dirname_pattern,
                                   args.dst_file_subdir,
                                   args.dst_file_pattern,
                                   args.files_per_job,
                                   datadir
                                   )
    )

flags_string = ''
if args.dump_job_options:
    flags_string += ' --dump_job_options'
if args.testrun:
    flags_string += ' --testrun'

for ana_job_config_path in analysis_job_config_paths:
    os.system('python3 ' + os.path.join(script_dir, 'ana_submit_script.py') +
              flags_string + " " + ana_job_config_path)
