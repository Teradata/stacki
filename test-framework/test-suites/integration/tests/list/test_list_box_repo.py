import json
from textwrap import dedent


class TestListBoxRepo:
	def test_invalid(self, host):
		result = host.run('stack list box repo test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid box
			[box ...]
		''')

	def test_no_args(self, host, add_repo, revert_etc):
		# Add a second box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add a repo to our test box
		result = host.run('stack enable repo test box=test')
		assert result.rc == 0

		# Run list box repo without args
		result = host.run('stack list box repo output-format=json')
		assert result.rc == 0

		# Make sure we got data for more a single box
		boxes = set(item['box'] for item in json.loads(result.stdout))
		assert len(boxes) == 1
		assert 'test' in boxes

	def test_one_arg(self, host, add_repo, revert_etc):
		# Add a second box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add a repo to our test box
		result = host.run('stack enable repo test box=test')
		assert result.rc == 0

		# Run list box repo with just the test box
		result = host.run('stack list box repo test output-format=json')
		assert result.rc == 0

		# Make sure we got data only for the test box
		boxes = [item['box'] for item in json.loads(result.stdout)]
		assert boxes == ['test']

	def test_multiple_args(self, host, host_os, add_repo, revert_etc):
		# Add a second box to be included
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add a repo to our test box
		result = host.run('stack enable repo test box=test')
		assert result.rc == 0

		# Add a third box to be skipped
		result = host.run('stack add box foo')
		assert result.rc == 0

		# Add a repo to our skipped box
		result = host.run('stack enable repo test box=foo')
		assert result.rc == 0

		# Run list box repo with two boxes
		result = host.run('stack list box repo default test output-format=json')
		assert result.rc == 0

		# Make sure we got data only for one box - default box has no repo's in it
		boxes = set(item['box'] for item in json.loads(result.stdout))
		assert len(boxes) == 1
		assert 'test' in boxes
