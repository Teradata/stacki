import re
from stack.exception import CommandError

def checkCommand(obj, command):
		# Check if the command exist. To do this, transform the
		# command from "{verb} [obj] [*] to verb.obj.*. Then subject
		# it to the regular expression match to remove any commands
		# with just * or a * in the middle of the command.
		cmd = re.sub('[ \t]+','.',command)
		cmd_re = re.compile('^([a-z]+\.?)+(\*)?$')
		if not cmd_re.match(cmd):
			raise CommandError(obj, "Invalid command specification")

		# If we're here, that means the command specification
		# was correct. Take the trailing .* off, and check if
		# the rest of the command is correct
		cmd = cmd.rstrip('.*')
		mod = "stack.commands.%s" % cmd
		cmd_found = False
		try:
			__import__(mod)
			# If we're here that means the import and eval succeeded. 
			cmd_found = True
		except:
			pass
		if not cmd_found:
			raise CommandError(obj, f"Command {command} not found")
