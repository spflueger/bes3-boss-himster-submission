# bes3-boss-himster-submission
submission scripts for the boss software for the himster

### Overview
All of these files have to reside on the himster of course...
- *himster.py* and *general.py*: are two small python files which take care of himster job submission and help finding files in directories
- *example_submit_script.py*: as the name suggest... An example himster submission script. Should work out of the box, after two simple modifications (see steps 1 and 2 below)
- *run_boss_ana.sh*: shell script, which is executed on the himster for each individual job and calls boss.exe

### Usage:
0. If you like copy the *example_submit_script.py*
1. Inside the *example_submit_script.py* change the **application_path** variable to the path of your boss.exe executable
2. Inside the *example_submit_script.py* change the job option file extension (see **job_option_file_ext**) and the delimiter characters between the base filename and the index/arrayid of the job option file (see **job_option_filename_index_delimiter**)
3. (optional) Inside the *example_submit_script.py*, you can also change the himster log filename and job name (see **job_name** and **log_file_url**)

Thats it. Now just run the your version of submit script via 
`./example_submit_script.py <path-to-directory-containing-job-option-files>`

