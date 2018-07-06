import os
import subprocess
import pytest

NETWORK_JSON = 'network.json'

@pytest.mark.usefixtures("network")
@pytest.mark.parametrize("file", NETWORK_JSON)
def test_load_json_network(host, file):
	# get filename
	dirn = '/export/test-files/load/'
	input_file = dirn + file

	# load the network file
	result = host.run(f'stack load json network file={input_file}')
	assert result.rc == 0

	# export our network configuration
	result = host.run('stack export network')
	assert result.rc == 0
	exported_network_information = result.stdout

	# check to make sure the export and the import are the same
	result = host.run(f'cat {inputfile}')
	assert result.stdout == exported_network_information
