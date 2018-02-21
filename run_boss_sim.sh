#!/bin/sh


echo "using boss: ${application_path}"

# check if we run simulation
if [ "${sim_job_option_filename_base}" != "" ]; then
    jobopt="${sim_job_option_dir}/${sim_job_option_filename_base}${job_option_filename_index_delimiter}${PBS_ARRAYID}${job_option_file_ext}"
    echo "using job options file: $jobopt"
    time boss.exe $jobopt
fi

# check if we run also reconstruction
if [ "${rec_job_option_filename_base}" != "" ]; then
    jobopt="${rec_job_option_dir}/${sim_job_option_filename_base}${job_option_filename_index_delimiter}${PBS_ARRAYID}${job_option_file_ext}"
    echo "using job options file: $jobopt"
    input_filepath=`cat $jobopt | grep EventCnvSvc.digiRootInputFile | awk '{print $3}' | sed 's/;//'`
    # additionally check if the required files from the simulation exist
    if [ -f "input_filepath" ]; then
        echo "rtraw file exists! Running boss.exe ..."
        time boss.exe $jobopt
    fi
fi

exit 0


