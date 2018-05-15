from himster2 import Job, JobResourceRequest


class TestJob(object):
    def test_create_array_string(self):
        test_job = Job(JobResourceRequest(1), '', '', '')
        cases = [
            (list(range(1, 11)), ' --array=1-10'),
            ([1, 2, 3, 4, 6, 7, 8], ' --array=1-4,6-8'),
            ([1, 2, 4, 5, 6, 7, 54, 65, 66, 67, 90],
             ' --array=1,2,4-7,54,65-67,90')
        ]
        for case in cases:
            assert test_job.create_array_string(case[0]) == case[1]
