import json


def test_add_switch(host, add_switch, test_file):
	with open(test_file('list/switch_with_make_and_model_output.json')) as output:
		expected_output = output.read()

	result = host.run('stack list switch output-format=json')
	assert result.rc == 0
	assert json.loads(result.stdout) == json.loads(expected_output)
