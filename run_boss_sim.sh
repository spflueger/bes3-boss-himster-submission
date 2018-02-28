#!/bin/sh

is_himster=1

# first create job option files
temp_outdir=`mktemp -d --tmpdir=/local/scratch`
JOBID=${PBS_ARRAYID}

rtraw_filepath="${rtraw_filepath_base}${JOBID}.rtraw"
dst_filepath="${dst_filepath_base}${JOBID}.dst"

tmp_rtraw_filepath="${temp_outdir}/digi-${JOBID}.rtraw"
tmp_dst_filepath="${temp_outdir}/reco-${JOBID}.dst"

echo "task type: $task_type"
echo "using boss: ${application_path}"

# check if we run simulation
if [[ "$task_type" -eq 1 || "$task_type" -eq 3 ]]; then
    # Create the simulation card
    sim_job_option_filename="sim_$Ecms-$JOBID.txt"
    outfilename="${temp_outdir}/${sim_job_option_filename}"

echo "#include \"${sim_job_option_template_path}\"" > $outfilename
if [[ -f ${pdt_table_path} ]]; then
    echo "EvtDecay.PdtTableDir = \"${pdt_table_path}\";" >> $outfilename
fi
cat << EOT >> $outfilename
EvtDecay.userDecayTableName = "$dec_file_path";
BesRndmGenSvc.RndmSeed = $JOBID;
RootCnvSvc.digiRootOutputFile = "$tmp_rtraw_filepath";
ApplicationMgr.EvtMax = $events_per_job;
EOT

    jobopt="${temp_outdir}/${sim_job_option_filename}"
    echo "using job options file: $jobopt"
    cat $jobopt
    time boss.exe $jobopt
fi

# check if we run also reconstruction
if [[ "$task_type" -eq 2 || "$task_type" -eq 3 ]]; then
    RndTrg=""
    # Himster uses different queue name and different dir for Random Trigger Data
    if [ ${is_himster} ]; then
        RndTrg="MixerAlg.ReplaceDataPath = \"/data/group/bes3/bes3data/offline/data/randomtrg/\";"
    fi

    rec_job_option_filename="rec_$Ecms-$JOBID.txt"
    outfilename="$temp_outdir/$rec_job_option_filename"

    rtraw_path_used=$rtraw_filepath
    if [[ "$task_type" -eq 1 || "$task_type" -eq 3 ]]; then
        rtraw_path_used=$tmp_rtraw_filepath
    fi

cat << EOT > $outfilename
#include "$rec_job_option_template_path"
$RndTrg
BesRndmGenSvc.RndmSeed = $JOBID;
EventCnvSvc.digiRootInputFile = {"$rtraw_path_used"};
EventCnvSvc.digiRootOutputFile = "$tmp_dst_filepath";
ApplicationMgr.EvtMax = $events_per_job;
EOT

    jobopt="${temp_outdir}/${rec_job_option_filename}"
    echo "using job options file: $jobopt"
    cat $jobopt
    # additionally check if the required files from the simulation exist
    if [ -f "$rtraw_filepath" ]; then
        echo "rtraw file exists! Running boss.exe ..."
        time boss.exe $jobopt
    else
        echo "ERROR: could not find rtraw $input_filepath which is needed for the reconstruction!"
    fi
fi

if [[ "$task_type" -eq 1 || "$task_type" -eq 3 ]]; then
    mv $tmp_rtraw_filepath $rtraw_filepath
fi
mv $tmp_dst_filepath $dst_filepath

rm -rf $temp_outdir

exit 0