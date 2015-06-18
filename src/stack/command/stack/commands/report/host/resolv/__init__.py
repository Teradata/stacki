# @SI_Copyright@
# @SI_Copyright@

import sys
import socket
import string
import stack.commands

class Command(stack.commands.report.host.command):
        """
        Generate the /etc/resolv.conf for a host

	<arg optional='0' repeat='1' type='string' name='host'>
	Host name of machine
	</arg>
	"""

	def run(self, params, args):

		self.beginOutput()

                zones = {}
                for row in self.call('list.network'):
                        zones[row['network']] = row['zone']
                        
		for host in self.getHostnames(args):

                        self.addOutput(host,'<file name="/etc/resolv.conf">')
                        
                        # The default search path should always have the
                        # hosts default network first in the list, after
                        # that go by whatever ordering list.network returns.
                        #
                        # If the default network in 'public' we the
                        # public DNS rather that the server on the boss.
                        
                        search = []
                        public = False
                	for row in self.call('list.host.interface', [ host ]):
                        	if row['default']:
                                        search.append(zones[row['network']])
                                        if row['network'] == 'public':
                                        	public = True

                        for zone in zones.values():
                        	if zone not in search:
                                        search.append(zone)
                        self.addOutput(host, 'search %s' % string.join(search))
                        if public:
				self.addOutput(host, 'nameserver %s' %
                                	self.db.getHostAttr(host, 'Kickstart_PublicDNSServers'))
                        else:
				self.addOutput(host, 'nameserver %s' %
                                	self.db.getHostAttr(host, 'Kickstart_PrivateDNSServers'))
                        	
			self.addOutput(host,'</file>')

		self.endOutput(padChar='')

