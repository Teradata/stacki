import os
import subprocess
import pytest

BOOTACTION_JSON = 'bootaction.json'

@pytest.mark.usefixtures("bootaction")
@pytest.mark.parametrize("file", BOOTACTION_JSON)
def test_load_json_bootaction(host, file):
	# get filename
	dirn = '/export/test-files/load/'
	input_file = dirn + file

	# load the bootaction file
	result = host.run(f'stack load json bootaction file={input_file}')
	assert result.rc == 0

	# export our bootaction configuration
	result = host.run('stack export bootaction')
	assert result.rc == 0
	exported_bootaction_information = result.stdout

	# check to make sure the export and the import are the same
	result = host.run(f'cat {inputfile}')
	assert result.stdout == exported_bootaction_information
