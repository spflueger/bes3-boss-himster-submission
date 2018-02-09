#!/bin/sh

echo "using boss: ${application_path}"
jobopt="${job_option_dir}/${job_option_filename}${job_option_filename_index_delimiter}${PBS_ARRAYID}${job_option_file_ext}"
echo "using job options file: $jobopt"

echo "running boss..."
time ${application_path} $jobopt

exit 0