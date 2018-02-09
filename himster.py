import os
import subprocess
from time import time, sleep


def get_num_jobs_on_himster():
    '''
    check number of jobs currently running or in queue on himster
    (only this user, so you!)
    '''
    bashcommand = 'qstat -t | wc -l'
    returnvalue = subprocess.Popen(
        bashcommand, shell=True, stdout=subprocess.PIPE)
    out, err = returnvalue.communicate()
    return int(out)


def is_executable(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def is_cluster_environment():
    program = 'qsub'
    is_cluster = False
    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        exe_file = os.path.join(path, program)
        if is_executable(exe_file):
            is_cluster = True
            break
    return is_cluster


class JobResourceRequest:
    def __init__(self, walltime_in_minutes):
        self.walltime_string = self.format_walltime(walltime_in_minutes)
        self.number_of_nodes = 1
        self.processors_per_node = 1
        self.memory_in_mb = 1000
        self.virtual_memory_in_mb = 1000
        self.node_scratch_filesize_in_mb = 0

    def format_walltime(self, walltime_in_minutes):
        walltime_string = str(int(int(walltime_in_minutes) / 60)) + ':'
        walltime_string = walltime_string + str(int(walltime_in_minutes) % 60)
        if int(walltime_in_minutes) % 60 < 10:
            walltime_string = walltime_string + '0'
        walltime_string = walltime_string + ':00'
        return walltime_string

    def get_submit_string(self):
        resource_request = ' -l nodes=' + str(self.number_of_nodes) \
            + ':ppn=' + str(self.processors_per_node) \
            + ',mem=' + str(self.memory_in_mb) \
            + 'mb,vmem=' + str(self.virtual_memory_in_mb) + 'mb'\
            + ',walltime=' + self.walltime_string
        if self.node_scratch_filesize_in_mb > 0:
            resource_request = resource_request + ',file=' + \
                str(self.node_scratch_filesize_in_mb) + 'mb'
        return resource_request


class Job:
    def __init__(self,
                 job_resource_request,
                 application_url,
                 jobname,
                 logfile_url):
        self.resource_request = job_resource_request
        self.application_url = str(application_url)
        self.jobname = str(jobname)
        self.logfile_url = str(logfile_url)
        self.job_array_index_low = 1
        self.job_array_index_high = 1
        self.exported_user_variables = {}

    def set_job_array_size(self, job_array_index_low, job_array_index_high):
        self.job_array_index_low = int(job_array_index_low)
        self.job_array_index_high = int(job_array_index_high)

    def add_exported_user_variable(self, name, value):
        self.exported_user_variables[str(name)] = str(value)

    def create_bash_commands(self, max_jobarray_size):
        bashcommand_list = []
        for job_index in range(self.job_array_index_low,
                               self.job_array_index_high + 1,
                               max_jobarray_size):
            bashcommand = 'qsub'
            if self.job_array_index_high > self.job_array_index_low:
                bashcommand = bashcommand + ' -t ' + str(job_index) + '-' \
                    + str(min(job_index + max_jobarray_size - 1,
                              self.job_array_index_high))
            bashcommand = bashcommand + ' -N ' + self.jobname + \
                self.resource_request.get_submit_string() + ' -j oe -o ' \
                + self.logfile_url
            if len(self.exported_user_variables) > 0:
                bashcommand = bashcommand + ' -v '
                counter = 0
                for name, value in self.exported_user_variables.items():
                    counter = counter + 1
                    bashcommand = bashcommand + name + '="' + value + '"'
                    if counter < len(self.exported_user_variables):
                        bashcommand = bashcommand + ','
            bashcommand = bashcommand + ' -V ' + self.application_url
            bashcommand_list.append(bashcommand)

        return bashcommand_list


class HimsterJobManager:
    def __init__(self, himster_total_job_threshold=1600,
                 resubmit_wait_time_in_seconds=1800,
                 max_jobarray_size=100):
        self.job_command_list = []
        # user total job threshold
        self.himster_total_job_threshold = himster_total_job_threshold
        # max number of jobs within a job array on himster (atm 100)
        self.max_jobarray_size = max_jobarray_size
        # sleep time when total job threshold is reached in seconds
        self.resubmit_wait_time_in_seconds = resubmit_wait_time_in_seconds

    def manage_jobs(self):
        recently_failed_submit_commands = {}
        while self.job_command_list:
            print("checking if total job threshold is reached...")
            bashcommand = self.job_command_list.pop(0)
            if get_num_jobs_on_himster() < self.himster_total_job_threshold:
                print("Nope, trying to submit job...")
                returnvalue = subprocess.call(bashcommand.split())
                if returnvalue > 0:
                    resubmit = True
                    if bashcommand in recently_failed_submit_commands:
                        if time() < (recently_failed_submit_commands[bashcommand]
                                     + self.resubmit_wait_time_in_seconds):
                            print(bashcommand)
                            print(
                                "something is wrong with this submit command."
                                " Skipping...")
                            resubmit = False
                    else:
                        print(
                            "Submit failed! Appending job to resubmit list "
                            "for later submission...")
                        recently_failed_submit_commands[bashcommand] = time()

                    if resubmit:
                        # put the command back into the list
                        self.job_command_list.insert(0, bashcommand)
                else:
                    # sleep 5 sec to make the queue changes active
                    sleep(5)
            else:
                # put the command back into the list
                self.job_command_list.insert(0, bashcommand)
                print('Yep, we have currently have ' +
                      str(len(self.job_command_list)) +
                      ' jobs waiting in queue!')
                # and sleep for some time
                print('Waiting for '
                      + str(self.resubmit_wait_time_in_seconds / 60)
                      + ' min and then trying a resubmit...')
                sleep(self.resubmit_wait_time_in_seconds)

    def submit_jobs_to_himster(self, job_list):
        if is_cluster_environment():
            print('This is a cluster environment. Adding jobs to queue list!')
            for job in job_list:
                for bashcommand in job.create_bash_commands(self.max_jobarray_size):
                    self.job_command_list.append(bashcommand)

        else:
            print('This is not a cluster environment! Please make sure this '
                  'script is executed on a cluster environment!')
