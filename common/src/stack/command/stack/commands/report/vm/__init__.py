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
from jinja2 import Environment, meta
from pathlib import Path
import secrets

from stack.kvm import Hypervisor
from stack.exception import CommandError, ParamError
from stack.argument_processors.host import HostArgProcessor
from stack.argument_processors.vm import VmArgProcessor
from stack.util import _exec

class command(HostArgProcessor, stack.commands.report.command):
        pass

class Command(command, VmArgProcessor):
	"""
	Output a libvirt virtual machine config based on
	information stored in Stacki for a given host

	<arg type='string' name='host' repeat='1' optional='1'>
	The host or hosts to generate config files for
	</arg>

	<param type='string' name='hypervisor'>
	Output libvirt configs for virtual machines on a specified hypervisor
	</param>

	<param type='bool' name='bare'>
	Output the config file in non-SUX format for feeding
	directly to the hypervisor.
	</param>

	<example cmd='report vm virtual-backend-0-1'>
	Output the libvirt config of virtual-backend-0-1
    </example>

	<example cmd='report vm virtual-backend-0-1 bare=y'>
	Output the libvirt config of virtual-backend-0-1 without SUX
    </example>

	<example cmd='report vm hypervisor=hypervisor-0-1'>
	Get the libvirt config for all hosts on hypervisor-0-1
    </example>
	"""

	def run(self, param, args):
		self.beginOutput()
		vm_hosts = self.valid_vm_args(args)
		conf_loc = Hypervisor.conf_loc
		default_template = '/opt/stack/share/templates/libvirt.conf.j2'
		req_vars = {'memory', 'cpucount', 'uuid', 'os', 'name'}
		out = []

		bare_output, hypervisor = self.fillParams([
			('bare', False),
			('hypervisor', ''),
		])

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
			raise ParamError(self, 'hypervisor', f'{hypervisor} is not a valid hypervisor')

		for vm in vm_hosts:
			self.bootorder = 1
			curr_hypervisor = self.get_hypervisor_by_name(vm)
			loc = conf_loc
			template_loc = self.getHostAttr(vm, 'vm_config_location')

			# Use the default template in /opt/stack/share/templates
			# if the template attribute isn't set
			if not template_loc:
				template_loc = default_template

			template_conf = Path(template_loc)
			env = Environment()

			# Check if the template exists
			# and has the required variables
			if template_conf.is_file():
				ast = env.parse(template_conf.read_text())
				var_list = meta.find_undeclared_variables(ast)
			else:
				raise CommandError(self, f'Unable to find template file: {template_conf}')

			if req_vars.issubset(var_list):
				libvirt_template = jinja2.Template(template_conf.read_text(), lstrip_blocks=True, trim_blocks=True)
			else:
				raise CommandError(self, f'Missing required template variables for libvirt config file: {template_conf}')

			# If the hypervisor param is set
			# ignore any VM not belonging to the
			# specified hypervisor host
			if hypervisor and curr_hypervisor != hypervisor:
				continue

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
			template_vars['os'] = self.getHostAttr(curr_hypervisor, 'os')

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
		Generate a random mac address for virtual machine interfaces
		"""

		# Generate 6 random hex chars
		mac = secrets.token_hex(3)

		# Assign every 2 hex digits to the new mac address
		# The first 6 digits are the VirtIO mac manufacturer address
		return f'52:54:00:{mac[0:2]}:{mac[2:4]}:{mac[4:6]}'

	def getInterfaceByNetwork(self, host, network):
		"""
		Return the first network interface for a host on a specified network
		"""

		for interface in self.call('list.host.interface', [host]):
			if interface['network'] == network:
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
		kickstartable = self.str2bool(self.getHostAttr(host, 'kickstartable'))
		interfaces = []

		for interface in self.call('list.host.interface', [host]):
			interface_name = interface['interface']
			host_interface = None
			network_pxe = False
			network = interface['network']
			channel = interface['channel']
			out = {}

			# Skip any vlan tagged or virtual interfaces
			# interfaces containing . are considered vlan tagged
			# interfaces containing : are considered virtual interfaces
			if '.' in interface_name or ':' in interface_name:
				continue

			if network:

				# Check if the hypervisor has a interface on the same network
				# as the virtual machine
				host_interface = self.getInterfaceByNetwork(vm_host, network)

				# If the network isn't set for pxe, don't use it for the bootorder
				network_pxe = self.str2bool(self.call('list.network', args = [network])[0].get('pxe'))

			# If no network is set for the source interface
			# use the channel setting for a default one
			# if it is a valid interface on the hypervisor
			elif channel:
				for interface in self.call('list.host.interface', [vm_host]):
					if interface['interface'] == channel:
						host_interface = channel

			# Otherwise raise an error as libvirt requires
			# a source interface when defining the VM's interfaces
			if not host_interface:
				raise CommandError(self, f'On VM {host} could not find interface for network {network} on hypervisor {vm_host}')

			out['mac'] = interface['mac']
			out['name'] = host_interface

			# Only set the bootorder for the interface  if the network
			# is set to pxe and that the kickstartable attr is true for the host
			if network_pxe and kickstartable:
				out['bootorder'] = self.bootorder
				self.bootorder+=1

			# If no mac address is assigned to a VM's
			# interface, generate one and assign it
			if not out.get('mac'):
				mac_addr = self.getMAC()
				out['mac'] = mac_addr
				self.command('set.host.interface.mac', [host, f'interface={interface_name}', f'mac={mac_addr}'])

			interfaces.append(out)
		return interfaces
