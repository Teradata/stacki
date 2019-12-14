import json
from textwrap import dedent


class TestRemoveHost:
	def test_invalid_host(self, host):
		result = host.run('stack remove host test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot resolve host "test"\n'

	def test_no_args(self, host):
		result = host.run('stack remove host')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...}
		''')

	def test_no_host_matches(self, host):
		result = host.run('stack remove host a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...}
		''')

	def test_remove_self(self, host):
		result = host.run('stack remove host frontend-0-0')
		assert result.rc == 255
		assert result.stderr == 'error - cannot remove "frontend-0-0"\n'

	def test_single_arg(self, host, add_host_with_interface, add_group, host_os, revert_etc):
		# Attach a bunch of data to the backend
		result = host.run('stack add host interface alias backend-0-0 alias=test interface=eth0')
		assert result.rc == 0

		result = host.run('stack add host attr backend-0-0 attr=test value=true')
		assert result.rc == 0

		result = host.run(
			'stack add host firewall backend-0-0 service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		result = host.run('stack add host group backend-0-0 group=test')
		assert result.rc == 0

		result = host.run('stack add host key backend-0-0 key=foo')
		assert result.rc == 0

		# Create a second backend which shouldn't get touched
		add_host_with_interface('backend-0-1', '0', '2', 'backend', 'eth0')

		# Now remove our backend
		result = host.run('stack remove host backend-0-0')
		assert result.rc == 0

		# Confirm we only have one backend left
		result = host.run('stack list host a:backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'box': 'default',
				'comment': None,
				'environment': None,
				'host': 'backend-0-1',
				'installaction': 'default',
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '2'
			}
		]

	def test_multiple_args(self, host, add_host_with_interface, add_group, host_os, revert_etc):
		# Attach a bunch of data to the backend
		result = host.run('stack add host interface alias backend-0-0 alias=test interface=eth0')
		assert result.rc == 0

		result = host.run('stack add host attr backend-0-0 attr=test value=true')
		assert result.rc == 0

		result = host.run(
			'stack add host firewall backend-0-0 service=1234 chain=INPUT '
			'action=ACCEPT protocol=TCP network=private rulename=test'
		)
		assert result.rc == 0

		result = host.run('stack add host group backend-0-0 group=test')
		assert result.rc == 0

		result = host.run('stack add host key backend-0-0 key=foo')
		assert result.rc == 0

		# Create a second backend which shouldn't get touched
		add_host_with_interface('backend-0-1', '0', '2', 'backend', 'eth0')

		# Create a third backend we are blowing away as well
		add_host_with_interface('backend-0-2', '0', '3', 'backend', 'eth0')

		# Now remove our backend
		result = host.run('stack remove host backend-0-0 backend-0-2')
		assert result.rc == 0

		# Confirm we only have one backend left
		result = host.run('stack list host a:backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'box': 'default',
				'comment': None,
				'environment': None,
				'host': 'backend-0-1',
				'installaction': 'default',
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '2'
			}
		]

	def test_hypervisor_with_vm(self, host, add_hypervisor, add_vm_multiple):
		"""
		Test that remove host doesn't allow removing
		a hypervisor host with virtual machines defined
		on it
		"""

		# hypervisor-0-1 currently has two VM's
		# defined on it
		result = host.run('stack remove host hypervisor-0-1')
		assert result.rc != 0

	def test_hypervisor_no_vm(self, host, add_hypervisor, add_vm):
		"""
		Test that we can remove a hypervisor host
		with no virtual machines defined on it
		"""

		result = host.run('stack remove host hypervisor-0-2')
		assert result.rc == 0
