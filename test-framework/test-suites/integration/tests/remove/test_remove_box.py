import json
from textwrap import dedent


class TestRemoveBox:
	def test_no_args(self, host):
		result = host.run('stack remove box')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "box" argument is required
			{box}
		''')

	def test_invalid(self, host):
		result = host.run('stack remove box test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid box
			{box}
		''')

	def test_default(self, host):
		result = host.run('stack remove box default')
		assert result.rc == 255
		assert result.stderr == 'error - cannot remove default box\n'

	def test_in_use(self, host, add_box, add_host):
		# Add our backend-0-0 to the new test box
		result = host.run('stack set host box backend-0-0 box=test')
		assert result.rc == 0

		# Now try to remove the test box
		result = host.run('stack remove box test')
		assert result.rc == 255
		assert result.stderr == 'error - cannot remove box "test" because host "backend-0-0" is assigned to it\n'

	def test_single_arg(self, host, add_box, host_os):
		# Confirm the test box is there
		result = host.run('stack list box test output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'test',
				'os': host_os,
				'pallets': '',
				'carts': '',
				'repos': '',
			}
		]

		# Now remove it
		result = host.run('stack remove box test')
		assert result.rc == 0

		# And confirm it is gone
		result = host.run('stack list box test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid box
			[box ...]
		''')

	def test_multiple_args(self, host, add_box, host_os):
		# Create a second box
		add_box('foo')

		# Confirm both boxes are there
		result = host.run('stack list box test foo output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'name': 'test',
				'os': host_os,
				'pallets': '',
				'carts': '',
				'repos': '',
			},
			{
				'name': 'foo',
				'os': host_os,
				'pallets': '',
				'carts': '',
				'repos': '',
			}
		]

		# Now remove our boxes
		result = host.run('stack remove box test foo')
		assert result.rc == 0

		# And confirm they are gone
		result = host.run('stack list box test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid box
			[box ...]
		''')

		result = host.run('stack list box foo')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "foo" argument is not a valid box
			[box ...]
		''')
