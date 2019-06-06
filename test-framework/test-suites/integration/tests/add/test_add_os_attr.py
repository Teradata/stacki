import json
from textwrap import dedent


class TestAddOSAttr:
	def test_no_args(self, host):
		result = host.run('stack add os attr attr=test value=True')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "os" argument is required
			{os ...} {attr=string} {value=string} [shadow=boolean]
		''')

	def test_existing(self, host, host_os):
		# Add a test attr
		result = host.run(f'stack add os attr {host_os} attr=test value=True')
		assert result.rc == 0

		# Make sure it got there
		result = host.run(f'stack list os attr {host_os} attr=test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'attr': 'test',
			'os': host_os,
			'scope': 'os',
			'type': 'var',
			'value': 'True'
		}]

		# Add the test attr again, which should fail
		result = host.run(f'stack add os attr {host_os} attr=test value=False')
		assert result.rc == 255
		assert result.stderr == 'error - attr "test" already exists\n'
