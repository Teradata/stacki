import json
from textwrap import dedent


class TestSetHostBoot:
	def test_set_host_boot_no_hosts(self, host):
		result = host.run('stack set host boot')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {action=string} [nukecontroller=boolean] [nukedisks=boolean] [sync=boolean]
		''')

	def test_set_host_boot_no_matching_hosts(self, host):
		result = host.run('stack set host boot a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {action=string} [nukecontroller=boolean] [nukedisks=boolean] [sync=boolean]
		''')

	def test_set_host_boot_no_parameters(self, host):
		result = host.run('stack set host boot frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" parameter is required
			{host ...} {action=string} [nukecontroller=boolean] [nukedisks=boolean] [sync=boolean]
		''')

	def test_set_host_boot_invalid_action(self, host):
		result = host.run('stack set host boot frontend-0-0 action=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" parameter must be one of: os, install
			{host ...} {action=string} [nukecontroller=boolean] [nukedisks=boolean] [sync=boolean]
		''')

	def test_set_host_boot_single_host(self, host, add_host):
		# Set the host boot action
		result = host.run('stack set host boot backend-0-0 action=install')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host boot backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'host': 'backend-0-0',
			'action': 'install',
			'nukedisks': False,
			'nukecontroller': False
		}]

	def test_set_host_boot_multiple_hosts(self, host, add_host):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Set the boot action on both backends
		result = host.run(
			'stack set host boot backend-0-0 backend-0-1 action=install'
		)
		assert result.rc == 0

		# Check that the change made it into the database
		result = host.run(f'stack list host boot a:backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'host': 'backend-0-0',
				'action': 'install',
				'nukedisks': False,
				'nukecontroller': False
			},
			{
				'host': 'backend-0-1',
				'action': 'install',
				'nukedisks': False,
				'nukecontroller': False
			}
		]

	def test_set_host_boot_all_parameters(self, host, add_host):
		# Set the host boot action
		result = host.run(
			'stack set host boot backend-0-0 action=install '
			'nukedisks=true nukecontroller=true sync=false'
		)
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host boot backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'host': 'backend-0-0',
			'action': 'install',
			'nukedisks': True,
			'nukecontroller': True
		}]

	def test_set_host_boot_existing(self, host, add_host):
		# Set the host boot action
		result = host.run('stack set host boot backend-0-0 action=install')
		assert result.rc == 0

		# Now set it again
		result = host.run('stack set host boot backend-0-0 action=os')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host boot backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'host': 'backend-0-0',
			'action': 'os',
			'nukedisks': False,
			'nukecontroller': False
		}]
