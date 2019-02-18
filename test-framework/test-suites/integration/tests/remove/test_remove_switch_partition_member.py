import pytest
import json

class TestRemoveSwitchPartitionMember:

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
				partition_name, guid, hostname, interface, membership, output_file, test_file):

		with open(test_file(f'add/{output_file}')) as f:
			expected_output = f.read()

		result = host.run(f'stack add host interface backend-0-0 interface=ib0 mac=00:00:00:00:00:00:00:00')
		assert result.rc == 0

		if partition_name.lower() != 'default':
			add_ib_switch_partition('switch-0-0', partition_name, None)

		# command can be called with guid or with hostname+iface
		cmd = [f'stack set switch partition membership switch-0-0 name={partition_name}']
		params = []
		if guid:
			params.append(f'guid={guid}')
		elif hostname and interface:
			params.append(f'member={hostname} interface={interface}')
		if membership:
			params.append(f'membership={membership}')

		result = host.run(' '.join(cmd + params))
		assert result.rc == 0

		# list switch partition member does not list partitions which have no members
		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

		# command can be called with guid or with hostname+iface
		cmd = [f'stack remove switch partition member switch-0-0 name={partition_name}']

		result = host.run(' '.join(cmd + params))
		assert result.rc == 0

		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''

	def test_negative_behavior(self, host, add_host_with_interface, add_ib_switch, add_ib_switch_partition, test_file):
		with open(test_file('add/add_default_member_output.json')) as f:
			expected_output = f.read()

		# add a host...
		partition_name = 'default'
		guid = '00:00:00:00:00:00:00:00'

		result = host.run(f'stack add host interface backend-0-0 interface=ib0 mac={guid}')
		assert result.rc == 0

		# should be able to add 
		result = host.run(f'stack add switch partition member switch-0-0 name=Default guid={guid}')
		assert result.rc == 0

		# should error on invalid name
		result = host.run(f'stack remove switch partition member switch-0-0 name=fake guid={guid}')
		assert result.rc != 0
		assert result.stderr.strip() != ''

		# should error on valid but non-existing partition
		result = host.run(f'stack remove switch partition member switch-0-0 name=aaa guid={guid}')
		assert result.rc != 0
		assert result.stderr.strip() != ''

		# bad remove should leave db same
		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

		# should not error on valid, existing name with non-existing guid
		result = host.run(f'stack remove switch partition member switch-0-0 name=default guid=5')
		assert result.rc == 0
		assert result.stderr.strip() == ''
		assert result.stdout.strip() == ''

		# ... but it also shouldn't do anything.
		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

	@pytest.mark.parametrize("partition_name,guid,hostname,interface", SWITCH_PARTITION_MEMBER_NEGATIVE_TEST_DATA)
	def test_bad_input(self, host, add_ib_switch, add_ib_switch_partition, add_host_with_interface,
				partition_name, guid, hostname, interface, test_file):

		with open(test_file('add/add_default_member_output.json')) as f:
			expected_output = f.read()

		# add a host...
		host_guid = '00:00:00:00:00:00:00:00'

		result = host.run(f'stack add host interface backend-0-0 interface=ib0 mac={host_guid}')
		assert result.rc == 0
		result = host.run(f'stack add switch partition member switch-0-0 name=default guid={host_guid}')
		assert result.rc == 0

		# command can be called with guid or with hostname+iface
		cmd = [f'stack remove switch partition member switch-0-0 name={partition_name}']
		params = []
		if guid:
			params.append(f'guid={guid}')
		if hostname:
			params.append(f'member={hostname}')
		if interface:
			params.append(f'interface={interface}')

		result = host.run(' '.join(cmd + params))
		assert result.rc != 0
		assert result.stderr.strip() != ''
		assert result.stdout.strip() == ''

		# list switch partition member does not list partitions which have no members
		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

	def test_passed_no_args(self, host, add_ib_switch):
		result = host.run(f'stack remove switch partition member name=default')
		assert result.rc != 0
		assert result.stderr.strip() != ''

	def test_can_remove_twice(self, host, add_host_with_interface, add_ib_switch, add_ib_switch_partition, test_file):
		with open(test_file('add/add_default_member_output.json')) as f:
			expected_output = f.read()

		partition_name = 'default'
		guid = '00:00:00:00:00:00:00:00'

		result = host.run(f'stack add host interface backend-0-0 interface=ib0 mac={guid}')
		assert result.rc == 0

		result = host.run(f'stack add switch partition member switch-0-0 name={partition_name} guid={guid}')
		assert result.rc == 0
		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

		# should be able to remove all day long
		for i in range(2):
			result = host.run(f'stack remove switch partition switch-0-0 name={partition_name} guid={guid}')
			assert result.rc == 0
			assert result.stdout.strip() == ''
			result = host.run('stack list switch partition member switch-0-0 output-format=json')
			assert result.rc == 0
			assert result.stdout.strip() == ''
			assert result.stderr.strip() == ''

	@pytest.mark.skip()
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
		result = host.run(f'stack remove switch partition member switch-0-0 name=Default')
		assert result.rc != 0
		assert result.stderr.strip() != ''

	def test_cannot_remove_with_enforce_sm(self, host, add_ib_switch):
		# by design this should fail if there's no actual switch to talk to.
		result = host.run(f'stack remove switch partition member switch-0-0 name=Default enforce_sm=true')
		assert result.rc != 0
		assert result.stderr.strip() != ''

	@pytest.mark.skip()
	@pytest.mark.parametrize("partition_name,guid,hostname,interface,membership,output_file", SWITCH_PARTITION_MEMBER_TEST_DATA)
	def test_two_switches_same_partition_name(self, host, add_ib_switch,
				partition_name, guid, hostname, interface, membership, output_file, test_file):

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

	def test_remove_everything(self, host, add_host_with_interface, add_ib_switch, add_ib_switch_partition):
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
			cmd = f'stack set switch partition membership switch-0-{i} name=default guid=00:00:00:00:00:00:00:0{i}'
			result = host.run(cmd)
			assert result.rc == 0

			cmd = f'stack set switch partition membership switch-0-{i} name=aaa guid=00:00:00:00:00:00:00:0{i}'
			result = host.run(cmd)
			assert result.rc == 0

		result = host.run('stack list switch partition member switch-0-0 switch-0-1 output-format=json')
		assert result.rc == 0
		assert len(json.loads(result.stdout.strip())) == 4

		result = host.run('stack remove switch partition member switch-0-0')
		assert result.rc == 0

		result = host.run('stack list switch partition member switch-0-0 switch-0-1 output-format=json')
		assert result.rc == 0
		assert len(json.loads(result.stdout.strip())) == 2

		result = host.run('stack remove switch partition member switch-0-1')
		assert result.rc == 0

		result = host.run('stack list switch partition member switch-0-0 switch-0-1 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''
