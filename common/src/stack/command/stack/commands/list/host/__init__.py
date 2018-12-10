# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands
from stack.opt import opt

class command(stack.commands.HostArgumentProcessor,
	stack.commands.list.command):
	pass
	

@opt.desc("""
Lists the following information for one or more hosts:

- host : hostname
- rack : cabinet name
- rank : ID within cabinent
- appliance : name of appliance (e.g. *backend*)
- os : operating system (e.g. *sles*)
- box : package and configuration repository
- environment : optional extra attribute level
- osaction : bootaction to boot from local disk
- installaction : bootaction start os installer
- status : current status (e.g. *up*)
- comment : optional comment
- hash : see `hash` option
""")
@opt.arg('host', required=False, description="""
Zero or more host names. If no hostnames are supplied, information about all 
known hosts is listed.
""")
@opt.param('hash', default=False, type=bool, description="""
If true then output *synced* or *outdated* which indicates if the host is in 
sync with the box for the host (pallets and carts) and if the current 
installation file (profile) is the same as the installation file that was used
when the host was last installed.
""")
class Command(command):

	@opt.parse
	def run(self, params, args):

		hosts = self.getHostnames(args)
		self.hashit = params['hash']
	    
		header = [ 'host' ]
		values = { }
		for host in hosts:
			values[host] = [ ]
			
		for (provides, result) in self.runPlugins((hosts, expanded, hashit)):
			header.extend(result['keys'])
			for h, v in result['values'].items():
				values[h].extend(v)

		self.beginOutput()
		for host in hosts:
			self.addOutput(host, values[host])
		self.endOutput(header=header, trimOwner=False)

