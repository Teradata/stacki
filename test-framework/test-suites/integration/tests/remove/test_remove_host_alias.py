import pytest

@pytest.mark.usefixtures('revert_database')
class TestRemoveHostAlias:
	list_host_alias_json_cmd = 'stack list host alias output-format=json'

	@pytest.mark.usefixtures('add_host_with_interface')
	def test_remove_single_alias(self, host):
		result = host.run('stack add host alias backend-0-0 alias=test interface=eth0')
		assert result.rc == 0
		result = host.run('stack remove host alias backend-0-0 alias=test interface=eth0')
		assert result.rc == 0

		# no aliases in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		assert result.stdout.strip() == ''

	@pytest.mark.usefixtures('add_host_with_interface')
	def test_remove_all_aliases_on_interface(self, host):
		result = host.run('stack add host alias backend-0-0 alias=test0 interface=eth0')
		result = host.run('stack add host alias backend-0-0 alias=test1 interface=eth0')
		result = host.run('stack remove host alias backend-0-0 interface=eth0')
		assert result.rc == 0

		# no aliases in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		assert result.stdout.strip() == ''

	@pytest.mark.usefixtures('add_host_with_interface')
	def test_remove_host_interface_removes_aliases(self, host):
		result = host.run('stack add host alias backend-0-0 alias=test interface=eth0')
		assert result.rc == 0
		result = host.run('stack remove host interface backend-0-0 interface=eth0')
		assert result.rc == 0

		# no aliases in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		assert result.stdout.strip() == ''

	@pytest.mark.usefixtures('add_host_with_interface')
	def test_remove_host_removes_aliases(self, host):
		result = host.run('stack add host alias backend-0-0 alias=test interface=eth0')
		assert result.rc == 0
		result = host.run('stack remove host backend-0-0')
		assert result.rc == 0

		# no aliases in list
		result = host.run(self.list_host_alias_json_cmd)
		assert result.rc == 0
		assert result.stdout.strip() == ''

