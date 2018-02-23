# bes3-boss-himster-submission
Submission scripts for the boss software for the HIMster.
It avoids making any unneccesary intermediate job option and script files!

### Installation
Clone the repository with `git clone <this_repo_url>`. Then you can easily get updates.
Thats all.

### Overview
All of these files have to reside on the himster of course...
- *himster.py* and *general.py*: are two small python files which take care of himster job submission and help finding files in directories
- *config.json*: Configuration file, which contains variables used by the submission scripts for steering and defining your default behaviour.
- *ana_submit_script.py*: The himster analysis job submission script. Should work out of the box, after two simple steps (see Usage below).
- *simreco_submit_script.py*: The himster simulation and reconstruction submission script. This should work out of the box as well, once the same modifications as in the config file have been made.

### Usage:
Before you can run the scripts you need to make a change in the **config.json** file:
1. Make sure the *boss_workarea_envname* and *boss_data_envname* you choose, exist as
environment variables.
2. Change the **application_path** variables to the path of your boss.exe executable
3. (optional) You make further changes in the config file to your preference, for example the himster log filename and job name (see **job_name** and **log_file_url**)
4. (optional) If you want to run the scripts from any directory, make sure that this 
directory is in the in the *$PATH* environment variable

Thats it! Now just run the your version of submit scripts