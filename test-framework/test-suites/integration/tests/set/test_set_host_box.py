import json
from textwrap import dedent


class TestSetHostBox:
	def test_set_host_box_no_hosts(self, host):
		result = host.run('stack set host box')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {box=string}
		''')

	def test_set_host_box_no_matching_hosts(self, host):
		result = host.run('stack set host box a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {box=string}
		''')

	def test_set_host_box_no_parameters(self, host):
		result = host.run('stack set host box frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "box" parameter is required
			{host ...} {box=string}
		''')

	def test_set_host_box_invalid_box(self, host):
		result = host.run('stack set host box frontend-0-0 box=test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid box
			{host ...} {box=string}
		''')

	def test_set_host_box_single_host(self, host, add_host, add_box, host_os):
		# Set the host box
		result = host.run('stack set host box backend-0-0 box=test')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'test',
			'comment': None,
			'environment': None,
			'host': 'backend-0-0',
			'installaction': 'default',
			'os': host_os,
			'osaction': 'default',
			'rack': '0',
			'rank': '0'
		}]

	def test_set_host_box_multiple_hosts(self, host, add_host, add_box, host_os):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Set the host box on both backends
		result = host.run('stack set host box backend-0-0 backend-0-1 box=test')
		assert result.rc == 0

		# Check that the change made it into the database
		result = host.run(f'stack list host a:backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'box': 'test',
				'comment': None,
				'environment': None,
				'host': 'backend-0-0',
				'installaction': 'default',
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '0'
			},
			{
				'appliance': 'backend',
				'box': 'test',
				'comment': None,
				'environment': None,
				'host': 'backend-0-1',
				'installaction': 'default',
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '1'
			}
		]
