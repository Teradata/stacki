# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt # @copyright@
# @copyright@
#
import stack.commands
from stack.exception import ArgRequired, CommandError
from stack.argument_processors.vm import VmArgumentProcessor

class command(stack.commands.HostArgumentProcessor,
		stack.commands.remove.command):
	pass

class Command(command, VmArgumentProcessor):
	"""
	Mark a vm for removal from the database and hypervisor.
	Upon running the sync vm command, nodes set to pending deletion will
	be removed on the hypervisor.

	<arg type='string' name='host' repeat='1' optional='1'>
	List of hosts to remove from the database.
	</arg>

	<param type='bool' name='nukedisks'>
	Mark all of a VM's storage for removal as well.
	</param>

	<param type='bool' name='force'>
	Override the default behavior of not allowing removal of
	currently running virtual machines.
	</param>

	<example cmd='remove vm virtual-backend-0-0'>
	Marks virtual-backend-0-0 for deletion upon sync vm.
	</example>

	<example cmd='remove vm virtual-backend-0-1 nukedisks=y'>
	Mark virtual-backend-0-1 for deletion along with all
	its storage.
	</example>
	"""

	def run(self, params, args):
		if len(args) < 1:
			raise ArgRequired(self, 'host')

		nukedisks, force  = self.fillParams([
			('nukedisks', False),
			('force', False)
		])

		list_args = [*args, 'expanded=y']
		force = self.str2bool(force)
		nukedisks = self.str2bool(nukedisks)
		hosts = self.call('list.vm', list_args)
		disks = self.call('list.vm.storage', args)
		host_id = {}

		for host in hosts:
			vm_id = self.vm_id_by_name(host['virtual machine'])
			if (host['status'] != 'on') or force:
				host_id[host['virtual machine']] = vm_id

		if len(host_id) != len(hosts) and not force:
			self.notify('Skipping virtual machines that are on')

		# Don't remove the frontend if it's defined as a virtual machine
		me = self.db.getHostname()
		if me in host_id:
			raise CommandError(self, 'cannot remove "%s"' % me)
		self.runPlugins((host_id, disks, nukedisks))
