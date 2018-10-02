import json
from textwrap import dedent


class TestSetHostBootaction:
	def test_set_host_bootaction_no_hosts(self, host):
		result = host.run('stack set host bootaction')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {action=string} {type=string} [sync=boolean]
		''')

	def test_set_host_bootaction_no_matching_hosts(self, host):
		result = host.run('stack set host bootaction a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {action=string} {type=string} [sync=boolean]
		''')

	def test_set_host_bootaction_no_parameters(self, host):
		result = host.run('stack set host bootaction frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "action" parameter is required
			{host ...} {action=string} {type=string} [sync=boolean]
		''')

	def test_set_host_bootaction_invalid_type(self, host):
		result = host.run(
			'stack set host bootaction frontend-0-0 action=memtest type=test'
		)
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "type" parameter must be one of: os, install
			{host ...} {action=string} {type=string} [sync=boolean]
		''')

	def test_set_host_bootaction_invalid_action(self, host):
		result = host.run(
			'stack set host bootaction frontend-0-0 action=test type=os'
		)
		assert result.rc == 255
		assert result.stderr == 'error - bootaction "test" does not exist\n'

	def test_set_host_bootaction_single_host(self, host, add_host, host_os):
		# Set the host install bootaction
		result = host.run(
			'stack set host bootaction backend-0-0 action=console type=install'
		)
		assert result.rc == 0

		# Set the host os bootaction
		result = host.run(
			'stack set host bootaction backend-0-0 action=memtest type=os'
		)
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': None,
			'environment': None,
			'host': 'backend-0-0',
			'installaction': 'console',
			'os': host_os,
			'osaction': 'memtest',
			'rack': '0',
			'rank': '0'
		}]

	def test_set_host_bootaction_multiple_hosts(self, host, add_host, host_os):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Set the install boot action on both backends
		result = host.run(
			'stack set host bootaction backend-0-0 backend-0-1 '
			'action=console type=install'
		)
		assert result.rc == 0

		# Set the os boot action as well
		result = host.run(
			'stack set host bootaction backend-0-0 backend-0-1 '
			'action=memtest type=os'
		)
		assert result.rc == 0

		# Check that the change made it into the database
		result = host.run(f'stack list host a:backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'box': 'default',
				'comment': None,
				'environment': None,
				'host': 'backend-0-0',
				'installaction': 'console',
				'os': host_os,
				'osaction': 'memtest',
				'rack': '0',
				'rank': '0'
			},
			{
				'appliance': 'backend',
				'box': 'default',
				'comment': None,
				'environment': None,
				'host': 'backend-0-1',
				'installaction': 'console',
				'os': host_os,
				'osaction': 'memtest',
				'rack': '0',
				'rank': '1'
			}
		]
