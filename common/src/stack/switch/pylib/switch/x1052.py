# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from . import Switch, SwitchException
import re
from pathlib import Path
from functools import wraps
from threading import Timer
from collections import namedtuple
import tempfile
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
	CONTINUE_PROMPT = r"^.*continue.*\?"
	SHUTDOWN_PROMPT = r"^.*Shutting down"
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
		"""Download the running-config from the switch to the server.

		If downloading the config fails, a SwitchException is raised.
		"""
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
		"""Upload the file from the switch to the server.

		If uploading the config fails, a SwitchException is raised.
		"""
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
		"""Apply running-config to startup-config.

		If applying the config fails, a SwitchException is raised.
		"""
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

	def _parse_versions(self, results):
		"""Parses out the versions and returns a namedtuple of software, boot, and hardware versions found.

		The results are returned as a namedtuple with the attributes software, boot, and hardware. Each is a list
		containing the versions found in the provided results.
		"""
		# Parse out the firmware versions
		software = []
		boot = []
		hardware = []
		for line in results:
			software_regex = r"SW version"
			software_match = re.search(pattern = software_regex, string = line, flags = re.IGNORECASE)
			# If we found the software version, add it to the results.
			if software_match:
				software.append(
					# Drop the heading and strip leading and trailing whitespace.
					re.sub(pattern = software_regex, repl = "", string = line, flags = re.IGNORECASE).strip()
				)

			boot_regex = r"Boot version"
			boot_match = re.search(pattern = boot_regex, string = line, flags = re.IGNORECASE)
			# If we found the boot version, add it to the results.
			if boot_match:
				boot.append(
					# Drop the heading and strip leading and trailing whitespace.
					re.sub(pattern = boot_regex, repl = "", string = line, flags = re.IGNORECASE).strip()
				)

			hardware_regex = r"HW version"
			hardware_match = re.search(pattern = hardware_regex, string = line, flags = re.IGNORECASE)
			# If we found the hardware version, add it to the results.
			if hardware_match:
				hardware.append(
					# Drop the heading and strip leading and trailing whitespace.
					re.sub(pattern = hardware_regex, repl = "", string = line, flags = re.IGNORECASE).strip()
				)

		return namedtuple("ParsedVersions", ("software", "boot", "hardware"))(
			software = software,
			boot = boot,
			hardware = hardware,
		)

	def _check_parsed_versions(self, parsed_versions):
		"""Validate that for software, boot, and hardware that exactly one version number was parsed.

		If there were any parsing errors, a SwitchException is raised.
		"""
		# There must be only one version found for each. Yell loudly if we found multiple.
		errors = []
		if not parsed_versions.software:
			errors.append(f"No software version reported for {self.switchname}.")
		elif len(parsed_versions.software) > 1:
			errors.append(f"Multiple software versions reported for {self.switchname}: {parsed_versions.software}.")
		# Else we're good

		if not parsed_versions.boot:
			errors.append(f"No boot version reported for {self.switchname}.")
		elif len(parsed_versions.boot) > 1:
			errors.append(f"Multiple boot versions reported for {self.switchname}: {parsed_versions.boot}.")
		# Else we're good

		if not parsed_versions.hardware:
			errors.append(f"No hardware version reported for {self.switchname}.")
		elif len(parsed_versions.hardware) > 1:
			errors.append(f"Multiple hardware versions reported for {self.switchname}: {parsed_versions.hardware}.")
		# Else we're good

		# Throw an exception if there were any parsing errors
		if errors:
			errors.append("Did the console output format change?")
			errors = " ".join(errors)
			raise SwitchException(errors)

	@_requires_regular_console
	def get_versions(self):
		"""Returns the current software, boot, and hardware versions as a namedtuple.

		The software attribute returns the software version, the boot attribute returns the boot version,
		and the hardware attribute returns the hardware version.

		If there was any error parsing the results, a SwitchException is raised.
		"""
		# Get the current version information from the switch
		results = self.proc.ask(cmd = "show version")
		parsed_versions = self._parse_versions(results = results)
		self._check_parsed_versions(parsed_versions = parsed_versions)

		return namedtuple("Versions", ("software", "boot", "hardware"))(
			software = parsed_versions.software[0],
			boot = parsed_versions.boot[0],
			hardware = parsed_versions.hardware[0],
		)

	def _upload_tftp(self, source, destination, timeout):
		"""Uploads the provided source file via TFTP to the destination on the switch.

		This will return the resulting console output from the upload operation.

		If the source file does not exist on disk, a FileNotFoundError is raised.
		"""
		source_file = Path(source).resolve(strict = True)
		full_tftp_directory = Path(self.tftpdir) / self.switchname
		full_tftp_directory = full_tftp_directory.resolve(strict = True)

		# Copy into the TFTP directory so we can TFTP it to the switch.
		# Use a temporary file so we don't litter the filesystem with files. It has to be named
		# so that the switch can find it.
		with tempfile.NamedTemporaryFile(dir = full_tftp_directory) as temp_file:
			# Copy the data to the temporary file and flush it.
			temp_file.write(source_file.read_bytes())
			temp_file.flush()
			# Need to chmod the file so that the switch can read it.
			temp_file_path = Path(temp_file.name)
			temp_file_path.chmod(mode = 0o777)

			# TFTP the firmware file to the server
			return self.proc.ask(
				cmd = f"copy tftp://{self.stacki_server_ip}/{temp_file_path.parent.stem}/{temp_file_path.stem} {destination}",
				timeout = timeout,
			)

	@_requires_regular_console
	def upload_software(self, software_file):
		"""Uploads the provided software file to the switch.

		If the upload was not successful, a SwitchException is raised.

		If the source file does not exist, a FileNotFoundError is raised.
		"""
		# Copy the software image to the switch. Give a long timeout (10 minutes) to allow for time to upload
		# the potentially large software image.
		results = self._upload_tftp(source = software_file, destination = "image", timeout = 600)

		# ensure we copied successfully
		if not self._check_success(results = results, success_string = self.COPY_SUCCESS):
			raise SwitchException(f"Failed to upload new software file {software_file} to {self.switchname}")

	@_requires_regular_console
	def upload_boot(self, boot_file):
		"""Uploads the provided boot file to the switch.

		If the upload was not successful, a SwitchException is raised.

		If the source file does not exist, a FileNotFoundError is raised.
		"""
		# Copy the boot image to the switch. Give a long timeout (10 minutes) to allow for time to upload
		# the potentially large boot image.
		results = self._upload_tftp(source = boot_file, destination = "boot", timeout = 600)

		# ensure we copied successfully
		if not self._check_success(results = results, success_string = self.COPY_SUCCESS):
			raise SwitchException(f"Failed to upload new boot file {boot_file} to {self.switchname}")

	@_requires_regular_console
	def reload(self):
		"""Reboots the switch.

		This will disconnect from the switch. Connect will have to be called again once it reboots
		before any other commands can be issued.
		"""
		prompts = [self.CONTINUE_PROMPT, self.SHUTDOWN_PROMPT]

		self.proc.say(cmd = "reload", prompt = prompts)
		# If it's prompting to confirm reload, say yes. It may prompt multiple times in a downgrade scenario.
		# Timeout after 1 minute of attempting to confirm all the prompts.
		# We use a no-op lambda because we just want to know when the timer expired.
		timer = Timer(60, lambda: ())
		timer.start()
		while self.proc.match_index == prompts.index(self.CONTINUE_PROMPT):
			# Check for timeout condition and raise a SwitchException if we timed out.
			if not timer.is_alive():
				raise SwitchException(
					f"Timed out trying to confirm reload on {self.switchname}."
					" Did the console output format change?"
				)

			# We must use pexpect.spawn.send instead of pexpect.spawn.sendline as the switch appears to treat the
			# os.linesep that pexpect sends as auto cancelling the second confirmation prompt.
			self.proc.say(cmd = "Y", prompt = prompts, sendline = False)

		timer.cancel()
		# Now unconditionally terminate the process as we've hit one of the expected prompts and the switch
		# doesn't appear to gracefully terminate the ssh session on reboot.
		self.proc.end(quit_cmd = "", prompt = "")
