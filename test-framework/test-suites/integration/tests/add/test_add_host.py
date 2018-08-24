import json
from textwrap import dedent

import pytest


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
		('backend', 'appliance=backend rack=4 rank=',''),
		('backend', 'appliance=backend rack= rank=4',''),
		('backend', 'appliance=backend rack= rank= ','')
	]

	@pytest.mark.parametrize("host_name, add_params, output_file", HOST_NEGATIVE_TEST_DATA)
	def test_add_host_negative_behaviour(self, host, host_name, add_params, output_file):
		result = host.run(f'stack add host {host_name} {add_params}')
		assert result.rc != 0

	def test_add_host_multiple_hosts(self, host):
		result = host.run('stack add host test test2 appliance=test rack=0 rank=0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument must be unique
			{host} [box=string] [environment=string] [rack=string] [rank=string]
		''')

	def test_add_host_duplicate(self, host):
		# Add the host
		result = host.run('stack add host test appliance=backend rack=0 rank=0')
		assert result.rc == 0

		# Add it again
		result = host.run('stack add host test appliance=backend rack=0 rank=0')
		assert result.rc == 255
		assert result.stderr == 'error - host "test" already exists in the database\n'

	def test_add_host_invalid_appliance(self, host):
		result = host.run('stack add host test appliance=test rack=0 rank=0')
		assert result.rc == 255
		assert result.stderr == 'error - appliance "test" is not in the database\n'

	def test_add_host_invalid_box(self, host):
		result = host.run('stack add host test appliance=backend rack=0 rank=0 box=test')
		assert result.rc == 255
		assert result.stderr == 'error - box "test" is not in the database\n'

	def test_add_host_invalid_installaction(self, host, host_os):
		result = host.run('stack add host test appliance=backend rack=0 rank=0 installaction=test')
		assert result.rc == 255
		assert result.stderr == f'error - "test" install boot action for "{host_os}" is missing\n'

	def test_add_host_invalid_osaction(self, host, host_os):
		result = host.run('stack add host test appliance=backend rack=0 rank=0 osaction=test')
		assert result.rc == 255
		assert result.stderr == f'error - "test" os boot action for "{host_os}" is missing\n'

	def test_add_host_with_environment(self, host, host_os):
		# Create our environment
		result = host.run('stack add environment test')
		assert result.rc == 0

		# Add our host
		result = host.run('stack add host test appliance=backend rack=0 rank=0 environment=test')
		assert result.rc == 0

		# Make sure the environment is there
		result = host.run('stack list host test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'box': 'default',
				'comment': None,
				'environment': 'test',
				'host': 'test',
				'installaction': 'default',
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '0',
				'status': 'deprecated'
			}
		]
