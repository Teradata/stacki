import pytest
import json

@pytest.mark.usefixtures("add_switch")
def test_add_switch(host):
	dirn = '/export/test-files/list/'
	output_file = 'switch_with_make_and_model_output.json'
	expected_output = open(dirn + output_file).read()

	result = host.run('stack list switch output-format=json')
	assert result.rc == 0
	assert json.loads(result.stdout) == json.loads(expected_output)

