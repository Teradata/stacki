import pytest
import json

class TestSetSwitchPartition:

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

	SWITCH_PARTITION_NEGATIVE_TEST_DATA = [
		['fred', ''],
		['default', 'badopt=true'],
		['default', 'badopt_no_param'],
	]

	@pytest.mark.parametrize("partition_name,options,output_file", SWITCH_PARTITION_TEST_DATA)
	def test_set_as_add_behavior(self, host, add_ib_switch, partition_name, options, output_file):
		# set should work just like add (we create if it doesn't exist)
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		result = host.run(f'stack set switch partition options switch-0-0 name={partition_name} options="{options}"')
		assert result.rc == 0
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == expected_output.strip()

	@pytest.mark.parametrize("partition_name,options,output_file", SWITCH_PARTITION_TEST_DATA)
	def test_set_for_options_behavior(self, host, add_ib_switch, partition_name, options, output_file):
		# for each partition we create, we should be able to change its options to anything.
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		result = host.run(f'stack set switch partition options switch-0-0 name={partition_name} options="{options}"')
		assert result.rc == 0
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == expected_output.strip()

		for row in TestSetSwitchPartition.SWITCH_PARTITION_TEST_DATA:
			if partition_name.lower() != row[0]:
				continue

			new_opt_str, new_output_file = row[1], row[2]
			result = host.run(f'stack set switch partition options switch-0-0 name={partition_name} options="{new_opt_str}"')
			assert result.rc == 0
			result = host.run('stack list switch partition switch-0-0 output-format=json')
			assert result.rc == 0
			assert result.stdout.strip() == open(dirn + new_output_file).read().strip()

	@pytest.mark.parametrize("partition_name,options", SWITCH_PARTITION_NEGATIVE_TEST_DATA)
	def test_set_negative_behavior(self, host, add_ib_switch, partition_name, options):
		result = host.run(f'stack set switch partition options switch-0-0 name={partition_name} options="{options}"')
		assert result.rc != 0
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''

	def test_passed_no_args(self, host, add_ib_switch):
		result = host.run(f'stack set switch partition options name=fake')
		assert result.rc != 0

	@pytest.mark.parametrize("partition_name,options,output_file", SWITCH_PARTITION_TEST_DATA)
	def test_can_add_then_set(self, host, add_ib_switch, partition_name, options, output_file):
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		result = host.run(f'stack add switch partition switch-0-0 name={partition_name} options="{options}"')
		assert result.rc == 0
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == expected_output.strip()

		result = host.run(f'stack set switch partition options switch-0-0 name={partition_name} options="{options}"')
		assert result.rc == 0

	def test_can_duplicate_names_that_resolve_same(self, host, add_ib_switch):
		output_file = 'add_nondefault_partition_output.json'
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		same_parts = ['aaa', '0xaaa', '0x0aaa', 'AAA']

		result = host.run(f'stack set switch partition options switch-0-0 name={same_parts[0]}')
		assert result.rc == 0
		for partition_name in same_parts[1:]:
			result = host.run(f'stack set switch partition options switch-0-0 name={partition_name}')
			assert result.rc == 0
			result = host.run('stack list switch partition switch-0-0 output-format=json')
			assert result.rc == 0
			assert result.stdout.strip() == expected_output.strip()

	def test_cannot_add_via_set_to_non_ib(self, host, add_switch):
		result = host.run(f'stack add switch partition switch-0-0 name=Default')
		assert result.rc != 0

	def test_cannot_add_with_enforce_sm(self, host, add_ib_switch):
		# by design this should fail if there's no actual switch to talk to.
		result = host.run(f'stack add switch partition switch-0-0 name=Default enforce_sm=true')
		assert result.rc != 0

		result = host.run(f'stack set switch partition options switch-0-0 name=Default enforce_sm=true')
		assert result.rc != 0

	@pytest.mark.parametrize("partition_name,options,output_file", SWITCH_PARTITION_TEST_DATA)
	def test_two_switches_same_partition_name(self, host, add_ib_switch, partition_name, options, output_file):
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		# add second switch
		add_ib_switch('switch-0-1', '0', '1', 'switch', 'Mellanox', 'm7800', 'infiniband')

		result = host.run(f'stack set switch partition options switch-0-0 name={partition_name} options="{options}"')
		assert result.rc == 0	
		result = host.run(f'stack set switch partition options switch-0-1 name={partition_name} options="{options}"')
		assert result.rc == 0	

		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == expected_output.strip()

		# output here should be same as the output for switch-0-0, except for the name of the switch
		result = host.run('stack list switch partition switch-0-1 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip().replace('switch-0-1', 'switch-0-0') == expected_output.strip()

		result = host.run('stack list switch partition switch-0-0 switch-0-1 output-format=json')
		assert result.rc == 0
		assert len(json.loads(result.stdout)) == 2
