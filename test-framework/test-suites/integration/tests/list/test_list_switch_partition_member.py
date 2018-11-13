import pytest
import json

class TestListSwitchPartitionMember:

	SWITCH_PARTITION_MEMBER_TEST_DATA = [
		['default', '00:00:00:00:00:00:00:00', '', '', '', 'add_default_member_output.json'],
		['default', '', 'backend-0-0', 'ib0', '', 'add_default_member_output.json'],
		['Default', '', 'backend-0-0', 'ib0', 'limited', 'add_default_member_output.json'],
		['default', '', 'backend-0-0', 'ib0', 'full', 'add_default_member_full_output.json'],
		['aaa', '', 'backend-0-0', 'ib0', '', 'add_nondefault_member_output.json'],
		['AaA', '', 'backend-0-0', 'ib0', '', 'add_nondefault_member_output.json'],
		['AaA', '', 'backend-0-0', 'ib0', 'limited', 'add_nondefault_member_output.json'],
		['0x0aaa', '00:00:00:00:00:00:00:00', '', '', 'full', 'add_nondefault_member_full_output.json'],
	]

	SWITCH_PARTITION_MEMBER_NEGATIVE_TEST_DATA = [
		['0xfred', '', 'backend-0-0', 'ib0'],
		['default', '', 'no-such-host', 'ib0'],
		['Default', '', 'backend-0-0', 'fake_iface'],
		['0x0aaa', '00:00:00:00:00:00:00:00', 'backend-0-0', ''],
		['0x0aaa', '00:00:00:00:00:00:00:00', '', 'ib0'],
		['0x0aaa', 'fake:guid', '', ''],
	]

	@pytest.mark.parametrize("partition_name,guid,hostname,interface,membership,output_file", SWITCH_PARTITION_MEMBER_TEST_DATA)
	def test_behavior(self, host, add_ib_switch, add_ib_switch_partition, add_host_with_interface,
				partition_name, guid, hostname, interface, membership, output_file):

		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		result = host.run(f'stack add host interface backend-0-0 interface=ib0 mac=00:00:00:00:00:00:00:00')
		assert result.rc == 0

		if partition_name.lower() != 'default':
			add_ib_switch_partition('switch-0-0', partition_name, None)

		# command can be called with guid or with hostname+iface
		cmd = [f'stack add switch partition member switch-0-0 name={partition_name}']
		if guid:
			cmd.append(f'guid={guid}')
		elif hostname and interface:
			cmd.append(f'member={hostname} interface={interface}')
		if membership:
			cmd.append(f'membership={membership}')

		result = host.run(' '.join(cmd))
		assert result.rc == 0

		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

	def test_list_by_name(self, host, add_ib_switch, add_ib_switch_partition, add_host_with_interface):
		dirn = '/export/test-files/add/'

		host_guid = '00:00:00:00:00:00:00:00'
		result = host.run(f'stack add host interface backend-0-0 interface=ib0 mac={host_guid}')
		assert result.rc == 0

		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''

		partition_name = 'default'
		output_file = 'add_default_member_output.json'

		result = host.run(f'stack add switch partition member switch-0-0 name={partition_name} guid={host_guid}')
		assert result.rc == 0
		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(open(dirn + output_file).read())

		partition_name = 'aaa'
		output_file = 'add_nondefault_member_output.json'

		result = host.run(f'stack add switch partition switch-0-0 name={partition_name}')
		assert result.rc == 0
		result = host.run(f'stack add switch partition member switch-0-0 name={partition_name} guid={host_guid}')
		assert result.rc == 0

		result = host.run(f'stack list switch partition member switch-0-0 name={partition_name} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(open(dirn + output_file).read())

		# valid names should return nothing, and not error
		partition_name = 'bbb'
		result = host.run(f'stack list switch partition member switch-0-0 name={partition_name} output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''
		assert result.stderr.strip() == ''

		# invalid names should return an error
		partition_name = 'badname'
		result = host.run(f'stack list switch partition member switch-0-0 name={partition_name} output-format=json')
		assert result.rc != 0
		assert result.stdout.strip() == ''
		assert result.stderr.strip() != ''

	def test_list_everything(self, host, add_ib_switch, add_ib_switch_partition, add_host_with_interface):
		dirn = '/export/test-files/add/'
		output_file = 'add_multiple_partitions_multiple_members_output.json'

		add_host_with_interface('backend-0-1', '0', '1', 'backend', 'eth0')
		# add hosts with ib interfaces
		for i in range(2):
			result = host.run(f'stack add host interface backend-0-{i} interface=ib0 mac=00:00:00:00:00:00:00:0{i}')
			assert result.rc == 0

		# add second switch
		add_ib_switch('switch-0-1', '0', '1', 'switch', 'Mellanox', 'm7800', 'infiniband')
		add_ib_switch_partition('switch-0-1', 'default', None)
		add_ib_switch_partition('switch-0-0', 'aaa', None)
		add_ib_switch_partition('switch-0-1', 'aaa', None)

		for i in range(2):
			cmd = f'stack add switch partition member switch-0-{i} name=default guid=00:00:00:00:00:00:00:0{i}'
			result = host.run(cmd)
			assert result.rc == 0
			cmd = f'stack add switch partition member switch-0-{i} name=aaa guid=00:00:00:00:00:00:00:0{i}'
			result = host.run(cmd)
			assert result.rc == 0

		result = host.run('stack list switch partition switch-0-0 switch-0-1 output-format=json')
		assert result.rc == 0

		sort_key = lambda d: d['partition']
		assert json.loads(result.stdout).sort(key=sort_key) == json.loads(open(dirn + output_file).read()).sort(key=sort_key)

		result = host.run('stack list switch partition member switch-0-0 switch-0-1 output-format=json expanded=true')
		assert result.rc == 0

		output_file = 'add_multiple_partitions_multiple_members_output.json'
		assert json.loads(result.stdout).sort(key=sort_key) == json.loads(open(dirn + output_file).read()).sort(key=sort_key)

	def test_passed_no_args(self, host, add_ib_switch, add_ib_switch_partition):
		result = host.run(f'stack list switch partition member name=default')
		assert result.rc != 0
		assert result.stderr.strip() != ''

	def test_cannot_list_non_ib(self, host, add_switch):
		result = host.run(f'stack list switch partition member switch-0-0 name=Default')
		assert result.rc != 0
		assert result.stderr.strip() != ''

	def test_cannot_add_with_enforce_sm(self, host, add_ib_switch):
		# by design this should fail if there's no actual switch to talk to.
		result = host.run(f'stack list switch partition member switch-0-0 name=Default enforce_sm=true')
		assert result.rc != 0
		assert result.stderr.strip() != ''

