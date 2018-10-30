import json
from textwrap import dedent


class TestRemoveSwitch:
	def test_no_args(self, host):
		result = host.run('stack remove switch')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "switch" argument is required
			{switch}
		''')

	def test_invalid_switch(self, host):
		result = host.run('stack remove switch switch-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "switch-0-0" argument is not a valid switch
			{switch}
		''')

	def test_x1052(self, host, add_switch):
		# Confirm our switch exists
		result = host.run('stack list switch switch-0-0 output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [{
			'appliance': 'switch',
			'make': 'fake',
			'model': 'unrl',
			'rack': '0',
			'rank': '0',
			'switch': 'switch-0-0'
		}]

		# Now remove it
		result = host.run('stack remove switch switch-0-0')
		assert result.rc == 0

		# Make sure it is gone
		result = host.run('stack list switch switch-0-0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "switch-0-0" argument is not a valid switch
			[switch ...] [expanded=boolean]
		''')
