# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import json
import subprocess


class StackCommandError(Exception):
    """Exception raised for errors running a stack command."""

    def __init__(self, message):
        self.message = message


def run_stack_command(command, args=None):
	"""Runs a stack command, returning StackCommandError if there is an error."""

	# Create our command to run
	command_args = ["/opt/stack/bin/stack"]
	command_args.extend(command.replace(".", " ").split())
	if args:
		command_args.extend(args)
	command_args.append("output-format=json")

	try:
		# Run the command, throwing a CalledProcessError if something goes wrong
		result = subprocess.run(
			command_args, capture_output=True, text=True, check=True
		)
	except subprocess.CalledProcessError as e:
		# Get the first line of the stderr
		if e.stderr:
			message = e.stderr.splitlines()[0]
		else:
			message = "error - unknown"

		# Raise an exception for the caller
		raise StackCommandError(message)

	# Return the result as a dict
	try:
		data = json.loads(result.stdout)
	except json.JSONDecodeError:
		# Something invalid was returned, likely an empty string
		data = []

	return data
