# @SI_Copyright@
# @SI_Copyright@
import os
from pyipmi.bmc import LanBMC
from pyipmi import make_bmc
import stack.api
import stack.commands
from stack.exception import *

class Command(stack.commands.Command):
	"""
	Update firmware on machine remotely.
	Currently works only for Dell Servers.
	<arg type='string' name='host' repeat='1'>
	One or more host names.
	</arg>

	<param type='string' name='name' optional='0'>
	Name of the update file.
	</param>
	<example cmd='update host firmware compute-0-0 name=ESM.bin'>
	Update iDRAC firmware on compute-0-0 to ESM.bin.
	</example>
	"""
	MustBeRoot = 0
	DELL = "dell"

	def run(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'host')
		host = args[0]
		(name,) = self.fillParams([('name', None)])
		if not name:
			raise ParamRequired(self, 'name')

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
			self.abort('ipmi password not found in the database')
		pwd = r[0]['value']

		# Get IP addr of tftp server
		r = stack.api.Call("list.attr", 
			["attr=Kickstart_PrivateNetwork"])
		if not r:
			raise CommandError(self, 'Kickstart_PrivateNetwork ' \
				'not found in database')
		tftp_ip = r[0]['value']

		# Get Manufacturer information
		bmc = make_bmc(LanBMC, 
			hostname=ipmi_ip, 
			username=uname, 
			password=pwd)
		bmc_info = bmc.info()
		
		# Run implementation specific code
		if Command.DELL in bmc_info.manufacturer_name.lower():
			path = '/tftpboot/' + name
			if not os.path.isfile(path):
				raise CommandError(self, 'Update file %s should '
					'be present in /tftpboot/' % path)
			self.runImplementation('%s' % Command.DELL,
				(host, ipmi_ip, uname, pwd, path, tftp_ip))
