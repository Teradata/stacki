# @SI_Copyright@
# @SI_Copyright@
# @SI_Copyright@
import pyipmi
from pyipmi.bmc import LanBMC
from pyipmi import make_bmc
import stack.api
import stack.commands
from stack.exception import *

class command(stack.commands.set.host.command):
	MustBeRoot = 0


class Command(command):
	"""
	Set boot order for a host without having to go through the BIOS
	settings manually.
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='action'>
	Should be one of the below:
	none : Do not change boot device order
	pxe   : Force PXE boot
	disk  : Force boot from default Hard-drive
	safe  : Force boot from default Hard-drive, request Safe Mode
	diag  : Force boot from Diagnostic Partition
	cdrom : Force boot from CD/DVD
	bios  : Force boot into BIOS Setup
	floppy: Force boot from Floppy/primary removable media
	</param>
		
	<example cmd='set host boot order compute-0-0 action=pxe'>
	Set compute-0-0 to pxe boot first.
	</example>
	"""
	def run(self, params, args):
		(action, ) = self.fillParams([
			('action', ),
			])
		
		if not len(args):
			raise ArgRequired(self, 'host')
		host = args[0]

		if action not in [ 'none', 'pxe', 'disk', 'safe', 
			'diag', 'cdrom', 'bios', 'floppy' ]:
			raise ParamError(self, 'action', 'must be one of' \
				'"none", "pxe", "safe", "disk","diag", '  \
				'"cdrom", "bios" or "floppy"')
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

		bmc = make_bmc(LanBMC,
			hostname=ipmi_ip,
			username=uname,
			password=pwd)

		# Set bootdev via IPMI interface
		bmc.set_bootdev(action)
