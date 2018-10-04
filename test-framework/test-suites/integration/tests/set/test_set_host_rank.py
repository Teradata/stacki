import json
from textwrap import dedent


class TestSetHostRank:
	def test_set_host_rank_no_hosts(self, host):
		result = host.run('stack set host rank')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {rank=string}
		''')

	def test_set_host_rank_no_matching_hosts(self, host):
		result = host.run('stack set host rank a:test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "host" argument is required
			{host ...} {rank=string}
		''')

	def test_set_host_rank_no_parameters(self, host):
		result = host.run('stack set host rank frontend-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "rank" parameter is required
			{host ...} {rank=string}
		''')

	def test_set_host_rank_single_host(self, host, add_host, host_os):
		# Set the host rank
		result = host.run('stack set host rank backend-0-0 rank=1')
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
			'installaction': 'default',
			'os': host_os,
			'osaction': 'default',
			'rack': '0',
			'rank': '1'
		}]

	def test_set_host_rank_multiple_hosts(self, host, add_host, host_os):
		# Add a second test backend
		add_host('backend-0-1', '0', '1', 'backend')

		# Set the host rank on both backends
		result = host.run('stack set host rank backend-0-0 backend-0-1 rank=2')
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
				'installaction': 'default',
				'os': host_os,
				'osaction': 'default',
				'rack': '0',
				'rank': '2'
			},
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
