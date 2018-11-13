from textwrap import dedent

import pytest
import json


class TestAddHostAlias:
	list_host_alias_json_cmd = 'stack list host alias output-format=json'
	dirn = '/export/test-files/add/'

	# split possible?
	def test_to_multiple_interfaces_across_multiple_hosts(self, host):
		result = host.run(f'stack load hostfile file={self.dirn}add_host_alias_hostfile.csv')
		assert result.rc == 0
		result = host.run('stack add host alias backend-0-0 alias=test0-eth0 interface=eth0')
		assert result.rc == 0

		# one alias in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		expected_output = open(self.dirn + 'add_host_alias_one_alias.json').read()
		assert json.loads(result.stdout) == json.loads(expected_output)

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
		assert json.loads(result.stdout) == json.loads(expected_output)

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
		assert json.loads(result.stdout) == json.loads(expected_output)

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
		assert json.loads(result.stdout) == json.loads(expected_output)

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
		assert json.loads(result.stdout) == json.loads(expected_output)

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
		assert json.loads(result.stdout) == json.loads(expected_output)

	def test_no_host(self, host):
		result = host.run('stack add host alias')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} {alias=string} {interface=string}
		''')

	def test_no_matching_hosts(self, host):
		result = host.run('stack add host alias a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host} {alias=string} {interface=string}
		''')
	
	def test_multiple_hosts(self, host, add_host):
		result = host.run('stack add host alias frontend-0-0 backend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument must be unique
			{host} {alias=string} {interface=string}
		''')
	
	def test_hostname_in_use(self, host, add_host):
		result = host.run('stack add host alias frontend-0-0 alias=backend-0-0 interface=eth0')
		assert result.rc == 255
		assert result.stderr == 'error - hostname already in use\n'

	def test_invalid_alias(self, host, add_host):
		result = host.run('stack add host alias frontend-0-0 alias=127.0.0.1 interface=eth0')
		assert result.rc == 255
		assert result.stderr == 'error - aliases cannot be an IP address\n'
	
	def test_invalid_interface(self, host, add_host):
		result = host.run('stack add host alias frontend-0-0 alias=foo interface=eth7')
		assert result.rc == 255
		assert result.stderr == 'error - interface does not exist\n'
