# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from . import Switch, SwitchException
import re
from pathlib import Path
from functools import wraps
from threading import Timer
from stack.expectmore import ExpectMore, ExpectMoreException

def _requires_regular_console(member_function):
	"""Decorator to ensure that the switch is at the regular console before running the decorated function."""
	@wraps(member_function)
	def wrapper(self, *args, **kwargs):
		"""Make sure we are at the normal console, and get us there if we are not."""
		# q will exit out of an existing scrollable more/less type of prompt
		# Probably not necessary, but a bit safer. Use this to check the current prompt.
		self.proc.say(cmd = "q")
		# If we're not at the regular console, we need to get out of the configure console.
		# "exit" will get us back to the normal console.
		if self.proc.match_index != self.CONSOLE_PROMPTS.index(self.CONSOLE_PROMPT):
			self.proc.say(cmd = "exit")
			if self.proc.match_index != self.CONSOLE_PROMPTS.index(self.CONSOLE_PROMPT):
				raise SwitchException(f"Could not get to the base switch console for {self.switchname}. Did a firmware update change the prompts?")

		# Run the wrapped member function
		return member_function(self, *args, **kwargs)

	return wrapper

def _requires_configure_console(member_function):
	"""Decorator to ensure that the switch is at the configure console before running the decorated function."""
	@wraps(member_function)
	def wrapper(self, *args, **kwargs):
		"""Make sure we are at the configure console, and get us there if we are not."""
		# q will exit out of an existing scrollable more/less type of prompt
		# Probably not necessary, but a bit safer. Use this to check the current prompt.
		self.proc.say(cmd = "q")
		# If we're not at the configure console, we need to get into the configure console.
		# "configure" should get us into the configure mode.
		if self.proc.match_index != self.CONSOLE_PROMPTS.index(self.CONFIGURE_CONSOLE_PROMPT):
			self.proc.say(cmd = "configure")
			if self.proc.match_index != self.CONSOLE_PROMPTS.index(self.CONFIGURE_CONSOLE_PROMPT):
				raise SwitchException(f"Could not get to the configure console for {self.switchname}. Did a firmware update change the prompts?")

		# Run the wrapped member function
		return member_function(self, *args, **kwargs)

	return wrapper

class SwitchDellX1052(Switch):
	"""
	Class for interfacing with a Dell x1052 switch.
	"""
	CONSOLE_PROMPT = "console#"
	CONFIGURE_CONSOLE_PROMPT = "console.config.#"
	CONSOLE_PROMPTS = [CONSOLE_PROMPT, CONFIGURE_CONSOLE_PROMPT,]
	PAGING_PROMPT = r"^.*More:.*<return>"
	OVERWRITE_PROMPT = r"^.*Overwrite file.*\?"
	COPY_SUCCESS = "The copy operation was completed successfully"

	def __init__(self, *args, **kwargs):
		"""Override __init__ to set up expectmore. Let the superclass __init__ do everything else."""
		self.proc = ExpectMore(prompts = self.CONSOLE_PROMPTS)
		super().__init__(*args, **kwargs)

	def supported(*cls):
		return [
			('Dell', 'x1052'),
		]

	def connect(self):
		"""Connect to the switch"""
		try:
			# Don't connect if we are already connected.
			if self.proc.isalive():
				return

			self.proc.start(cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -tt {self.switch_ip_address}")
			self.proc.conversation(
				response_pairs = [
					("User Name:", self.username),
					("Password:", self.password),
					(self.CONSOLE_PROMPTS, None),
				]
			)
		except ExpectMoreException:
			raise SwitchException(f"Couldn't connect to {self.switchname}")

	@_requires_regular_console
	def disconnect(self):
		"""Disconnect from the switch if a connection is active."""
		# if we've already disconnected, don't try again.
		if not self.proc.isalive():
			return

		# Send the exit command.
		self.proc.end(quit_cmd = "exit")

	@_requires_regular_console
	def get_mac_address_table(self):
		"""Download and parse the mac address table and return list of connected macs"""
		_hosts = []
		# Get the mac address table. The switch might page the output, so send commands to
		# read more of the output until it is all read.
		results = self._read_paged_output(cmd = "show mac address-table")

		# Parse the results
		for line in results:
			if 'dynamic' in line:
				# appends line to list
				# map just splits out the port
				#   from the interface
				_hosts.append(list(
					map(lambda x: x.split('/')[-1],
					line.split())
				))

		return sorted(_hosts, key=lambda x: x[2])

	@_requires_regular_console
	def get_interface_status_table(self):
		"""Download and parse the interface status and return list of port information"""
		_hosts = []
		# Get the interface status table. The switch might page the output, so send commands to
		# read more of the output until it is all read.
		results = self._read_paged_output(cmd = "show interfaces status")

		# Parse the results out of the file
		for line in results:
			if 'gi1/0/' in line:
				# appends line to list
				# map just splits out the port
				#   from the interface
				_hosts.append(list(
					map(lambda x: x.split('/')[-1],
					line.split())
				))

		return _hosts

	def _read_paged_output(self, cmd):
		"""Send the command and use spacebar to read more of the output until we have paged through it all."""
		prompts = [*self.CONSOLE_PROMPTS, self.PAGING_PROMPT]
		results = self.proc.ask(cmd = cmd, prompt = prompts)
		# Sometimes the paging ends up putting the results in the pexpect "after" buffer, so grab it
		# if we got no results.
		if not results:
			results = self.proc.after

		# timeout after 1 minute of attempting to page through the output.
		# We use a no-op lambda because we just want to know when the timer expired.
		timer = Timer(60, lambda: ())
		timer.start()
		# Keep paging through the output if we matched on the paging prompt.
		while self.proc.match_index == prompts.index(self.PAGING_PROMPT):
			# Check for timeout condition and raise a SwitchException if we timed out.
			if not timer.is_alive():
				raise SwitchException(
					f"Timed out trying to page through output for command {cmd} on {self.switchname}."
					" Did the console output format change?"
				)

			# The "more output please" button is spacebar.
			paged_results = self.proc.ask(cmd = "\x20", prompt = prompts)
			# Sometimes the paging ends up putting the results in the pexpect "after" buffer, so grab it
			# if we got no results.
			if not paged_results:
				paged_results = self.proc.after

			results.extend(paged_results)

		timer.cancel()
		# Remove the paging menu from the lines if it was captured in the output.
		return [re.sub(self.PAGING_PROMPT, "", line, flags = re.IGNORECASE) for line in results]

	@_requires_regular_console
	def download(self):
		"""Download the running-config from the switch to the server"""
		#
		# tftp requires the destination file to already exist and to be writable by all
		#
		filename = Path(self.tftpdir).resolve(strict = True) / self.current_config
		filename.touch(exist_ok = True)
		filename.chmod(mode = 0o777)

		results = self.proc.ask(
			cmd = f"copy running-config tftp://{self.stacki_server_ip}/{self.current_config}",
		)

		# ensure we copied successfully
		if not self._check_success(results = results, success_string = self.COPY_SUCCESS):
			raise SwitchException(f"Failed to download the running config from {self.switchname}")

	@_requires_regular_console
	def upload(self):
		"""Upload the file from the switch to the server"""
		prompts = [*self.CONSOLE_PROMPTS, self.OVERWRITE_PROMPT]
		# Copy the file
		results = self.proc.ask(
			cmd = f"copy tftp://{self.stacki_server_ip}/{self.new_config} temp",
			prompt = prompts,
		)
		# If it's prompting to confirm overwrite, say yes
		if self.proc.match_index == prompts.index(self.OVERWRITE_PROMPT):
			results = self.proc.ask(cmd = "Y", prompt = self.CONSOLE_PROMPTS)

		# ensure we copied successfully
		if not self._check_success(results = results, success_string = self.COPY_SUCCESS):
			raise SwitchException(f"Failed to upload the new config to {self.switchname}")

		#
		# we remove all VLANs (2-4094) which is time consuming, so up the timeout to 30
		#
		results = self.proc.ask(cmd = "copy temp running-config", prompt = prompts, timeout = 30)
		# If it's prompting to confirm overwrite, say yes
		if self.proc.match_index == prompts.index(self.OVERWRITE_PROMPT):
			results = self.proc.ask(cmd = "Y", prompt = self.CONSOLE_PROMPTS, timeout = 30)

		# ensure we copied successfully
		if not self._check_success(results = results, success_string = self.COPY_SUCCESS):
			raise SwitchException(f"Failed to ovewrite the running config on {self.switchname}")

	@_requires_regular_console
	def apply_configuration(self):
		"""Apply running-config to startup-config"""
		prompts = [*self.CONSOLE_PROMPTS, self.OVERWRITE_PROMPT]

		results = self.proc.ask(cmd = "write", prompt = prompts)
		# If it's prompting to confirm overwrite, say yes
		if self.proc.match_index == prompts.index(self.OVERWRITE_PROMPT):
			results = self.proc.ask(cmd = "Y", prompt = self.CONSOLE_PROMPTS)

		# ensure we applied successfully
		if not self._check_success(results = results, success_string = self.COPY_SUCCESS):
			raise SwitchException(f"Failed to apply the new config to {self.switchname}")

	def set_tftp_ip(self, ip):
		self.stacki_server_ip = ip

	def _check_success(self, results, success_string):
		"""Checks that the success string was found in the output."""
		for line in results:
			if success_string in line:
				return True

		return False
