[![Test Status](https://travis-ci.com/spflueger/bes3-boss-himster-submission.svg?branch=master)](https://travis-ci.com/spflueger/bes3-boss-himster-submission)

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
1. Make sure the **boss_workarea_envname** and **boss_data_envname** you choose, exist as
environment variables.
2. Change the **application_path** variables to the path of your boss.exe executable
3. (optional) The simulation and reconstruction submission script includes a convenient feature for resubmission. It detects which of the output files already exist and have a file size
above a threshold. These jobs are automatically skipped (can be overwritten with the *--force* flag). Because the filesize of a job, depends on the analysis, 
it might be neccessary for you to modify the parameters **sim_min_filesize_per_event_in_kb** and **reco_min_filesize_per_event_in_kb** in the config file.
4. (optional) You make further changes in the config file to your preference, for example the himster log filename and job name (see **job_name** and **log_file_url**)
5. (optional) If you want to run the scripts from any directory, make sure that this 
directory is in the in the *$PATH* environment variable

Thats it! Now just run the your version of submit scripts

### File Naming Conventions
Currently there are certain conditions on the job option template filenames, in order that the scripts work correctly.
- the analysis job option template files, should contain "ana" and depending on which kind of data that is analysed "mc", "data" or "inclMc"
- ...

### Usage
Generally, use the *-h* or *--help* flags in the python script calls for more information.

For simulations and reconstruction simply call the **simreco_submit_script.py** script with the corresponding arguments.

For analysis use the **create_ana_job.py** script, when running a job for the first time. It will generate a job option file and automatically use this file in the analysis job submission.
If you want to resubmit an analysis job, use the **ana_submit_script.py** with analysis job option files as arguments.

### Updating
When a new version of the submission tools are available, the following steps show how the update is performed easieast.
It is a assumed you are in the directory of the cloned git repository

1. Run `git stash`, which "saves" your local changes (should only be config.json, you can verify this with `git status`)
2. Run `git pull`, which performs the update from the main repository
3. Run `git stash apply`. This applies your local changes on the updated code. Here merge conflicts may appear, which you should check carefully.
