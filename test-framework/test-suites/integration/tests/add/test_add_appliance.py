import pytest
import json


class TestAddAppliance:

	APPLIANCE_TEST_DATA = [
		('new_appliance_no_params', '', 'add_new_appliance_created_with_no_params_list_attr_output.json',),
		('new_appliance_node_is_backend', 'node=backend', 'add_new_appliance_created_with_node_as_backend_output.json',),
		('new_appliance_node_is_empty_str', 'node=', 'add_new_appliance_created_with_node_as_empty_str_output.json'),
		('new_appliance_node_is_any_str', 'node=anystr', 'add_new_appliance_created_with_node_as_any_str_output.json'),
	]

	@pytest.mark.parametrize("appliance_name,add_params,output_file", APPLIANCE_TEST_DATA)
	def test_behavior(self, host, appliance_name, add_params, output_file, test_file):
		with open(test_file(f'add/{output_file}')) as output:
			expected_output = output.read()

		result = host.run(f'stack add appliance {appliance_name} {add_params}')
		assert result.rc == 0

		result = host.run(f'stack list appliance attr {appliance_name} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

	def test_duplicate(self, host):
		result = host.run('stack add appliance backend')
		assert result.rc == 255
		assert result.stderr == 'error - appliance "backend" already exists\n'

	def test_two_args(self, host):
		result = host.run('stack add appliance foo foo')
		assert result.rc == 255
		assert result.stderr == 'error - "appliance" argument must be unique\n{appliance} [node=string] [public=bool]\n'
