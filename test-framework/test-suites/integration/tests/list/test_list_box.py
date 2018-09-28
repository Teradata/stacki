import json
from textwrap import dedent


class TestListBox:
	def test_list_box_invalid(self, host):
		result = host.run('stack list box test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid box
			[box ...]
		''')

	def test_list_box_no_args(self, host, host_os):
		# Add a second box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Run list box without args
		result = host.run('stack list box output-format=json')
		assert result.rc == 0

		# Make sure we got data for both our boxes
		boxes = {box['name']: box['os'] for box in json.loads(result.stdout)}
		assert boxes == {
			'default': host_os,
			'test': host_os
		}

	def test_list_box_one_arg(self, host, host_os):
		# Add a second box so we can make sure it is skipped
		result = host.run('stack add box test')
		assert result.rc == 0

		# Run list box with just the test box
		result = host.run('stack list box test output-format=json')
		assert result.rc == 0

		# Make sure we got data only for the test box
		boxes = {box['name']: box['os'] for box in json.loads(result.stdout)}
		assert boxes == {
			'test': host_os
		}

	def test_list_box_multiple_args(self, host, host_os):
		# Add a second box to be included
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add a third box to be skipped
		result = host.run('stack add box foo')
		assert result.rc == 0

		# Run list box with just the test box
		result = host.run('stack list box default test output-format=json')
		assert result.rc == 0

		# Make sure we got data only for the two boxes
		boxes = {box['name']: box['os'] for box in json.loads(result.stdout)}
		assert boxes == {
			'default': host_os,
			'test': host_os
		}
