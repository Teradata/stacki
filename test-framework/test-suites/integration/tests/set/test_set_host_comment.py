import json
from textwrap import dedent


class TestSetHostComment:
	def test_no_hosts(self, host):
		result = host.run('stack set host comment')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {comment=string}
		''')

	def test_no_matching_hosts(self, host):
		result = host.run('stack set host comment a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {comment=string}
		''')

	def test_no_parameters(self, host):
		result = host.run('stack set host comment frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "comment" parameter is required
			{host ...} {comment=string}
		''')

	def test_too_long(self, host):
		comment = 'A' * 141
		result = host.run(f'stack set host comment frontend-0-0 comment={comment}')
		assert result.rc == 255
		assert result.stderr == 'error - comments must be no longer than 140 characters\n'

	def test_single_host(self, host, add_host, host_os):
		# Set the host comment
		result = host.run('stack set host comment backend-0-0 comment=test')
		assert result.rc == 0

		# Check that it made it into the database
		result = host.run('stack list host backend-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'backend',
			'box': 'default',
			'comment': 'test',
			'environment': None,
			'host': 'backend-0-0',
			'installaction': 'default',
			'os': host_os,
			'osaction': 'default',
			'rack': '0',
			'rank': '0'
		}]

	def test_multiple_hosts(self, host, add_host, host_os):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Set the host comment on both backends
		result = host.run('stack set host comment backend-0-0 backend-0-1 comment=test')
		assert result.rc == 0

		# Check that the change made it into the database
		result = host.run(f'stack list host a:backend output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'appliance': 'backend',
				'box': 'default',
				'comment': 'test',
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
				'box': 'default',
				'comment': 'test',
				'environment': None,
				'host': 'backend-0-1',
				'installaction': 'default',
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '1'
			}
		]
