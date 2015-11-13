# @SI_Copyright@
# @SI_Copyright@
# @SI_Copyright@
from pyipmi.bmc import LanBMC
from pyipmi import make_bmc
import stack.api
import stack.commands
from stack.exception import *

class Command(stack.commands.Command):
	"""
	Boot Once from virtual media or any other device.
	Currently works only for Dell Servers.
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='action' optional='0'>
	disk  : Force boot from default Hard-drive
	safe  : Force boot from default Hard-drive, request Safe Mode
	diag  : Force boot from Diagnostic Partition
	cdrom : Force boot from CD/DVD
	pxe   : Force pxe boot
	bios  : Force boot into BIOS Setup
	floppy: Force boot from Floppy/primary removable media	
	vmedia: Force boot from virtual media image
	</param>
	<example cmd='set host bootonce compute-0-0 action=vmedia'>
	Boot once from selected device compute-0-0 remotely.
	</example>
	"""
	MustBeRoot = 0
	DELL = "dell"

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'host')
		host = args[0]
		
		(action,) = self.fillParams([('action', None)])
		action_arr = ['pxe', 'disk', 'safe', 'diag', 'cdrom', 
			'bios', 'floppy', 'vmedia']
		if action not in action_arr:
			raise ParamError(self, 'action', 'needs to be one of ' \
				'pxe, disk, safe, diag, cdrom, bios, floppy, ' \
				' vmedia')
		# Get ipmi interface from db for this host
		output = self.call('list.host.interface', [ host ])
		ipmi_ip = None
		for o in output:
			if o['interface'] == 'ipmi':
				ipmi_ip = o['ip']
		if not ipmi_ip:
			raise CommandError(self, 'No ipmi interface found for ' \
				'host ' + host)

		# Get the ipmi uname, pwd
		r = stack.api.Call("list.host.attr", 
			[host,"attr=ipmi_uname"])
		if not r:
			raise CommandError(self, 'ipmi uname not found in' \
				' the database')
		uname = r[0]['value']

		r = stack.api.Call("list.host.attr",
			[host,"attr=ipmi_pwd"])
		if not r:
			raise CommandError(self, 'ipmi password not found ' \
				'in the database')
		pwd = r[0]['value']

		# Get Manufacturer information
		bmc = make_bmc(LanBMC, 
			hostname=ipmi_ip, 
			username=uname, 
			password=pwd)
		bmc_info = bmc.info()
		
		# Run implementation specific code
		if Command.DELL in bmc_info.manufacturer_name.lower():
			self.runImplementation('%s' % Command.DELL,
				(host, ipmi_ip, uname, pwd, action))
