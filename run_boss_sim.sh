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

echo "task type: $task_type"
echo "using boss: ${application_path}"

# check if we run simulation
if [[ "$task_type" -eq 1 || "$task_type" -eq 3 ]]; then
    # random seed calculation
    sim_random_seed=$(($random_seed+$JOBID))

    # create sim output dir and filename
    sim_filepath="${sim_file_dir}/${sim_filename_base}-evts_${events_per_job}-rndseed_${sim_random_seed}.rtraw"
    if [ -z ${dump_job_options+x} ]; then
        temp_outdir="/localscratch/${SLURM_JOB_ID}"
        cd ${temp_outdir}
        tmp_sim_filepath="${temp_outdir}/sim-${JOBID}.rtraw"
    else
        temp_outdir=${sim_file_dir}
        tmp_sim_filepath=${sim_filepath}
    fi

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
RootCnvSvc.digiRootOutputFile = "$tmp_sim_filepath";
ApplicationMgr.EvtMax = $events_per_job;
EOT

    jobopt="${temp_outdir}/${sim_job_option_filename}"
    echo "using job options file: $jobopt"
    cat $jobopt
    if [ -z ${dump_job_options+x} ]; then
        # copy extra files if needed
        if [[ "${extra_file}" != "" ]] && [[ -f ${extra_file} ]]; then
            cp ${extra_file} ${temp_outdir}/.
        fi
        time ${application_path} $jobopt
        cp $tmp_sim_filepath $sim_filepath
    fi
fi

# check if we run also reconstruction
if [[ "$task_type" -eq 2 || "$task_type" -eq 3 ]]; then
    # random seed calculation
    rec_random_seed=$(($random_seed+$JOBID))

    # create sim output dir and filename
    reco_filepath="${reco_file_dir}/${reco_filename_base}-evts_${events_per_job}-rndseed_${rec_random_seed}.dst"
    if [ -z ${dump_job_options+x} ]; then
        temp_outdir="/localscratch/${SLURM_JOB_ID}"
        cd ${temp_outdir}
        tmp_reco_filepath="${temp_outdir}/reco-${JOBID}.dst"
    else
        temp_outdir=${reco_file_dir}
        tmp_reco_filepath=${reco_filepath}
    fi

    RndTrg=""
    # Himster uses different queue name and different dir for Random Trigger Data
    if [ ${is_himster} ]; then
        RndTrg="MixerAlg.ReplaceDataPath = \"${himster2_randomtrg_path}\";"
    fi

    rec_job_option_filename="rec_$Ecms-$JOBID.txt"
    outfilename="$temp_outdir/$rec_job_option_filename"

    sim_path_used=$sim_filepath
    if [[ "$task_type" -eq 1 || "$task_type" -eq 3 ]]; then
        sim_path_used=$tmp_sim_filepath
    fi

cat << EOT > $outfilename
#include "$rec_job_option_template_path"
$RndTrg
BesRndmGenSvc.RndmSeed = $rec_random_seed;
EventCnvSvc.digiRootInputFile = {"$sim_path_used"};
EventCnvSvc.digiRootOutputFile = "$tmp_reco_filepath";
ApplicationMgr.EvtMax = $events_per_job;
EOT

    jobopt="${temp_outdir}/${rec_job_option_filename}"
    echo "using job options file: $jobopt"
    cat $jobopt
    if [ -z ${dump_job_options+x} ]; then
        # additionally check if the required files from the simulation exist
        if [ -f "$sim_path_used" ]; then
            echo "sim file exists! Running boss.exe ..."
            time ${application_path} $jobopt
            cp $tmp_reco_filepath $reco_filepath
        else
            echo "ERROR: could not find sim file $sim_path_used which is needed for the reconstruction!"
        fi
    fi
fi

if [ -z ${dump_job_options+x} ]; then
    rm -rf $temp_outdir
fi

exit 0