import pytest
import json


class TestRemoveSwitchPartition:

	SWITCH_PARTITION_TEST_DATA = [
		['default', '', 'add_default_partition_output.json'],
		['Default', '', 'add_default_partition_output.json'],
		['Default', 'ipoib=true', 'add_default_partition_ipoib_output.json'],
		['aaa', '', 'add_nondefault_partition_output.json'],
		['0xaaa', '', 'add_nondefault_partition_output.json'],
		['aaa', 'ipoib=true', 'add_nondefault_partition_with_ipoib_output.json'],
		['AAA', 'defmember=limited', 'add_nondefault_partition_with_defmember_limited_output.json'],
		['aaa', 'defmember=full', 'add_nondefault_partition_with_defmember_full_output.json'],
		['aaa', 'ipoib=true defmember=full', 'add_nondefault_partition_with_multiple_opts_output.json'],
		['aaa', 'defmember=full ipoib=true', 'add_nondefault_partition_with_multiple_opts_diff_order_output.json'],
	]

	@pytest.mark.parametrize("partition_name,options,output_file", SWITCH_PARTITION_TEST_DATA)
	def test_behavior(self, host, add_ib_switch, partition_name, options, output_file, test_file):
		with open(test_file(f'add/{output_file}')) as f:
			expected_output = f.read()

		result = host.run(f'stack add switch partition switch-0-0 name={partition_name} options="{options}"')
		assert result.rc == 0
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

		result = host.run(f'stack remove switch partition switch-0-0 name={partition_name}')
		assert result.rc == 0
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''

	def test_negative_behavior(self, host, add_ib_switch, test_file):
		with open(test_file('add/add_default_partition_output.json')) as f:
			expected_output = f.read()

		# should be able to add 
		result = host.run(f'stack add switch partition switch-0-0 name=Default')
		assert result.rc == 0

		# should error on invalid name
		result = host.run(f'stack remove switch partition switch-0-0 name=fake')
		assert result.rc != 0
		assert result.stderr.strip() != ''

		# bad remove should leave db same
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

		# should not error on valid but non-existing name
		result = host.run(f'stack remove switch partition switch-0-0 name=bbb')
		assert result.rc == 0
		assert result.stderr.strip() == ''
		assert result.stdout.strip() == ''

		# ... but it also shouldn't do anything.
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

	def test_passed_no_args(self, host, add_ib_switch):
		result = host.run(f'stack remove switch partition name=default')
		assert result.rc != 0
		assert result.stderr.strip() != ''

	def test_can_remove_twice(self, host, add_ib_switch, test_file):
		with open(test_file('add/add_default_partition_output.json')) as f:
			expected_output = f.read()

		partition_name = 'default'
		result = host.run(f'stack add switch partition switch-0-0 name={partition_name}')
		assert result.rc == 0
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

		# should be able to remove all day long
		for i in range(2):
			result = host.run(f'stack remove switch partition switch-0-0 name={partition_name}')
			assert result.rc == 0
			assert result.stdout.strip() == ''
			result = host.run('stack list switch partition switch-0-0 output-format=json')
			assert result.rc == 0
			assert result.stdout.strip() == ''
			assert result.stderr.strip() == ''

	def test_can_remove_names_that_resolve_same(self, host, add_ib_switch, test_file):
		with open(test_file('add/add_nondefault_partition_output.json')) as f:
			expected_output = f.read()

		same_parts = ['aaa', '0xaaa', '0x0aaa', 'AAA']

		for partition_name in same_parts[1:]:
			result = host.run(f'stack add switch partition switch-0-0 name=aaa')
			assert result.rc == 0

			result = host.run('stack list switch partition switch-0-0 output-format=json')
			assert result.rc == 0
			assert json.loads(result.stdout) == json.loads(expected_output)

			result = host.run(f'stack remove switch partition switch-0-0 name={partition_name}')
			assert result.rc == 0

			result = host.run('stack list switch partition switch-0-0 output-format=json')
			assert result.rc == 0
			assert result.stdout.strip() == ''

	def test_cannot_remove_from_non_ib(self, host, add_switch):
		result = host.run(f'stack remove switch partition switch-0-0 name=Default')
		assert result.rc != 0
		assert result.stderr.strip() != ''

	def test_cannot_remove_with_enforce_sm(self, host, add_ib_switch):
		# by design this should fail if there's no actual switch to talk to.
		result = host.run(f'stack remove switch partition switch-0-0 name=Default enforce_sm=true')
		assert result.rc != 0
		assert result.stderr.strip() != ''

	@pytest.mark.parametrize("partition_name,options,output_file", SWITCH_PARTITION_TEST_DATA)
	def test_two_switches_same_partition_name(self, host, add_ib_switch, partition_name, options, output_file, test_file):
		with open(test_file(f'add/{output_file}')) as f:
			expected_output = f.read()

		# add second switch
		add_ib_switch('switch-0-1', '0', '1', 'switch', 'Mellanox', 'm7800', 'infiniband')

		result = host.run(f'stack add switch partition switch-0-0 name={partition_name} options="{options}"')
		assert result.rc == 0	
		result = host.run(f'stack add switch partition switch-0-1 name={partition_name} options="{options}"')
		assert result.rc == 0	

		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

		# output here should be same as the output for switch-0-0, except for the name of the switch
		result = host.run('stack list switch partition switch-0-1 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout.strip().replace('switch-0-1', 'switch-0-0')) == json.loads(expected_output)

		result = host.run('stack remove switch partition switch-0-0 switch-0-1 output-format=json')
		assert result.rc == 0

		result = host.run('stack list switch partition switch-0-1 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''

	def test_remove_everything(self, host, add_ib_switch):
		# remove switch partition without any other classifiers should remove all partitions per switch
		# add second switch
		add_ib_switch('switch-0-1', '0', '1', 'switch', 'Mellanox', 'm7800', 'infiniband')

		for partition_name in ['aaa', 'default']:
			result = host.run(f'stack add switch partition switch-0-0 switch-0-1 name={partition_name}')
			assert result.rc == 0

		result = host.run('stack list switch partition switch-0-0 switch-0-1 output-format=json')
		assert result.rc == 0
		assert len(json.loads(result.stdout.strip())) == 4

		result = host.run('stack remove switch partition switch-0-0 switch-0-1')
		assert result.rc == 0

		result = host.run('stack list switch partition switch-0-0 switch-0-1 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''
