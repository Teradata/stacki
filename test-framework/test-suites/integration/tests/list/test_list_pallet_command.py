from collections import defaultdict
import json
from textwrap import dedent


class TestListPalletCommand:
	def test_invalid_pallet(self, host):
		result = host.run('stack list pallet command test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid pallet
			[pallet ...] [arch=string] [os=string] [release=string] [version=string]
		''')

	def test_no_args(self, host, host_os):
		# List out the commands for all pallets
		result = host.run('stack list pallet command output-format=json')
		assert result.rc == 0

		# Group the commands by pallet
		commands = defaultdict(list)
		for item in json.loads(result.stdout):
			commands[item['pallet']].append(item['command'])

		# We should have at least two pallets
		assert len(commands) >= 2

		# That stacki pallet should have a ton of commands
		assert len(commands['stacki']) > 200

		# The OS pallet shouldn't have any commands
		if host_os == 'sles':
			assert commands['SLES'] == ['']
		else:
			assert commands['CentOS'] == ['']

	def test_one_arg(self, host):
		# List out the commands for just the stacki pallet
		result = host.run('stack list pallet command stacki output-format=json')
		assert result.rc == 0

		# Group the commands by pallet
		commands = defaultdict(list)
		for item in json.loads(result.stdout):
			commands[item['pallet']].append(item['command'])

		# We should only have a single pallet
		assert len(commands) == 1

		# That stacki pallet should have a ton of commands
		assert len(commands['stacki']) > 200

	def test_multiple_args(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add two of the test pallets
		result = host.run(f'stack add pallet {create_pallet_isos}/test_1-sles-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		result = host.run(f'stack add pallet {create_pallet_isos}/test_1-redhat-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# List out the commands for the stacki pallet and our two test ones
		result = host.run('stack list pallet command stacki test_1-sles test_1-redhat output-format=json')
		assert result.rc == 0

		# Group the commands by pallet
		commands = defaultdict(list)
		for item in json.loads(result.stdout):
			commands[item['pallet']].append(item['command'])

		# We should only have three pallets
		assert len(commands) == 3

		# That stacki pallet should have a ton of commands
		assert len(commands['stacki']) > 200

		# The test pallets shouldn't have any
		assert commands['test_1-sles'] == ['']
		assert commands['test_1-redhat'] == ['']

	def test_missing_rollname(self, host):
		# Comment out the 'RollName' from the `list pallet command`
		result = host.run(
			"sed -i 's/^RollName/#RollName/' "
			"/opt/stack/lib/python3.6/site-packages/"
			"stack/commands/list/pallet/command/__init__.py"
		)
		assert result.rc == 0

		# List out the commands for just the stacki pallet
		result = host.run('stack list pallet command stacki output-format=json')
		assert result.rc == 0

		# Group the commands by pallet
		commands = defaultdict(list)
		for item in json.loads(result.stdout):
			commands[item['pallet']].append(item['command'])

		# We should only have a single pallet
		assert len(commands) == 1

		# That stacki pallet should have a ton of commands
		assert len(commands['stacki']) > 200

		# But `list pallet command` shouldn't be in the list
		assert 'list pallet command' not in commands['stacki']

		# Undo the 'RollName' change
		result = host.run(
			'rpm -iv --replacepkgs '
			'`find /export/stack/pallets/stacki/ -name stack-command*rpm`'
		)
		assert result.rc == 0

		# now check again
		# List out the commands for just the stacki pallet
		result = host.run('stack list pallet command stacki output-format=json')
		assert result.rc == 0

		# Group the commands by pallet
		commands = defaultdict(list)
		for item in json.loads(result.stdout):
			commands[item['pallet']].append(item['command'])

		# `list pallet command` should be back in the list
		assert 'list pallet command' in commands['stacki']
