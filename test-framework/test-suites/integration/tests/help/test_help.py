from textwrap import dedent

import pytest


class TestHelp:
	def test_no_args(self, host):
		result = host.run('stack help')
		assert result.rc == 0

		# So that this test doesn't break when a new command is added,
		# we'll just spot check a few commands and make sure a whole
		# lot of lines are returned.
		assert len(result.stdout.split('\n')) > 200
		assert 'list host' in result.stdout
		assert 'sync host' in result.stdout

	def test_with_substring(self, host):
		result = host.run('stack help set bootaction')
		assert result.rc == 0
		with open(f'/export/test-files/help/help_set_bootaction.txt') as output:
			assert result.stdout == output.read()

	@pytest.mark.parametrize('format', ['plain', 'raw', 'parsed', 'md'])
	def test_command_help(self, host, format):
		result = host.run(f'stack add pallet help format={format}')
		assert result.rc == 255
		with open(f'/export/test-files/help/add_pallet_{format}.txt') as output:
			assert result.stdout == output.read()

	def test_command_help_no_format(self, host):
		result = host.run(f'stack add pallet help')
		assert result.rc == 255
		with open(f'/export/test-files/help/add_pallet_plain.txt') as output:
			assert result.stdout == output.read()

	def test_command_help_docbook(self, host):
		result = host.run(f'stack add pallet help format=docbook')
		assert result.rc == 255
		assert result.stderr == 'error - "docbook" no longer supported - use "markdown"\n'
