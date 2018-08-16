import pytest
import json

@pytest.mark.usefixtures("revert_database")
class TestAddHost:

	# Tests for the positive behaviour of stack add host
	HOST_POSITIVE_TEST_DATA = [
		('backend-0-0','','add_host_with_standard_naming_convention.json',),
		('backend_4_3','appliance=backend rack=4 rank=3','add_host_with_appliance_rack_rank.json',),
		('backend-7-7','appliance=backend rack=5 rank=5','add_host_with_standard_naming_and_appliance_rack_rank.json',)
		]

	@pytest.mark.parametrize("host_name, add_params, output_file", HOST_POSITIVE_TEST_DATA)
	def test_add_host_positive_behaviour(self, host, host_name, add_params, output_file):
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		result = host.run(f'stack add host {host_name} {add_params}')
		assert result.rc == 0

		result = host.run(f'stack list host {host_name} output-format=json')
		assert result.rc == 0

		expected_output_json = json.loads(expected_output)
		actual_output_json = json.loads(result.stdout)
		actual_output_json[0]['os']=""
		assert expected_output_json == actual_output_json


	# Tests for the negative behaviour of stack add host
	HOST_NEGATIVE_TEST_DATA = [
		('','','',),
		('backend','','',),
		('backend', 'appliance=backend','',),
		('backend', 'appliance=backend rack=4','',),
		('backend', 'appliance=backend rank=4','',),
		('backend', 'appliance=backend rack=4 rank=',''),
		('backend', 'appliance=backend rack= rank=4',''),
		('backend', 'appliance=backend rack= rank= ','')
		]

	@pytest.mark.parametrize("host_name, add_params, output_file", HOST_NEGATIVE_TEST_DATA)
	def test_add_host_negative_behaviour(self, host, host_name, add_params, output_file):
		result = host.run(f'stack add host {host_name} {add_params}')
		assert result.rc != 0

