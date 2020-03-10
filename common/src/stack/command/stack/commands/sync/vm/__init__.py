import stack.kvm
from pathlib import Path
from stack.argument_processors.vm import VmArgumentProcessor
from stack.kvm import VmException
from stack.exception import CommandError, ParamError
from stack.util import _exec

class command(stack.commands.HostArgumentProcessor,
	stack.commands.sync.command):
	pass

class Command(command, VmArgumentProcessor):
	"""
	Sync virtual machines to their hypervisor host.
	Until this command is run, no virtual machines
	will be defined or modified in configuration
	on the actual hypervisor.

	<arg type='string' name='host'>
	One or more virtual machine hosts to sync.
	</arg>

	<param type='string' name='debug'>
	Display additional debugging information when syncing the
	virtual machines. Defaults to false if not set.
	</param>

	<param type='bool' name='force'>
	By default, sync vm will not sync virtual machines currently turned on.
	Force will hard power off the VM and proceed with syncing it.
	</param>

	<param type='string' name='hypervisor'>
	Sync Virtual Machines only on a particular hypervisor.
	</param>

	<param type='bool' name='autostart'>
	By default, sync vm will not turn on a VM,
	when autostart is set, all VM's affected by the sync command
	will be turned on
	</param>

	<param type='bool' name='sync_ssh'>
	Defaults to true, packs in the frontend's ssh key
	into image based storage (such as qcow2 or raw files).
	</param>

	<example cmd='sync vm virtual-machine-0-1'>
	Define a virtual machine virtual-machine-0-1 on it's assigned hypervisor
	</example>

	<example cmd='sync vm virtual-machine-0-1 sync_ssh=n autostart=y'>
	Sync a virtual machine but don't pack in the frontend's ssh key
	(assuming it has a premade qcow2 or raw image as its storage)
	and start if after syncing
	</example>
	"""

	def run(self, params, args):
		debug, hypervisor, force, autostart, sync_ssh = self.fillParams([
			('debug', False),
			('hypervisor', ''),
			('force', False),
			('autostart', False),
			('sync_ssh', True),
		])

		force = self.str2bool(force)
		debug = self.str2bool(debug)
		sync_ssh = self.str2bool(sync_ssh)
		autostart = self.str2bool(autostart)
		vm_hosts = {}
		vm_disks = {}

		# Gather the required info for each vm
		# If the force parameter isn't set, skip
		# vm's currently on
		for vm in self.call('list.vm', [*args, 'expanded=True', f'hypervisor={hypervisor}']):
			vm_name = vm['virtual machine']
			if vm['status'] != 'on':
				vm_hosts[vm_name] = vm
			elif force:
				self.notify(f'Force turning off {vm_name}')
				self.call('set.host.power', args = [vm_name, 'command=off', 'method=kvm'])
				vm['status'] = 'off'
				vm_hosts[vm_name] = vm
			elif debug:
				self.notify(f'VM host {vm_name} is on, skipping')

		# Gather each host's disk information
		for disk in self.call('list.vm.storage', list(vm_hosts)):
			vm_disks.setdefault(disk['Virtual Machine'], []).append(disk)

		# If there is no VM's to sync we are done
		if not vm_hosts:
			return
		self.notify('Sync Virtual Machines')
		self.beginOutput()
		plugin_args = (vm_hosts, vm_disks, debug, sync_ssh, force, autostart)

		# Gather plugin info and output any errors found
		# if the debug flag is set
		for (provides, plugin_errors) in self.runPlugins(plugin_args):
			if plugin_errors and debug:
				self.addOutput('', '\n'.join(plugin_errors))
		self.endOutput(header = [], trimOwner = False)
