#!/bin/sh

echo "using boss: ${application_path}"
jobopt="${job_option_dir}/${job_option_filename}_${PBS_ARRAYID}${job_option_file_ext}"
echo "using job options file: $jobopt"

echo "running boss..."
time ${application_path} $jobopt

exit 0