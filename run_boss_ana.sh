#!/bin/sh

sleep 5s

if [ -z ${dump_job_options+x} ]; then
    tmp_outdir=`mktemp -d --tmpdir=/localscratch/${SLURM_JOB_ID}/`
else
    tmp_outdir=$(dirname "${ana_job_option_template_path}")
fi

JOBID=${SLURM_ARRAY_TASK_ID}

root_filename="${tmp_outdir}/${root_filename_base}-${JOBID}.root"

# Create the reconstruction card
ana_job_option_filename="ana_$JOBID.txt"
jobopt="${tmp_outdir}/${ana_job_option_filename}"

input_data_files=`cat ${dst_chunk_file_path} | sed -n "s/^\s*$JOBID\s*:\s*{\(.*\)}\s*$/\1/p" | sed -e "s/\s*,\s*/,\n/g"`
template=`cat ${ana_job_option_template_path}`
cat << EOT > $jobopt
$template
EventCnvSvc.digiRootInputFile = {${input_data_files}
                                };
NTupleSvc.Output = {
"FILE88 DATAFILE='${root_filename}' OPT='NEW' TYP='ROOT'"};
EOT

echo "using job options file: $jobopt"
cat $jobopt
if [ -z ${dump_job_options+x} ]; then
    echo "using boss: ${application_path}"
    time ${application_path} $jobopt

    mv ${root_filename} ${output_dir}/.
    rm -rf ${tmp_outdir}
fi

exit 0
