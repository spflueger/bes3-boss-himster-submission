# bes3-boss-himster-submission
submission scripts for the boss software for the himster

### Installation
Clone the repository with `git clone <this_repo_url>`. Then you can easily get updates.
Thats all.

### Overview
All of these files have to reside on the himster of course...
- *himster.py* and *general.py*: are two small python files which take care of himster job submission and help finding files in directories
- *example_submit_script.py*: as the name suggest... An example himster submission script. Should work out of the box, after two simple modifications (see steps 1 and 2 below). This
can be used to submit a single boss task with one job option file per job.
- *run_boss_ana.sh*: shell script, which is executed on the himster for each individual job and calls boss.exe
- *create_sim_reco_job_options.py*: this script generates job option files needed for simulation and reconstruction runs.
- *simreco_submit_script.py*: this script is based on the example_submit_script.py above but
is modified for the use of simulation and reconstruction with boss. This should work out of the box as well, once the same modifications as in the example script above have been made.
- *run_boss_sim.sh*: a shell script that is used by the simreco_submit_script.py.

### Usage:
0. (optional) If you like copy the *example_submit_script.py*
1. Inside the *example_submit_script.py* change the **application_path** variable to the path of your boss.exe executable
2. Inside the *example_submit_script.py* change the job option file extension (see **job_option_file_ext**) and the delimiter characters between the base filename and the index/arrayid of the job option file (see **job_option_filename_index_delimiter**)
3. (optional) Inside the *example_submit_script.py*, you can also change the himster log filename and job name (see **job_name** and **log_file_url**)
4. (optional) If you want to run the scripts from any directory, make sure that this 
directory is in the in the *$PATH* environment variable

Thats it! Now just run the your version of submit script via 
`./example_submit_script.py <path-to-directory-containing-job-option-files>`

