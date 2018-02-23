#!/usr/bin/python3

import os

import argparse

datadir = os.environ["BOSSDATA"]
workarea = os.environ["BOSSWORKAREA"]

parser = argparse.ArgumentParser(
    description='Script for creation of boss job option files (bes3)',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('Ecms', type=int, nargs=1,
                    help='CMS energy in MeV')
parser.add_argument('events_per_job', type=int, nargs=1,
                    help='events per job')
parser.add_argument('job_index', metavar='job_index',
                    type=int, nargs=1,
                    help='index of the job, which is used in filenames'
                    ' and as the seed')
parser.add_argument('task_type',
                    type=int,
                    choices=range(1, 4),
                    help='Type of task:'
                    '\n1 -- simulation only'
                    '\n2 -- reconstruction only'
                    '\n3 -- both (default)')
parser.add_argument('sim_job_option_template_path', type=str, nargs=1)
parser.add_argument('rec_job_option_template_path', type=str, nargs=1)
parser.add_argument('simrec_job_opt_dir', type=str, nargs=1)
parser.add_argument('digi_root_dir', type=str, nargs=1)
parser.add_argument('dst_output_dir', type=str, nargs=1)
parser.add_argument('job_option_filename_index_delimiter', type=str, nargs=1)
parser.add_argument('job_option_file_ext', type=str, nargs=1)
parser.add_argument('dec_files', metavar='dec_files', type=str, nargs='*',
                    help='list of decay files')            

args = parser.parse_args()

Ecms = args.Ecms[0]

RndTrg = ""
# Himster uses different queue name and different dir for Random Trigger Data
if "himster" in os.environ["HOSTNAME"]:
    RndTrg = "MixerAlg.ReplaceDataPath = \"/data/group/bes3/bes3data/offline/data/randomtrg/\";"

for dec_file_path in args.dec_files:
    if not os.path.isfile(dec_file_path):
        raise FileNotFoundError('Decay file ' + dec_file_path + ' not found!')

    base = os.path.splitext(dec_file)[0]

    job_options_file_names = ["jobOptions_sim", "jobOptions_rec"]
    if args.isr:
        temp_list = []
        for file_name in job_options_file_names:
            temp_list.append(file_name + "_isr")
        job_options_file_names = temp_list
        base = base + "_isr"

    job_options_file_names[0] = job_options_file_names[0] + "_" + str(Ecms)

    job_options_file_paths = []
    for file_name in job_options_file_names:
        file_name = file_name + ".txt"
        job_options_file_paths.append(os.path.join(
            job_opt_dir, file_name))

        if not os.path.isfile(job_options_file_paths[-1]):
            raise FileNotFoundError('Job option file ' +
                                    job_options_file_paths[-1] +
                                    ' not found!')

    seed = job_index
    if args.task == 1 or args.task == 3:
        # Create the simulation card
        outfilename = simrec_job_opt_dir + "/sim_" + str(base) + "_" \
            + str(Ecms) + "-" \
            + str(job_index) + ".txt"
        with open(outfilename, "w") as out_file:
            out_file.write("#include \"" +
                            str(job_options_file_paths[0]) + "\";")
            out_file.write("\nEvtDecay.PdtTableDir = \"" +
                            str(pdt_table_path) + "\";")
            out_file.write(
                "\nEvtDecay.userDecayTableName = \"" +
                str(dec_file_path) + "\";")
            out_file.write("\nBesRndmGenSvc.RndmSeed = " + str(seed) + ";")
            temp_rtraw_filename = base + "_" + \
                str(Ecms) + "-" + str(job_index) + ".rtraw"
            out_file.write("\nRootCnvSvc.digiRootOutputFile = \"" +
                            str(os.path.join(digi_root_dir,
                                            temp_rtraw_filename)) + "\";")
            out_file.write("\nApplicationMgr.EvtMax = " +
                            str(args.number_of_events) + ";")
            out_file.close()

    if args.task == 2 or args.task == 3:
        # Create the reconstruction card
        outfilename = simrec_job_opt_dir + "/rec_" + \
            str(base) + "_" + str(Ecms) + "-" + str(job_index) + ".txt"
        with open(outfilename, "w") as out_file:
            out_file.write("#include \"" +
                            str(job_options_file_paths[1]) + "\";")
            out_file.write("\n" + str(RndTrg))
            out_file.write("\nBesRndmGenSvc.RndmSeed = " + str(seed) + ";")
            temp_rtraw_filename = base + "_" + \
                str(Ecms) + "-" + str(job_index) + ".rtraw"
            out_file.write("\nEventCnvSvc.digiRootInputFile = \"" +
                            str(os.path.join(digi_root_dir,
                                            temp_rtraw_filename)) + "\";")
            temp_dst_filename = base
            if not use_energy_subdir_for_dsts:
                temp_dst_filename = temp_dst_filename + "_" + str(Ecms)
            temp_dst_filename = temp_dst_filename + \
                "-" + str(job_index) + ".dst"
            out_file.write("\nEventCnvSvc.digiRootOutputFile = \"" +
                            str(os.path.join(dst_output_dir,
                                            temp_dst_filename)) + "\";")
            out_file.write("\nApplicationMgr.EvtMax = " +
                            str(args.number_of_events) + ";")
            out_file.close()