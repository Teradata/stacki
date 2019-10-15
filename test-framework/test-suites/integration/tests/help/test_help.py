import pytest
import ast

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

	def test_with_substring(self, host, test_file):
		result = host.run('stack help set bootaction')
		assert result.rc == 0
		with open(test_file('help/help_set_bootaction.txt')) as output:
			assert result.stdout == output.read()

	def test_command_help_different_formats(self, host):
		# plain is the normal stacki help output, so ensure those are the same
		result = host.run(f'stack list help help format=plain')
		assert result.rc == 255
		assert result.stdout != ''

		normalresult = host.run(f'stack list help help')
		assert normalresult.rc == 255
		assert normalresult.stdout != ''

		assert normalresult.stdout == result.stdout
		assert result.stdout.startswith('stack list help')

		# raw format is line numbers, starting with the description, but no headings
		result = host.run(f'stack list help help format=raw')
		assert result.rc == 255
		for li in result.stdout.splitlines():
			assert li.split(':', maxsplit=1)[0].isdigit()

		# md format is markdown
		result = host.run(f'stack list help help format=md')
		assert result.rc == 255
		sections = result.stdout.split('### ')
		assert sections[0].strip() == '## list help'
		assert sections[1].startswith('Usage')
		assert sections[2].startswith('Description')
		assert sections[3].startswith('Parameters')
		assert sections[4].startswith('Examples')
		assert '* `stack list help`' in sections[4]

		# parsed returns a python dictionary as a string...
		result = host.run(f'stack list help help format=parsed')
		assert result.rc == 255

		# ... so pass it through a safer eval so we can manipulate it
		parsed = ast.literal_eval(result.stdout)
		assert set(parsed.keys()) == {'optparam', 'reqarg', 'reqparam', 'example', 'optarg', 'description', 'related'}
		assert parsed['description'].startswith('The Help Command')
		assert parsed['example'][0][0] == 'list help'

	def test_command_help_docbook(self, host):
		result = host.run(f'stack add pallet help format=docbook')
		assert result.rc == 255
		assert result.stderr == 'error - "docbook" no longer supported - use "markdown"\n'
