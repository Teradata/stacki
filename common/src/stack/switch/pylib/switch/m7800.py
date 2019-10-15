import re
import syslog
import time

from collections import namedtuple
from stack.expectmore import ExpectMore, ExpectMoreException, remove_control_characters
from stack.bool import str2bool
from . import Switch, SwitchException
from . import mellanoknok

def info(message):
	syslog.syslog(syslog.LOG_INFO, f'm7800.py: {message}')

def remove_blank_lines(lines):
	"""Returns a new list with all blank lines removed."""
	return [line for line in lines if line.strip()]


# Needs to handle the old (< 3.6.8010) and new (>= 3.6.8010) formatting
partition_name = re.compile(r'(?P<format_1>  [a-z0-9]+\s*$)|(?P<format_2>[a-z0-9]+:\s*$)', re.IGNORECASE)
members_header = re.compile('  members', re.IGNORECASE)
# a GUID is a like a MAC, but 8 pairs
guid_format = re.compile("([0-9a-f]{2}:){7}[0-9a-f]{2}|ALL", re.IGNORECASE)
# a GID is like an ipv6? 20 pairs
gid_format = re.compile("([0-9a-f]{2}:){19}[0-9a-f]{2}|ALL", re.IGNORECASE)
guid_member_format = re.compile("(ALL|([0-9a-f]{2}:){7}[0-9a-f]{2}).*(full|both|limited)", re.IGNORECASE)

class SwitchMellanoxM7800(Switch):
	"""
	Class for interfacing with a Mellanox 7800 Infiniband Switch.
	"""
	SUPPORTED_IMAGE_FETCH_PROTOCOLS = ('http://', 'https://', 'ftp://', 'tftp://', 'scp://', 'sftp://')

	def supported(*cls):
		return [
			('Mellanox', 'm7800'),
		]

	def __init__(self, switch_ip_address, switchname='switch', username='admin', password=''):
		# Grab the user supplied info, in case there is a difference (PATCH)
		self.switch_ip_address = switch_ip_address
		self.username = username
		self.password = password

		self.switchname = switchname
		self.proc = ExpectMore()
		self.proc.PROMPTS = ['.config. #', ' >', ' #', 'initial configuration?']


	def connect(self):
		"""
		Connect to the switch and get a configuration prompt
		"""
		if self.proc.isalive():
			return

		ssh_options = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -tt'
		self.proc.start(f'ssh {ssh_options} {self.username}@{self.switch_ip_address}')
		info(f'ssh {ssh_options} {self.username}@{self.switch_ip_address}')

		try:
			self.proc.wait(['Password:', ' >'])
		except ExpectMoreException:
			raise SwitchException(f'Connection to switch at "{self.username}@{self.switch_ip_address}" unavailable')

		login_seq = [
			([' >', ''], 'terminal length 999'),
			(' >', 'enable'),
			(' #', 'configure terminal'),
			('.config. #', ''),
		]

		if self.proc.match_index == 0:
			info('password-based auth')
			# password-based auth
			try:
				self.proc.say(self.password)
			except ExpectMoreException:
				# try again with a factory default password
				self.proc.say('admin')
				# insert the conversation to disable the setup wizard
				# we are assuming this is a factory defaulted box
				login_seq.insert(0, ('', 'no'))
		# otherwise, key-based auth is already setup

		self.proc.conversation(login_seq)

		# don't worry if we can't connect -- too many connection attempts breaks the api
		# the library will auto try again if there's a method that actually needs it
		try:
			self._api_connection = mellanoknok.Mellanoknok(self.switch_ip_address, password=self.password)
		except:
			pass


	def disconnect(self):
		if self.proc.isalive():
			self.proc.end('quit')

	def set_password(self):
		"""Set the password on the switch to what we were initialized with."""
		# set the password for the given user
		self.proc.conversation(
			[
				('', f'username {self.username} password'),
				('Password:', self.password),
				('Confirm:', self.password),
			]
		)
		# disconnect and reconnect using the new password.
		self.disconnect()
		self.connect()

	@property
	def subnet_manager(self):
		""" get the subnet manager status for this switch """
		info('determining sm status')

		for line in self.proc.ask('show ib sm'):
			info(line)
			if 'enable' == line.strip():
				return True
			elif 'disable' == line.strip():
				return False

		raise SwitchException('unable to determine subnetmanager status')


	@subnet_manager.setter
	def subnet_manager(self, value):
		""" set the subnet manager status for this switch """
		cmd = 'ib sm'
		info(f'set {cmd}')
		if value:
			self.proc.say(cmd)
		else:
			self.proc.say('no ' + cmd)

		self.proc.say('configuration write')


	def ssh_copy_id(self, pubkey):
		""" relies on pubkey being a string whose format is exactly that of "id_rsa.pub" """

		self.proc.say(f'ssh client user admin authorized-key sshv2 "{pubkey}"')


	def wipe_ssh_keys(self):
		""" remove all authorized keys from the switch """

		info('wiping ssh keys from switch')
		key_section = False
		sshkeys = {}
		username = ''
		for line in self.proc.ask('show ssh client', seek='SSH authorized keys:'):
			line = line.strip()
			if line.startswith('User'):
				username = line.split()[1].rstrip(':')
				sshkeys[username] = []
				continue
			if line.startswith('Key'):
				key_id = line.split()[1].rstrip(':')
				sshkeys[username].append(key_id)
				continue

		for user, key_ids in sshkeys.items():
			for key in key_ids:
				info(f'removing key {key}')
				self.proc.say(f'no ssh client user {user} authorized-key sshv2 {key}')

	def set_hostname(self, hostname):
		self.subnet_manager = False
		# this doesn't happen immediately..
		i = 1
		while self.subnet_manager:
			time.sleep(i)
			self.subnet_manager = False
			i = i + 2
			if i > 11:
				raise SwitchException('waited over 30 seconds for subnet manager state to change')

		self.proc.say(f'hostname {hostname}')

		for host in self._get_smnodes():
			if host != hostname:
				self.proc.say(f'no ib smnode {host}')

		self.subnet_manager = True
		i = 1
		while not self.subnet_manager:
			time.sleep(i)
			self.subnet_manager = True
			i = i + 2
			if i > 11:
				raise SwitchException('waited over 30 seconds for subnet manager state to change')


	def _get_smnodes(self):
		nodes = self.proc.ask('no ib smnode ?', sanitizer=remove_control_characters)
		# hack.
		# the issue here is that the '?' above is similar to a tab-completion.
		# however, the string 'no ib smnode' gets put back on the buffer,
		# meaning every command after is garbage
		# ctrl-c on the CLI makes this go away, but sending the ctrl-c via pexpect doesn't seem to.
		# reconnecting fixes this.
		self.disconnect()
		self.connect()
		return nodes[1:-1]


	@property
	def partitions(self):
		"""
		Return a dictionary of the partitions.
		partition['partition_name'] = {'pkey': int, 'ipoib': bool, 'guids': [list, of, member, guids]}
		"""

		partitions = {}
		cur_partition = None
		new_console_format = None
		for line in remove_blank_lines(lines = self.proc.ask('show ib partition')):
			if re.match(members_header, line):
				# drop the 'members' line, because it can look like partition names
				# lord help us if someone names their partition 'members'
				continue

			header_match = re.match(partition_name, line)
			if header_match:
				# This should be the first thing we encounter when looping through the console
				# response, so we use it to set the format for the rest of the loop
				if new_console_format is None:
					if header_match.group("format_1"):
						new_console_format = False
					elif header_match.group("format_2"):
						new_console_format = True
				elif new_console_format and not header_match.group("format_2"):
					continue
				elif not new_console_format and not header_match.group("format_1"):
					continue

				cur_partition = line.strip().strip(":")
				partitions[cur_partition] = {
					'pkey': '',
					'ipoib': False,
					'guids': {},
				}
				continue

			line = line.strip()
			if line.startswith('PKey'):
				_, key = line.split(':' if new_console_format else '=')
				partitions[cur_partition]['pkey'] = int(key, 16)
			elif line.startswith('ipoib'):
				_, ipoib = line.split(':' if new_console_format else '=')
				partitions[cur_partition]['ipoib'] = str2bool(ipoib.strip())
			elif line.startswith('GUID'):
				m = re.search(guid_member_format, line)
				guid, membership = m.groups()[0].lower(), m.groups()[2]
				partitions[cur_partition]['guids'][guid] = membership

		info(partitions.keys())
		return partitions


	@property
	def interfaces(self):
		return self._api_connection.get_interfaces()


	def _validate_pkey(self, pkey):
		"""
		Valid pkey values are between 0x000 (2) to 0x7FFE (32766) (inclusive)
		0x7FFF is reserved for the Default partition.  0x0 is invalid
		"""

		try:
			pkey = int(pkey)
		except ValueError:
			return None
		if pkey < 2 and pkey > 32766:
			return None

		return hex(pkey)


	def add_partition(self, partition='Default', pkey=None, defmember=None, ipoib=None):
		"""
		Add `partition` to the switch, with partition key `pkey` which must be between 2-32766.
		`partition` 'Default' has a hard-coded pkey.
		"""
		info(f'adding partition {partition} pkey={pkey} defmember={defmember} ipoib={ipoib}')
		if partition != 'Default':
			if not pkey:
				raise SwitchException(f'a partition key is required for partition: {partition}.')
			pkey = self._validate_pkey(pkey)
			if not pkey:
				raise SwitchException(f'Infiniband partition keys must be between 2 and 32766, not {pkey}')
		else:
			pkey = '0x7fff'

		self.proc.say(f'ib partition {partition} pkey {pkey} force')

		if defmember:
			self.proc.say(f'ib partition {partition} defmember {defmember} force')
		elif defmember is None:
			if partition == 'Default':
				self.proc.conversation([
					(None, f'no ib partition {partition} defmember'),
					("Type 'yes' to continue:", 'yes'),
					(self.proc.PROMPTS, None),
				])
			else:
				self.proc.say(f'no ib partition {partition} defmember')

		if ipoib is True:
			self.proc.say(f'ib partition {partition} ipoib force')
		elif ipoib is False:
			if partition == 'Default':
				self.proc.conversation([
					(None, f'no ib partition {partition} ipoib'),
					("Type 'yes' to continue:", 'yes'),
					(self.proc.PROMPTS, None),
				])
			else:
				self.proc.say(f'no ib partition {partition} ipoib')


	def del_partition(self, partition):
		"""
		Remove `partition` from the switch.
		"""
		del_partition_seq = [(None, f'no ib partition {partition}')]
		if partition == 'Default':
			del_partition_seq.append(("Type 'yes' to continue:", 'yes'))
		info('in del partition')
		info(f'{del_partition_seq[0]}')
		self.proc.conversation(del_partition_seq + [(self.proc.PROMPTS, None)])


	def add_partition_member(self, partition, guid, membership='limited'):
		"""
		Add a member to `partition` on the switch, identified by `guid`.
		"""

		# check for a guid or gid
		m = re.fullmatch(guid_format, guid) or re.fullmatch(gid_format, guid)
		if not m:
			raise SwitchException(f'GUID {guid} not valid')

		# either way, get the final 23 characters (all of guid, relevant portion of gid)
		guid = m[0][-23:]

		# too expensive?
		cur_partitions = self.partitions
		if partition not in cur_partitions:
			raise SwitchException(f'Partition {partition} does not exist')

		info(f'ib partition {partition} member {guid} type {membership} force')
		self.proc.say(f'ib partition {partition} member {guid} type {membership} force')


	def del_partition_member(self, partition, guid):
		"""
		Remove a member from `partition` on the switch, identified by `guid`.
		"""
		# check for a guid or gid
		m = re.fullmatch(guid_format, guid) or re.fullmatch(gid_format, guid)
		if not m:
			raise SwitchException(f'GUID {guid} not valid')

		# either way, get the final 23 characters (all of guid, relevant portion of gid)
		guid = m[0][-23:]

		# too expensive?
		cur_partitions = self.partitions
		if partition not in cur_partitions:
			raise SwitchException(f'Partition {partition} does not exist')

		del_member_seq = [(None, f'no ib partition {partition} member {guid}')]
		if partition == 'Default':
			del_member_seq.append(("Type 'yes' to continue:", 'yes'))
		info(f'{del_member_seq[0]}')
		self.proc.conversation(del_member_seq + [(self.proc.PROMPTS, None)])


	def reload(self):
		"""Commands the switch to reboot without confirmation.

		This will close the connection to the switch, so connect() must be called
		again after it reboots to perform any further commands.
		"""
		self.proc.end(quit_cmd = 'reload noconfirm')

	def factory_reset(self):
		"""Comands the switch to perform a factory reset.

		This will clear all configuration and reboot the switch. connect() must be
		called again after it reboots to perform any further commands.
		"""
		self.proc.conversation(
			[
				('', 'reset factory'),
				('reset:', 'YES'),
			]
		)

	def image_boot_next(self):
		"""Commands the switch to toggle which partition to boot from next.

		If the toggle appears to fail, a SwitchException is raised.
		"""
		results = self.proc.ask(cmd = 'image boot next')
		errors = self._get_errors(command_response = results)
		if any(errors):
			raise SwitchException(f'Setting next boot image failed with error {errors}')

	def install_firmware(self, image):
		"""Commands the switch to install the firmware image with the provided name.

		The image must be previously loaded onto the switch with image_fetch().
		If the install appears to fail, a SwitchException is raised.
		"""
		results = self.proc.ask(cmd = f'image install {image}', timeout = 1800)
		# expect a number of success markers equal to the number of steps
		num_steps = 4
		completed_steps = len([result for result in results if '100.0%' in result])
		if completed_steps != num_steps:
			errors = self._get_expected_errors(command_response = results)
			raise SwitchException(
				f'Only {completed_steps} of {num_steps} firmware install steps appear to have completed successfully: {errors}'
			)

	def image_delete(self, image):
		"""Commands the switch to delete the firmware image with the provided name.

		The image must have been previously loaded onto the switch with image_fetch().
		If the deletion appears to fail, a SwitchException is raised.
		"""
		results = self.proc.ask(cmd = f'image delete {image}')
		errors = self._get_errors(command_response = results)
		if any(errors):
			raise SwitchException(f'Image delete failed with error {errors}')


	def image_fetch(self, url):
		"""Commands the switch to fetch a firmware image from the provided URL.

		The URL must begin with one of the supported protocols or a SwitchException is raised.
		If the transfer appears to fail, a SwitchException is raised.
		"""
		# validate the fetch url protocol is one we support
		if not url.startswith(self.SUPPORTED_IMAGE_FETCH_PROTOCOLS):
			raise SwitchException(f'Image fetch URL must be one of the following supported protocols {self.SUPPORTED_IMAGE_FETCH_PROTOCOLS}')

		results = self.proc.ask(cmd = f'image fetch {url}', timeout = 900)
		# check for success indicators and raise an error if not found.
		if not any('100.0%' in result for result in results):
			errors = self._get_expected_errors(command_response = results)
			raise SwitchException(f'Image fetch failed with error {errors}')

	def _get_relevant_responses(self, command_response, start_marker, end_marker):
		"""Given a start and end marker, return a new list of command responses containing all items between start and end.

		If the block of responses to return cannot be reliably found, a SwitchException is raised.
		"""
		# get the start and end indices for the block of responses to extract
		block_indices = [
			index for index, message in enumerate(command_response)
			if re.search(fr'{start_marker}|{end_marker}', message, re.IGNORECASE)
		]
		if len(block_indices) != 2:
			raise SwitchException(f'Ambiguous block. Expected one start and one end marker: {block_indices}')

		start_index, end_index = block_indices

		# ensure we found the start and end markers in the right order (I.E. start_marker before end_marker)
		if (
			not re.search(start_marker, command_response[start_index], re.IGNORECASE)
			or not re.search(end_marker, command_response[end_index], re.IGNORECASE)
		):
			raise SwitchException(
				f'Ambiguous block. Expected start marker matching {start_marker} but got {command_response[start_index].strip()}'
				f' and expected end marker matching {end_marker} but got {command_response[end_index].strip()}.'
			)

		return command_response[start_index + 1:end_index]

	def _get_installed_images(self, command_response):
		"""Extract the currently installed images from the `show images` command response.

		This attempts to identify the block of text where the installed images are listed.
		If no installed images are found within the installed images block, a SwitchException is raised.
		"""
		# narrow search to the relevant responses and parse out the images
		relevant_responses = self._get_relevant_responses(
			command_response = remove_blank_lines(lines = command_response),
			start_marker = 'Installed images',
			end_marker = 'Last boot partition'
		)
		partition_header_regex = r'Partition (?P<partition_number>\d).*$'
		installed_images = {}
		# populate the installed images dictionary
		for index, message in enumerate(relevant_responses):
			partition_header_match = re.search(partition_header_regex, message, re.IGNORECASE)
			if partition_header_match:
				key = int(partition_header_match.group('partition_number'))
				# the image versions are supposed to be the line after the partition headers.
				try:
					value = re.sub(r'\s*version\s*:', '', relevant_responses[index + 1], re.IGNORECASE).strip()
				except IndexError:
					raise SwitchException(f'No installed image listed for partition {key} when one was expected.')

				# If it looks like a header, don't use it as an image name.
				if re.search(partition_header_regex, value, re.IGNORECASE):
					raise SwitchException(
						f'No installed image listed for partition {key}, found what looked like a partition header instead: {value}'
					)

				installed_images[key] = value

		if not installed_images:
			raise SwitchException('No installed images found in the show images response.')

		return installed_images

	def _get_boot_partitions(self, command_response):
		"""Get the last and next boot partitions out of the provided command_response.

		If multiple boot partitions for either partition are found, a SwitchError is raised.
		If a boot partition cannot be found in the command_response, a SwitchError is raised.
		"""
		# get the next and last boot partitions
		last_partition = 'Last'.casefold()
		next_partition = 'Next'.casefold()
		boot_partitions = {}
		for response in remove_blank_lines(lines = command_response):
			match = re.search(
				fr'(?P<partition_name>{last_partition}|{next_partition}) boot partition: (?P<partition_number>\d)',
				response,
				re.IGNORECASE
			)
			if match:
				partition_name = match.group('partition_name').casefold()
				if partition_name in boot_partitions:
					raise SwitchException(f"Ambiguous boot partitions. Got multiple entries for boot partition {match.group('partition_name')}")

				boot_partitions[partition_name] = int(match.group('partition_number'))

		try:
			result = boot_partitions[last_partition], boot_partitions[next_partition]
		except KeyError as exception:
			raise SwitchException(f'No boot partition entry for {exception}')

		return result

	def _get_available_images(self, command_response):
		"""Get the image files that are available for installation out of the provided command_response.

		This returns a list of available images, with each list entry being a named tuple with the following members:
			filename - the image file name
			version - the image version

		This attempts to identify the block of text where the available images are listed.
		If that block cannot be reliably found, a SwitchException is raised.
		If no available images are found within the installed images block, an empty list is returned.
		"""
		# narrow search to the relevant responses and parse out the images
		# the available images listed inside the text block should take the form:
		#	'image_filename_1'
		#	'image_version_1'
		#	'image_filename_2'
		#	'image_version_2'
		# an empty available images block is acceptable
		AvailableImage = namedtuple('AvailableImage', ['filename', 'version'])
		available_images = []
		relevant_responses = self._get_relevant_responses(
			command_response = remove_blank_lines(lines = command_response),
			start_marker = r'next boot partition:',
			end_marker = 'Serve image files via'
		)
		# Firmware version 3.6.8010 changed the format to be:
		#	1:
		#		Image  : image_filename_1
		#		Version: image_version_1
		#	2:
		#		Image  : image_filename_2
		#		Version: image_version_2
		# and to always contain the 'Images available to be installed:' header even when
		# no images are available. So we drop the images header and the message that
		# images aren't available and drop the lines enumerating the image numbers if present.
		relevant_responses = [
			response for response in relevant_responses
			if not re.search(r'image.*available to be installed', response, re.IGNORECASE)
			and not re.search(r'\s*\d+:\s*$', response, re.IGNORECASE)
		]
		for index, message in enumerate(relevant_responses):
			# skip each odd index since it will be the "value" of the pair we are extracting
			if index % 2:
				continue
			# add an available image to the list
			try:
				filename = re.sub(r'\s*Image\s*:', '', message, flags = re.IGNORECASE).strip()
				version = re.sub(r'\s*Version\s*:', '', relevant_responses[index + 1], flags = re.IGNORECASE).strip()
				available_images.append(
					AvailableImage(
						filename = filename,
						version = version
					)
				)
			except IndexError:
				raise SwitchException(f'Missing version number for image file {message.strip()}')

		return available_images

	def show_images(self):
		"""Gets the listing of installed images, images available to be installed, and the last and next boot partition.

		Returns a namedtuple with the following members:
			installed_images - A dictionary of installed image versioned keyed by partition number
			last_boot_partition - The partition number that was last booted from
			next_boot_partition - The partition number that will be booted from next
			images_fetched_and_available - A list of images available for installation.
				This list is made up of named tuples, each with a filename and version member.

		Should an error occur during the parsing of the show images command output, a SwitchException is raised.
		"""
		images_text = self.proc.ask(cmd = 'show images')
		last_boot_partition, next_boot_partition = self._get_boot_partitions(command_response = images_text)
		ImagesListing = namedtuple(
			'ImagesListing',
			['installed_images', 'last_boot_partition', 'next_boot_partition', 'images_fetched_and_available',]
		)
		return ImagesListing(
			installed_images = self._get_installed_images(command_response = images_text),
			last_boot_partition = last_boot_partition,
			next_boot_partition = next_boot_partition,
			images_fetched_and_available = self._get_available_images(command_response = images_text),
		)

	def _get_errors(self, command_response):
		"""Looks for lines that start with a '%' character and returns a list of them.

		Error messages appear to start with a % character.
		"""
		return [error_string for error_string in command_response if error_string.startswith('%')]

	def _get_expected_errors(self, command_response):
		"""Looks for errors in the command_response and returns a list of errors found.

		However, if no errors are found 'unknown error' is returned instead.
		"""
		errors = self._get_errors(command_response = command_response)
		return errors if errors else 'unknown error'

	def disable_fallback_reboot(self):
		"""Command the switch to disable fallback reboot for the next reboot."""
		results = self.proc.ask(cmd = 'no boot next fallback-reboot enable')
		errors = self._get_errors(command_response = results)
		if any(errors):
			raise SwitchException(f'Disabling fallback reboot failed with error: {errors}')

	def write_configuration(self):
		"""Command the switch to write it's current configuration to non-volatile storage."""
		results = self.proc.ask(cmd = 'configuration write')
		errors = self._get_errors(command_response = results)
		if any(errors):
			raise SwitchException(f'Writing configuration failed with error: {errors}')
