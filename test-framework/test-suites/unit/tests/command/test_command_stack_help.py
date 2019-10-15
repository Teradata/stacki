import importlib
from stack.exception import CommandError
from stack.api import Call


class TestHelp:
	def test_all_commands_have_help(self):
		'''
		test that all stack commands ship with a functional help command
		'''

		missing = []
		malformed = []

		commands = Call('list.pallet.command', ['stacki'])

		for row in commands:
			command_name = row['command']
			module = importlib.import_module(f"stack.commands.{command_name.replace(' ', '.')}")
			cmd_obj = module.Command(None)
			try:
				cmd_obj.help(command_name)
			except CommandError:
				malformed.append(command_name)
				continue

			docstring = cmd_obj.getText()
			if not docstring:
				missing.append(command_name)
			elif docstring == f'stack {row["command"]} \n\nDescription\n':
				missing.append(command_name)

		errors = []
		if missing:
			errors.append('the following commands are missing docstrings: ' + ', '.join(missing))
		if malformed:
			errors.append('the following commands have malformed docstrings: ' + ', '.join(malformed))

		assert not any(missing + malformed), '\n'.join(errors)
