# bes3-boss-himster-submission
Submission scripts for the boss software for the HIMster2.
It avoids making any unneccesary intermediate job option and script files! It also offers some convenient control features.

### Installation
Clone the repository with `git clone <this_repo_url>` on the himster2. Then you can easily get updates.
Thats all.

### File Overview
All of these files have to reside on the himster2 of course...
- *himster2.py* and *general.py*: are two small python files which take care of himster job submission and help finding files in directories
- *config.json*: Configuration file, which contains variables used by the submission scripts for steering and defining your default behaviour.
- *create_ana_job.py*: Creates an analysis job option file. Afterwards it automatically calls the *ana_submit_script.py* submission script with the created analysis job option file.
- *ana_submit_script.py*: The analysis job submission script, accepts analysis job option files as arguments. This can be used to easily resubmit certain jobs.
- *simreco_submit_script.py*: The simulation and reconstruction submission script.

### Initial Setup:
Before you can run the scripts you need to make a change in the **config.json** file:
1. Make sure the *boss_workarea_envname* and *boss_data_envname* you choose, exist as
environment variables.
2. Change the **application_path** variables to the path of your boss.exe executable
3. (optional) You make further changes in the config file to your preference, for example the himster log filename and job name (see **job_name** and **log_file_url**)
4. (optional) If you want to run the scripts from any directory, make sure that this 
directory is in the in the *$PATH* environment variable

Thats it! Now just run the your version of submit scripts

### Usage
Generally, use the *-h* or *--help* flags in the python script calls for more information.

For simulations and reconstruction simply call the **simreco_submit_script.py** script with the corresponding arguments.

For analysis use the **create_ana_job.py** script, when running a job for the first time. It will generate a job option file and automatically use this file in the analysis job submission.
If you want to resubmit an analysis job, use the **ana_submit_script** with analysis job option files as arguments.
