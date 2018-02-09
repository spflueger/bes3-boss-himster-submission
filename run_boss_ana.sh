#!/bin/sh

echo "running the boss.exe here!"
echo "$application_path"

filename="${job_option_dir}/${job_option_filename}_${PBS_ARRAYID}${job_option_file_ext}"
echo "job option file url $filename"

exit 0