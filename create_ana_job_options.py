#!/usr/bin/python3

from os import sys, environ, path

import argparse


possible_energies = {4230: 4.22626,
                     4260: 4.25797,
                     4360: 4.35826,
                     4420: 4.41558,
                     4600: 4.600
                     }

datadir = os.environ["MYDATA"]
workarea = os.environ["WORKAREA"]
#workarea = os.environ["MYANAPKGROOT"]

parser = argparse.ArgumentParser(
    description='Script for creation of boss job option files (bes3)',
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('Ecms', metavar='Ecms', type=int, nargs=1,
                    choices=[x for x, y in possible_energies.items()])

parser.add_argument('--task', metavar='task', type=int, default=3,
                    choices=range(1, 6),
                    help='Possible tasks are:'
                    '\n1 -- simulation only'
                    '\n2 -- reconstruction only'
                    '\n3 -- both (default)')

parser.add_argument('--files_per_job', metavar='files_per_job',
                    type=int, default=60)
parser.add_argument('--algorithm', metavar='algorithm',
                    type=str, default='')
parser.add_argument('--subdir', metavar='subdir', type=str, default='')
parser.add_argument('--AltTop', metavar='AltTop', type=str, default='')
parser.add_argument('--filter', metavar='filter', type=str, default='')

args = parser.parse_args()


if args.files_per_job < 1:
    parser.print_help()
    sys.exit(1)

old_top = ''
# Change top_dir if wanted
if len(args.AltTop) and path.exists(args.AltTop):
    old_top = top_dir
    top_dir = args.AltTop

# create the name of the job option file to use
job_option_file = workarea + '/run/ana-' + args.algorithm
base_name = args.Ecms[0] + '_' + args.algorithm
if args.task == 1:
    $baseName . = "_data"
    $eventDir = "${TopDir}/data/${Ecms}"
    $jobOptionFile . = "_data"
elif args.task == 2:  # eventDir for generic MC
    $baseName . = "_inclMc"
    $eventDir = "${TopDir}/inclMc/${Ecms}"
    $jobOptionFile . = "_mc"
elif args.task == 3:  # eventDir for my MC
    $baseName . = "_mc"
    $eventDir = "${TopDir}/mc/${Ecms}"
    $jobOptionFile . = "_mc"

if (length $AltTop) {$TopDir = $OldTop
                     }

if not path.exists(args.AltTop):
    raise FileNotFoundError("Did not find job option template "
                            + str(job_option_file))

if (length $subdir) {$baseName . = "-" . $subdir
                     $baseName = ~ s | / | - | $subdir = "/" . $subdir
                     }
# Search for dst files in the our event dir
my % inputDataFiles
my @totalFiles = `find - L $eventDir$subdir - name "*${filter}*.dst"`
chomp(@totalFiles)
my $addedFiles = 0

my $toAdd = @totalFiles

print "Found $toAdd dst files\n"

# split list of files in small groups of $filesPerJob files
# and format them directly as string for the final job
# option files.
my $i = 1
foreach my $file(@totalFiles){
    if($addedFiles <= $filesPerJob){$inputDataFiles{$i} . = "\"$file\""
                                    $toAdd - -
                                    $addedFiles + +
                                    }

    if($addedFiles < $filesPerJob & & $toAdd){$inputDataFiles{$i} . = ", \n"
                                              }

    if($addedFiles == $filesPerJob & & $toAdd){$addedFiles = 0
                                               $i + +
                                               }

}

my $numJobFiles = 0

my $template = `sed - e "s/__ECMS__/$Energies{$Ecms}/g" $jobOptionFile`

# create the job options files
foreach my $i(sort keys % inputDataFiles){
    open(FILE, ">", "$TopDir/jobs/$baseName-$i.txt")
    print FILE << INLINE_LITERAL_TEXT
    $template
    EventCnvSvc.digiRootInputFile = {$inputDataFiles{$i}
                                     }
    NTupleSvc.Output = {
        "FILE88 DATAFILE='$TopDir/root/$baseName-$i.root' OPT='NEW' TYP='ROOT'"}
    INLINE_LITERAL_TEXT
    close FILE
  $numJobFiles + +
}
