import pytest
import json

class TestSetSwitchPartitionMember:

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
		['0000', '00:00:00:00:00:00:00:00', '', '', ''],
		['0xfred', '', 'backend-0-0', 'ib0', ''],
		['default', '', 'no-such-host', 'ib0', 'full'],
		['Default', '', 'backend-0-0', 'fake_iface', 'limited'],
		['default', '', 'backend-0-0', 'ib0', 'bad_member_state'],
		['default', '', '', '', ''],
		['0x0aaa', '00:00:00:00:00:00:00:00', 'backend-0-0', '', ''],
		['0x0aaa', '00:00:00:00:00:00:00:00', '', 'ib0', ''],
		['0x0aaa', 'fake:guid', '', '', ''],
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
		cmd = [f'stack set switch partition membership switch-0-0 name={partition_name}']
		if guid:
			cmd.append(f'guid={guid}')
		elif hostname and interface:
			cmd.append(f'member={hostname} interface={interface}')
		if membership:
			cmd.append(f'membership={membership}')

		result = host.run(' '.join(cmd))
		assert result.rc == 0
		# list switch partition member does not list partitions which have no members
		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

	@pytest.mark.parametrize("partition_name,guid,hostname,interface,membership,output_file", SWITCH_PARTITION_MEMBER_TEST_DATA)
	def test_set_for_membership_behavior(self, host, add_ib_switch, add_ib_switch_partition, add_host_with_interface,
				partition_name, guid, hostname, interface, membership, output_file):
		# for each member we add, we should be able to change its membership.
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		result = host.run(f'stack add host interface backend-0-0 interface=ib0 mac=00:00:00:00:00:00:00:00')
		assert result.rc == 0

		if partition_name.lower() != 'default':
			add_ib_switch_partition('switch-0-0', partition_name, None)

		# command can be called with guid or with hostname+iface
		cmd = [f'stack set switch partition membership switch-0-0 name={partition_name}']
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

		for row in TestSetSwitchPartitionMember.SWITCH_PARTITION_MEMBER_TEST_DATA:
			if partition_name.lower() != row[0]:
				continue

			guid, hostname, interface, membership, new_output_file = row[1:]
			# command can be called with guid or with hostname+iface
			cmd = [f'stack set switch partition membership switch-0-0 name={partition_name}']
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
			assert json.loads(result.stdout) == json.loads(open(dirn + new_output_file).read())


	@pytest.mark.parametrize("partition_name,guid,hostname,interface,membership", SWITCH_PARTITION_MEMBER_NEGATIVE_TEST_DATA)
	def test_negative_behavior(self, host, add_ib_switch, add_ib_switch_partition, add_host_with_interface,
				partition_name, guid, hostname, interface, membership):
		result = host.run(f'stack add host interface backend-0-0 interface=ib0 mac=00:00:00:00:00:00:00:00')
		assert result.rc == 0

		# command can be called with guid or with hostname+iface
		cmd = [f'stack set switch partition membership switch-0-0 name={partition_name}']
		if guid:
			cmd.append(f'guid={guid}')
		if hostname:
			cmd.append(f'member={hostname}')
		if interface:
			cmd.append(f'interface={interface}')
		if membership:
			cmd.append(f'membership={membership}')

		result = host.run(' '.join(cmd))
		assert result.rc != 0

		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert result.stdout.strip() == ''

	def test_passed_no_args(self, host, add_ib_switch):
		result = host.run(f'stack set switch partition membership')
		assert result.rc != 0

	@pytest.mark.parametrize("partition_name,guid,hostname,interface,membership,output_file", SWITCH_PARTITION_MEMBER_TEST_DATA)
	def test_can_add_then_set(self, host, add_ib_switch, add_ib_switch_partition, add_host_with_interface,
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

		# list switch partition member does not list partitions which have no members
		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

		# make the add a set command
		result = host.run(' '.join(cmd).replace('add', 'set').replace('member ', 'membership '))
		assert result.rc == 0

		# should be the same
		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

	def test_can_duplicate_names_that_resolve_same(self, host, add_ib_switch, add_host_with_interface):
		output_file = 'add_nondefault_member_output.json'
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + output_file).read()

		result = host.run(f'stack add host interface backend-0-0 interface=ib0 mac=00:00:00:00:00:00:00:00')
		assert result.rc == 0

		same_parts = ['aaa', '0xaaa', '0x0aaa', 'AAA']

		# create the initial partition
		result = host.run(f'stack add switch partition switch-0-0 name={same_parts[0]}')
		assert result.rc == 0

		result = host.run(f'stack set switch partition membership switch-0-0 name={same_parts[0]} guid=00:00:00:00:00:00:00:00')
		assert result.rc == 0
		for partition_name in same_parts[1:]:
			result = host.run(f'stack set switch partition membership switch-0-0 name={partition_name} guid=00:00:00:00:00:00:00:00')
			assert result.rc == 0
			result = host.run('stack list switch partition member switch-0-0 output-format=json')
			assert result.rc == 0
			assert json.loads(result.stdout) == json.loads(expected_output)

	def test_cannot_add_to_non_ib(self, host, add_switch):
		result = host.run(f'stack set switch partition membership switch-0-0 name=default guid=fake')
		assert result.rc != 0

	def test_cannot_add_with_enforce_sm(self, host, add_ib_switch, add_ib_switch_partition):
		# by design this should fail if there's no actual switch to talk to.
		result = host.run(f'stack set switch partition membership switch-0-0 name=Default guid=fake enforce_sm=true')
		assert result.rc != 0

	def test_two_switches_same_partition_name(self, host, add_ib_switch, add_ib_switch_partition, add_host_with_interface):
		dirn = '/export/test-files/add/'
		expected_output = open(dirn + 'add_default_member_output.json').read()

		add_host_with_interface('backend-0-1', '0', '1', 'backend', 'eth0')
		# add hosts with ib interfaces
		for i in range(2):
			result = host.run(f'stack add host interface backend-0-{i} interface=ib0 mac=00:00:00:00:00:00:00:0{i}')
			assert result.rc == 0

		# add second switch
		add_ib_switch('switch-0-1', '0', '1', 'switch', 'Mellanox', 'm7800', 'infiniband')
		add_ib_switch_partition('switch-0-1', 'default', None)

		for i in range(2):
			cmd = f'stack set switch partition membership switch-0-{i} name=default guid=00:00:00:00:00:00:00:0{i}'
			result = host.run(cmd)
			assert result.rc == 0

		result = host.run('stack list switch partition member switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == json.loads(expected_output)

		# output here should be same as the output for switch-0-0, except for the name of the switch
		result = host.run('stack list switch partition member switch-0-1 output-format=json')
		assert result.rc == 0
		output = result.stdout.strip()
		output = output.replace('switch-0-1', 'switch-0-0')
		output = output.replace('backend-0-1', 'backend-0-0')
		output = output.replace('00:00:00:00:00:00:00:01', '00:00:00:00:00:00:00:00')
		assert json.loads(output) == json.loads(expected_output)

		result = host.run('stack list switch partition member switch-0-0 switch-0-1 output-format=json')
		assert result.rc == 0
		assert len(json.loads(result.stdout)) == 2
