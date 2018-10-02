import re
import syslog
import time

from stack.expectmore import ExpectMore, remove_control_characters
from stack.bool import str2bool
from . import Switch, SwitchException
from . import mellanoknok

def info(message):
	syslog.syslog(syslog.LOG_INFO, f'm7800.py: {message}')


partition_name = re.compile('  [a-z0-9]', re.IGNORECASE)
members_header = re.compile('  members', re.IGNORECASE)
# a GUID is a like a MAC, but 8 pairs
guid_format = re.compile("([0-9a-f]{2}:){7}[0-9a-f]{2}|ALL", re.IGNORECASE)
# a GID is like an ipv6? 20 pairs
gid_format = re.compile("([0-9a-f]{2}:){19}[0-9a-f]{2}|ALL", re.IGNORECASE)
guid_member_format = re.compile("([0-9a-f]{2}:){7}[0-9a-f]{2}.*(full|both|limited)|ALL", re.IGNORECASE)


class SwitchMellanoxM7800(Switch):
	"""
	Class for interfacing with a Mellanox 7800 Infiniband Switch.
	"""

	def supported(*cls):
		return [
			('Mellanox', 'm7800'),
		]

	def __init__(self, switch_ip_address, switchname='switch', username='admin', password=''):
		# Grab the user supplied info, in case there is a difference (PATCH)
		self.switch_ip_address = switch_ip_address
		self.username = username
		self.password = password

		self.stacki_server_ip = None
		self.switchname = switchname
		self.proc = ExpectMore()
		self.proc.PROMPTS = (['.config. #', ' >', ' #'])


	def connect(self):
		"""
		Connect to the switch and get a configuration prompt
		"""
		if self.proc.isalive():
			return

		ssh_options = '-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -tt'
		self.proc.start(f'ssh {ssh_options} {self.username}@{self.switch_ip_address}')
		info(f'ssh {ssh_options} {self.username}@{self.switch_ip_address}')

		self.proc.wait(['Password:', ' >'])

		if self.proc.match_index == 0:
			info('password-based auth')
			# password-based auth
			self.proc.say(self.password)
		# otherwise, key-based auth is already setup

		login_seq = [
			([' >', ''], 'terminal length 999'),
			(' >', 'enable'),
			(' #', 'configure terminal'),
			('.config. #', ''),
		]

		self.proc.conversation(login_seq)

		self._api_connection = mellanoknok.Mellanoknok(self.switch_ip_address, password=self.password)


	def disconnect(self):
		if self.proc.isalive():
			self.proc.end('quit')


	@property
	def subnet_manager(self):
		""" get the subnet manager status for this switch """
		for line in self.proc.ask('show ib sm'):
			if 'enable' == line.strip():
				return True
		return False


	@subnet_manager.setter
	def subnet_manager(self, value):
		""" set the subnet manager status for this switch """
		cmd = 'ib sm'
		if value:
			self.proc.say(cmd)
		else:
			self.proc.say('no ' + cmd)


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
		time.sleep(.5)
		self.proc.say(f'hostname {hostname}')

		for host in self._get_smnodes():
			if host != hostname:
				self.proc.say(f'no ib smnode {host}')

		self.subnet_manager = True
		time.sleep(.5)


	def _get_smnodes(self):
		nodes = self.proc.ask('no ib smnode ?', sanitizer=expectmore.remove_control_characters(l.strip()))
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
		for line in self.proc.ask('show ib partition'):
			if re.match(members_header, line):
				# drop the 'members' line, because it can look like partition names
				# lord help us if someone names their partition 'members'
				continue
			if re.match(partition_name, line):
				cur_partition = line.strip()
				partitions[cur_partition] = {
					'pkey': '',
					'ipoib': False,
					'guids': [],
				}
				continue

			line = line.strip()
			if line.startswith('PKey'):
				_, key = line.split('=')
				partitions[cur_partition]['pkey'] = int(key, 16)
			elif line.startswith('ipoib'):
				_, ipoib = line.split('=')
				partitions[cur_partition]['ipoib'] = str2bool(ipoib.strip())
			elif line.startswith('GUID'):
				m = re.search(guid_member_format, line)
				partitions[cur_partition]['guids'].append((m.group(0), m.group(2)))

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


	def add_partition(self, partition='Default', pkey=None):
		"""
		Add `partition` to the switch, with partition key `pkey` which must be between 2-32766.
		`partition` 'Default' has a hard-coded pkey.
		"""
		info(f'adding partition {partition}')
		if partition != 'Default':
			if not pkey:
				raise SwitchException(f'a partition key is required for partition: {partition}.')
			pkey = self._validate_pkey(pkey)
			if not pkey:
				raise SwitchException('InfiniBand partition keys must be between 2 and 32766')

		if str(partition) == 'Default':
			add_part_seq = [
				(None, 'no ib partition Default'),
				("Type 'yes' to continue:", 'yes'),
				(self.proc.PROMPTS, 'ib partition Default pkey 0x7fff force'),
				(self.proc.PROMPTS, 'ib partition Default defmember limited force'),
				(self.proc.PROMPTS, 'ib partition Default ipoib force'),
				(self.proc.PROMPTS, None),
			]
			self.proc.conversation(add_part_seq)
		else:
			self.proc.say(f'ib partition {partition} pkey {pkey} force')


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
		self.proc.end('reload noconfirm')


	def image_boot_next(self):
		self.proc.say('image boot next')


	def install_firmware(self, image):
		self.proc.ask(f'image install {image}', timeout=1800)


	def image_delete(self, image):
		self.proc.say(f'image delete {image}')


	def image_fetch(self, url):
		self.proc.ask(f'image fetch {url}', timeout=900)


	def show_images(self):
		images_text = self.proc.ask('show images')
		data = {}
		data['installed_images'] = []
		data['last_boot_partition'] = None
		data['next_boot_partition'] = None
		data['images_fetched_and_available'] = []

		extraction1 = False
		extraction2 = False
		i = 0
		while i < len(images_text):
			line = images_text[i]
			if len(line) == 0 or len(line) == 1:
				i = i + 1
				continue
			if('Installed images' in line):
				extraction1 = True
				i = i + 1
				continue
			if('Last boot partition' in line):
				extraction1 = False
				data['last_boot_partition'] = int(line.split(':')[-1])
				data['next_boot_partition'] = int(images_text[i+1].split(':')[-1])
				i = i + 1
				continue
			if('available to be installed' in line):
				if('No image files are available to be installed' in line):
					i = i + 1
					continue
				extraction2 = True
				i = i + 1
				continue
			if('Serve image files via HTTP/HTTPS' in line):
				extraction2 = False
				break

			if(extraction1):
				partition = line.strip(': ')
				image = images_text[i+1].strip()
				d = {}
				d[partition] = image
				data['installed_images'].append(d)
				i = i + 1
			if(extraction2):
				data['images_fetched_and_available'].append(images_text[i].strip())
				i = i + 1
			i = i + 1
		return data

