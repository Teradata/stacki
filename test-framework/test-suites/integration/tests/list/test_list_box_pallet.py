import json
from textwrap import dedent


class TestListBoxPallet:
	def test_invalid(self, host):
		result = host.run('stack list box pallet test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid box
			[box ...]
		''')

	def test_no_args(self, host, revert_etc):
		# Add a second box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add a pallet to our test box
		result = host.run('stack enable pallet stacki box=test')
		assert result.rc == 0

		# Run list box pallet without args
		result = host.run('stack list box pallet output-format=json')
		assert result.rc == 0

		# Make sure we got data for both our boxes
		boxes = set(item['box'] for item in json.loads(result.stdout))
		assert len(boxes) == 2
		assert 'default' in boxes
		assert 'test' in boxes

	def test_one_arg(self, host, revert_etc):
		# Add a second box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add a pallet to our test box
		result = host.run('stack enable pallet stacki box=test')
		assert result.rc == 0

		# Run list box pallet with just the test box
		result = host.run('stack list box pallet test output-format=json')
		assert result.rc == 0

		# Make sure we got data only for the test box
		boxes = [item['box'] for item in json.loads(result.stdout)]
		assert boxes == ['test']

	def test_multiple_args(self, host, host_os, revert_etc):
		# Add a second box to be included
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add a pallet to our test box
		result = host.run('stack enable pallet stacki box=test')
		assert result.rc == 0

		# Add a third box to be skipped
		result = host.run('stack add box foo')
		assert result.rc == 0

		# Add a pallet to our skipped box
		result = host.run('stack enable pallet stacki box=foo')
		assert result.rc == 0

		# Run list box pallet with two boxes
		result = host.run('stack list box pallet default test output-format=json')
		assert result.rc == 0

		# Make sure we got data only for the two boxes
		boxes = set(item['box'] for item in json.loads(result.stdout))
		assert len(boxes) == 2
		assert 'default' in boxes
		assert 'test' in boxes
