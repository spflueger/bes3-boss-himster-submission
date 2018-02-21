#!/usr/bin/python3

import os

import argparse


datadir = os.environ["MYDATA"]
workarea = os.environ["WORKAREA"]


dec_file_dir = os.path.join(workarea, 'run/decfiles/')
job_opt_dir = os.path.join(workarea, 'run/recSimOptions/')
pdt_table_path = os.path.join(workarea, 'run/pdt.table')
digi_root_dir = os.path.join(datadir, 'mc/generated/rtraw/')
dst_output_dir = os.path.join(datadir, 'mc/generated/dst/')


parser = argparse.ArgumentParser(
    description='Script for submission of Boss analysis jobs',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('number_of_jobs', metavar='number_of_jobs',
                    type=int, nargs=1,
                    help='number of jobs per decay file')
parser.add_argument('Ecms', metavar='Ecms', type=int, nargs=1,
                    help='CMS energy in MeV')
parser.add_argument('dec_files', metavar='dec_files', type=str, nargs='+',
                    help='list of decay files')

parser.add_argument('--number_of_events', metavar='number_of_events',
                    type=int, default=10000)
parser.add_argument('--start_job_index', metavar='start_job_index',
                    type=int, default=1)
parser.add_argument('--task', metavar='task', type=int, default=3,
                    choices=range(1, 4),
                    help='Possible tasks are:'
                    '\n1 -- simulation only'
                    '\n2 -- reconstruction only'
                    '\n3 -- both (default)')
parser.add_argument('--isr', default=False,
                    action='store_true',
                    help='Use top job option file with ISR correction enabled.'
                    '\nFor this option to work, there has to be a template job'
                    '\noption file with the name'
                    '\n$MYANAPKGROOT/run/jopOptions_sim_isr_$Ecms.txt.'
                    '\nThe default template should have ISR correction '
                    'disabled'
                    '\nin KKMC (otherwise this option is useless).')

args = parser.parse_args()


RndTrg = ""
# Himster uses different queue name and different dir for Random Trigger Data
if "himster" in os.environ["HOSTNAME"]:
    RndTrg = 'MixerAlg.ReplaceDataPath = '
    '\"/data/group/bes3/bes3data/offline/data/randomtrg/\";'


Ecms = args.Ecms[0]

for dec_file in args.dec_files:
    dec_file_path = os.path.join(dec_file_dir, dec_file)
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

    for job_index in range(args.start_job_index, args.number_of_jobs[0] + 1):
        seed = job_index
        if args.task == 1 or args.task == 3:
            # Create the simulation card
            outfilename = "sim_" + str(base) + "_" \
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
            outfilename = "rec_" + str(base) + "_" \
                + str(Ecms) + "-" \
                + str(job_index) + ".txt"
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
                temp_dst_filename = base + "_" + \
                    str(Ecms) + "-" + str(job_index) + ".dst"
                out_file.write("\nEventCnvSvc.digiRootOutputFile = \"" +
                               str(os.path.join(dst_output_dir,
                                                temp_dst_filename)) + "\";")
                out_file.write("\nApplicationMgr.EvtMax = " +
                               str(args.number_of_events) + ";")
                out_file.close()
