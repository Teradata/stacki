import pytest

@pytest.mark.usefixtures('revert_database')
class TestAddHostAlias:
	list_host_alias_json_cmd = 'stack list host alias output-format=json'
	dirn = '/export/test-files/add/'

	# split possible?
	def test_add_host_alias_to_multiple_interfaces_across_multiple_hosts(self, host):
		result = host.run(f'stack load hostfile file={self.dirn}add_host_alias_hostfile.csv')
		assert result.rc == 0
		result = host.run('stack add host alias backend-0-0 alias=test0-eth0 interface=eth0')
		assert result.rc == 0

		# one alias in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		expected_output = open(self.dirn + 'add_host_alias_one_alias.json').read()
		assert result.stdout.strip() == expected_output.strip()

		result = host.run('stack add host alias backend-0-0 alias=test0-eth1 interface=eth1')
		assert result.rc == 0
		result = host.run('stack add host alias backend-0-1 alias=test1-eth0 interface=eth0')
		assert result.rc == 0
		result = host.run('stack add host alias backend-0-1 alias=test1-eth1 interface=eth1')
		assert result.rc == 0

		# four aliases in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		expected_output = open(self.dirn + 'add_host_alias_four_aliases.json').read()
		assert result.stdout.strip() == expected_output.strip()

	@pytest.mark.usefixtures('add_host_with_interface')
	def test_add_numeric_alias(self, host):
		# add numeric alias (invalid)
		result = host.run('stack add host alias backend-0-0 alias=42 interface=eth0')
		assert result.rc != 0

		# no aliases in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		assert result.stdout.strip() == ''

	@pytest.mark.usefixtures('add_host_with_interface')
	def test_add_duplicate_alias_same_host_interface(self, host):
		result = host.run('stack add host alias backend-0-0 alias=test0-eth0 interface=eth0')
		assert result.rc == 0
		# add same alias again (invalid)
		result = host.run('stack add host alias backend-0-0 alias=test0-eth0 interface=eth0')
		assert result.rc != 0

		# one alias in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		expected_output = open(self.dirn + 'add_host_alias_one_alias.json').read()
		assert result.stdout.strip() == expected_output.strip()

	def test_add_duplicate_alias_same_host(self, host):
		result = host.run(f'stack load hostfile file={self.dirn}add_host_alias_hostfile.csv')
		assert result.rc == 0
		result = host.run('stack add host alias backend-0-0 alias=test interface=eth0')
		assert result.rc == 0
		result = host.run('stack add host alias backend-0-0 alias=test interface=eth1')
		assert result.rc == 0

		# both aliases in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		expected_output = open(self.dirn + 'add_host_alias_two_aliases_same_name.json').read()
		print(result.stdout.strip())
		print(expected_output.strip())
		assert result.stdout.strip() == expected_output.strip()

	def test_add_duplicate_alias_different_host(self, host):
		result = host.run(f'stack load hostfile file={self.dirn}add_host_alias_hostfile.csv')
		assert result.rc == 0
		result = host.run('stack add host alias backend-0-0 alias=test0-eth0 interface=eth0')
		assert result.rc == 0
		# add same alias to different host (invalid)
		result = host.run('stack add host alias backend-0-1 alias=test0-eth0 interface=eth0')
		assert result.rc != 0

		# one alias in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		expected_output = open(self.dirn + 'add_host_alias_one_alias.json').read()
		assert result.stdout.strip() == expected_output.strip()

	@pytest.mark.usefixtures('add_host_with_interface')
	def test_add_multiple_aliases_same_host_interface(self, host):
		result = host.run('stack add host alias backend-0-0 alias=test0-eth0 interface=eth0')
		assert result.rc == 0
		result = host.run('stack add host alias backend-0-0 alias=2-test0-eth0 interface=eth0')
		assert result.rc == 0

		# both aliases in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		expected_output = open(self.dirn + 'add_host_alias_multiple_aliases_same_host_interface.json').read()
		assert result.stdout.strip() == expected_output.strip()

