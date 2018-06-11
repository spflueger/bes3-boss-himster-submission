from os import path
import pytest
import json

from general import create_file_chunks, get_exe_path


class TestAutomaticFileChunking(object):
    def test_file_chunks_amount(self):
        cases = [
            (list(range(1, 1801)), 5, 0.5, 360),
            ([1], 5, 0.5, 1),
            (list(range(1, 24)), 5, 0.5, 5),
            (list(range(1, 24)), 5, 0.7, 4)
        ]
        for case in cases:
            assert len(create_file_chunks(case[0], case[1], case[2])) == case[3]

    def test_file_chunks_false_input(self):
        with pytest.raises(TypeError):
            create_file_chunks([1, 2], 1, 1)
        with pytest.raises(TypeError):
            create_file_chunks([1, 2], 1, 'a')
        with pytest.raises(ValueError):
            create_file_chunks([1, 2], 1, 1.1)
        with pytest.raises(ValueError):
            create_file_chunks([1, 2], 1, -0.1)

    def test_config_chunk_redistribution_threshold(self):
        # get full path of the executable
        script_fullpath = get_exe_path('create_ana_job.py')
        script_dir = path.abspath(path.dirname(script_fullpath))

        json_file = open(script_dir + '/config.json')
        config_data = json.loads(json_file.read())
        print(config_data)
        redistribution_threshold = config_data['analysis'][
            'chunk_redistribution_threshold']

        assert redistribution_threshold >= 0.0
        assert redistribution_threshold <= 1.0
