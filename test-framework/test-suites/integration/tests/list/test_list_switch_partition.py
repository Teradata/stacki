import pytest
import json

class TestListSwitchPartition:

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
	def test_add_behavior(self, host, add_ib_switch, partition_name, options, output_file):
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		result = host.run(f'stack add switch partition switch-0-0 name={partition_name} options="{options}"')
		assert result.rc == 0
		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == expected_output.strip()

	def test_list_by_name(self, host, add_ib_switch):
		dirn = '/export/test-files/add/'

		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''

		partition_name = 'default'
		output_file = 'add_default_partition_output.json'
		result = host.run(f'stack add switch partition switch-0-0 name={partition_name}')
		assert result.rc == 0

		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == open(dirn + output_file).read().strip()

		partition_name = 'aaa'
		output_file = 'add_nondefault_partition_output.json'
		result = host.run(f'stack add switch partition switch-0-0 name={partition_name}')
		assert result.rc == 0

		result = host.run(f'stack list switch partition switch-0-0 name={partition_name} output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == open(dirn + output_file).read().strip()

		# valid names should return nothing, and not error
		partition_name = 'bbb'
		result = host.run(f'stack list switch partition switch-0-0 name={partition_name} output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''
		assert result.stderr.strip() == ''

		# invalid names should return an error
		partition_name = 'badname'
		result = host.run(f'stack list switch partition switch-0-0 name={partition_name} output-format=json')
		assert result.rc != 0
		assert result.stdout.strip() == ''
		assert result.stderr.strip() != ''

	def test_list_everything(self, host, add_ib_switch):
		dirn = '/export/test-files/add/'
		output_file = 'add_multiple_partitions_output.json'

		for partition_name in ['default', 'aaa']:
			result = host.run(f'stack add switch partition switch-0-0 name={partition_name}')
			assert result.rc == 0

		result = host.run('stack list switch partition switch-0-0 output-format=json')
		assert result.rc == 0

		sort_key = lambda d: d['partition']
		assert json.loads(result.stdout).sort(key=sort_key) == json.loads(open(dirn + output_file).read()).sort(key=sort_key)

	def test_passed_no_args(self, host, add_ib_switch):
		result = host.run(f'stack list switch partition name=fake')
		assert result.rc != 0

	def test_cannot_list_non_ib(self, host, add_switch):
		result = host.run(f'stack list switch partition switch-0-0 name=Default')
		assert result.rc != 0

	def test_cannot_add_with_enforce_sm(self, host, add_ib_switch):
		# by design this should fail if there's no actual switch to talk to.
		result = host.run(f'stack list switch partition switch-0-0 name=Default enforce_sm=true')
		assert result.rc != 0
