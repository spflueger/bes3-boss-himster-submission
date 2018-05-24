#!/bin/sh

sleep 5s

is_himster=1
if [[ -z "$SLURM_JOB_ID" ]]; then
    is_himster=0
fi

# first create job option files
if [[ "${is_himster}" -eq 1 ]]; then
    JOBID=${SLURM_ARRAY_TASK_ID}
else
    echo "this seems to be no valid cluster environment"
    exit 1
fi

if [ -z ${dump_job_options+x} ]; then
    temp_outdir=`mktemp -d --tmpdir=/localscratch/${SLURM_JOB_ID}/`
    cd ${temp_outdir}
else
    temp_outdir=$(dirname "${sim_job_option_template_path}")
fi

if [[ "${extra_file}" != "" ]] && [[ -f ${extra_file} ]]; then
    cp ${extra_file} ${temp_outdir}/.
fi

rtraw_filepath="${rtraw_filepath_base}${JOBID}.rtraw"
dst_filepath="${dst_filepath_base}${JOBID}.dst"

if [ -z ${dump_job_options+x} ]; then
    tmp_rtraw_filepath="${temp_outdir}/digi-${JOBID}.rtraw"
    tmp_dst_filepath="${temp_outdir}/reco-${JOBID}.dst"
else
    tmp_rtraw_filepath=${rtraw_filepath}
    tmp_dst_filepath=${dst_filepath}
fi

echo "task type: $task_type"
echo "using boss: ${application_path}"

# check if we run simulation
if [[ "$task_type" -eq 1 || "$task_type" -eq 3 ]]; then
    # random seed calculation
    sim_random_seed=$(($random_seed+$SLURM_ARRAY_TASK_ID))

    # Create the simulation card
    sim_job_option_filename="sim_$Ecms-$JOBID.txt"
    outfilename="${temp_outdir}/${sim_job_option_filename}"

echo "#include \"${sim_job_option_template_path}\"" > $outfilename
if [[ -f ${pdt_table_path} ]]; then
    echo "EvtDecay.PdtTableDir = \"${pdt_table_path}\";" >> $outfilename
fi
cat << EOT >> $outfilename
EvtDecay.userDecayTableName = "$dec_file_path";
BesRndmGenSvc.RndmSeed = $sim_random_seed;
RootCnvSvc.digiRootOutputFile = "$tmp_rtraw_filepath";
ApplicationMgr.EvtMax = $events_per_job;
EOT

    jobopt="${temp_outdir}/${sim_job_option_filename}"
    echo "using job options file: $jobopt"
    cat $jobopt
    if [ -z ${dump_job_options+x} ]; then
        time ${application_path} $jobopt
    fi
fi

# check if we run also reconstruction
if [[ "$task_type" -eq 2 || "$task_type" -eq 3 ]]; then
    # random seed calculation
    rec_random_seed=$(($random_seed+$SLURM_ARRAY_TASK_ID))

    RndTrg=""
    # Himster uses different queue name and different dir for Random Trigger Data
    if [ ${is_himster} ]; then
        RndTrg="MixerAlg.ReplaceDataPath = \"${himster2_randomtrg_path}\";"
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
BesRndmGenSvc.RndmSeed = $rec_random_seed;
EventCnvSvc.digiRootInputFile = {"$rtraw_path_used"};
EventCnvSvc.digiRootOutputFile = "$tmp_dst_filepath";
ApplicationMgr.EvtMax = $events_per_job;
EOT

    jobopt="${temp_outdir}/${rec_job_option_filename}"
    echo "using job options file: $jobopt"
    cat $jobopt
    if [ -z ${dump_job_options+x} ]; then
        # additionally check if the required files from the simulation exist
        if [ -f "$rtraw_path_used" ]; then
            echo "rtraw file exists! Running boss.exe ..."
            time ${application_path} $jobopt
        else
            echo "ERROR: could not find rtraw $input_filepath which is needed for the reconstruction!"
        fi
    fi
fi

if [ -z ${dump_job_options+x} ]; then
    if [[ "$task_type" -eq 1 || "$task_type" -eq 3 ]]; then
        mv $tmp_rtraw_filepath $rtraw_filepath
    fi
    mv $tmp_dst_filepath $dst_filepath

    rm -rf $temp_outdir
fi

exit 0