import pytest

@pytest.mark.usefixtures("revert_database")
class TestAddAppliance:

	APPLIANCE_TEST_DATA = [
		('new_appliance_no_params', '', 'add_new_appliance_created_with_no_params_list_attr_output.json',),
		('new_appliance_node_is_backend', 'node=backend', 'add_new_appliance_created_with_node_as_backend_output.json',),
		('new_appliance_node_is_empty_str', 'node=', 'add_new_appliance_created_with_node_as_empty_str_output.json'),
		('new_appliance_node_is_any_str', 'node=anystr', 'add_new_appliance_created_with_node_as_any_str_output.json'),
		]

	@pytest.mark.parametrize("appliance_name,add_params,output_file", APPLIANCE_TEST_DATA)
	def test_add_appliance_behavior(self, host, appliance_name, add_params, output_file):
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		result = host.run(f'stack add appliance {appliance_name} {add_params}')
		assert result.rc == 0

		result = host.run(f'stack list appliance attr {appliance_name} output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == expected_output.strip()

