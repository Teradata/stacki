# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#

import stack.commands
import random
import uuid
import jinja2
from pathlib import Path
from stack.exception import CommandError, ParamError
from stack.argument_processors.vm import VmArgumentProcessor
from stack.util import _exec

class command(stack.commands.HostArgumentProcessor,
              stack.commands.report.command):
        pass

class Command(command, VmArgumentProcessor):
	"""
	Output a libvirt virtual machine config based on
	information stored in Stacki for a given host

	<arg type='string' name='host' repeat='1' optional='1'>
	The host/mutliple hosts to output a config of
	</arg>

	<param type='bool' name='bare'>
	Output the config file in non-SUX format for feeding
	directly to the hypervisor.
	</param>
	"""

	def run(self, param, args):
		self.beginOutput()
		vm_hosts = self.valid_vm_args(args)
		conf_loc = '/etc/libvirt/qemu/'
		out = []

		bare_output, hypervisor = self.fillParams([
			('bare', False),
			('hypervisor', '')
		])

		template_conf = Path('/opt/stack/share/templates/libvirt.conf.j2')
		if template_conf.is_file():
			libvirt_template = jinja2.Template(template_conf.read_text(), lstrip_blocks=True, trim_blocks=True)
		else:
			raise CommandError(self, f'Unable to parse template file: {template_conf}')

		# Strip the SUX tags if set to true
		bare_output = self.str2bool(bare_output)
		vm_info =  {vm['virtual machine']: vm for vm in self.call('list.vm', vm_hosts)}
		vm_disks = {}
		for disk in self.call('list.vm.storage', vm_hosts):
			host = disk['Virtual Machine']
			disk.pop('Virtual Machine')
			vm_disks.setdefault(host, []).append(disk)

		# Check if the hypervisor is valid
		# if the param is set
		if hypervisor and not self.is_hypervisor(hypervisor):
			raise ParamError(self, 'hypervisor', '{hypervisor} is not a valid hypervisor')

		for vm in vm_hosts:
			self.bootorder = 1
			curr_hypervisor = self.get_hypervisor_by_name(vm)
			loc = conf_loc

			# If the hypervisor param is set
			# ignore any VM not belonging to the
			# specified hypervisor host
			if hypervisor and curr_hypervisor != hypervisor:
				continue

			conf_loc_attr = self.getHostAttr(curr_hypervisor, 'vm.config.location')

			if conf_loc_attr:
				loc = conf_loc_attr

			# Handle if no disks are defined for a
			# virtual machine
			if vm not in vm_disks:
				curr_disks = []
			else:
				curr_disks = vm_disks[vm]

			template_vars = {}
			vm_values = vm_info[vm]

			# Assign libvirt template values
			template_vars['name'] = vm
			template_vars['memory'] = int(vm_values['memory']) * 1024
			template_vars['cpucount'] = vm_values['cpu']
			template_vars['uuid'] = uuid.uuid4()

			# Get template info that varies between VM's
			template_vars['interfaces'] = self.gen_interfaces(vm)
			template_vars['disks'] = self.gen_disks(vm, curr_disks)

			vm_config = libvirt_template.render(template_vars)
			if not bare_output:
				config_file = Path(f'{loc}/{vm}.xml')

				# Output SUX
				if len(vm_hosts) > 1:
					self.addOutput(vm, f'<stack:file stack:name={config_file}>')
				else:
					self.addOutput('', f'<stack:file stack:name={config_file}>')
				self.addOutput('', vm_config)
				self.addOutput('', '</stack:file>')
			else:
				self.addOutput(vm, vm_config)
		self.endOutput(padChar='', trimOwner=True)

	def getMAC(self):
		"""
		Generate a random mac address for
		virtual machine interfaces
		"""

		r = random.SystemRandom()
		m = "%06x" % r.getrandbits(24)

		return "52:54:00:%s:%s:%s" % (m[0:2], m[2:4], m[4:6])

	def getInterfaceByNetwork(self, host, network):
		"""
		Return the first network interface for a host on a specified network
		"""

		for interface in self.call('list.host.interface', [host]):
			if interface['network'] == network and network != None:
				return interface['interface']

	def gen_disks(self, host, disks):
		"""
		Generate the storage portion of the libvirt xml
		"""

		disk_output = []
		diskid = 0
		disks = sorted(disks, key=lambda d: d['Name'])
		for disk in disks:
			disk_delete = self.str2bool(disk['Pending Deletion'])
			out = {}
			if not disk['Name'] or disk_delete:
				continue
			pool = Path(disk['Location'])

			# Sata is needed for new volumes due to
			# default partition scheme expecting sda
			bus_type = 'sata'
			src_path = ''
			dev_type = 'file'
			src_type = 'file'
			devname = disk['Name']

			# Handle premade qcow or raw images
			if disk['Type'] == 'image':
				vol = Path(disk['Image Name'])
				frmt_type = vol.suffix.replace('.', '')
				bus_type = 'virtio'
				src_path = Path(f'{pool}/{vol.name}')

			# Handle block devices
			elif disk['Type'] == 'mountpoint':
				vol = disk['Mountpoint']
				frmt_type = 'raw'
				dev_type = 'block'
				src_type = 'dev'
				src_path = Path(vol)

			# Specify new volumes
			elif disk['Type'] == 'disk':

				# Change the bus type if the devname
				# is vdX to virtio
				if 'vd' in devname:
					bus_type = 'virtio'
				vol_name = disk['Image Name']
				frmt_type = 'qcow2'
				diskid += 1
				src_path = Path(f'{pool}/{vol_name}')

			out = {
					'dev':dev_type,
					'type': frmt_type,
					'src_type': src_type,
					'path': f'{src_path}',
					'name': devname,
					'bus' : bus_type,
					'bootorder': self.bootorder
			}
			disk_output.append(out)
			self.bootorder += 1

		return disk_output

	def gen_interfaces(self, host):
		"""
		Generate the network interface portion
		for a libvirt config
		"""

		vm_host = self.get_hypervisor_by_name(host)
		interfaces = []

		for interface in self.call('list.host.interface', [host]):
			interface_name = interface['interface']
			network = interface['network']
			out = {}

			# Check if the hypervisor has a interface on the same network
			# as the virtual machine
			host_interface = self.getInterfaceByNetwork(vm_host, network)

			# Skip ipmi and interfaces that the underlying hypervisor
			# has no interface for on that network
			if interface_name == 'ipmi' or not host_interface:
				continue
			if network:

				# If the network isn't set for pxe, don't use it for the bootorder
				network_pxe = self.str2bool(self.call('list.network', args = [network])[0].get('pxe'))
			out['mac'] = interface['mac']
			out['name'] = host_interface

			if network_pxe:
				out['bootorder'] = self.bootorder
				self.bootorder+=1

			# If no mac address is assigned to a VM's
			# interface, generate one
			if not out.get('mac'):
				mac_addr = self.getMAC()
				out['mac'] = mac_addr
				self.command('set.host.interface.mac', [host, f'interface={interface_name}', f'mac={mac_addr}'])

			interfaces.append(out)
		return interfaces
