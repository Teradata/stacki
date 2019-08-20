# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import socket
import ipaddress
import netifaces
from stack.exception import CommandError
import stack.commands


class Command(stack.commands.report.command):
	"""
	Constructs a minimal site.attr file strictly from inspecting
	the host the command is run on.

	<param type='string' name='interface' optional='0'>
	Name of the private interface (defaults to eth0)
	</param>
	"""

	def run(self, params, args):

		(private, ) = self.fillParams([
			('interface', 'eth0')
			])

		if private not in netifaces.interfaces():
			raise CommandError(self, 'unkown interface %s' % private)

		addrs     = netifaces.ifaddresses(private)
		mac	  = addrs[netifaces.AF_LINK][0]['addr']
		ip	  = addrs[netifaces.AF_INET][0]['addr']
		mask	  = addrs[netifaces.AF_INET][0]['netmask']
		broadcast = addrs[netifaces.AF_INET][0]['broadcast']
		fqdn      = socket.gethostbyaddr(ip)[0]
		net       = ipaddress.IPv4Network('%s/%s' % (ip, mask), strict=False)

		(gateway, dev) = netifaces.gateways()['default'][netifaces.AF_INET]
		try:
			(hostname, domainname) = fqdn.split('.', 1)
		except ValueError:
			hostname = fqdn
			domainname = ''

		nameserver = ''
		with open('/etc/resolv.conf', 'r') as fin:
			for line in fin:
				if line.startswith('nameserver'):
					nameserver = line[10:].strip()

		attrs = { 
			'Info_CertificateCountry'        : 'US',
			'Info_CertificateLocality'       : 'San Diego',
			'Info_CertificateOrganization'   : 'Stacki',
			'Info_CertificateState'          : 'California',
			'Info_ClusterLatlong'            : 'N32.87 W117.22',
			'Info_FQDN'                      : fqdn,
			'Kickstart_Keyboard'             : 'us',
			'Kickstart_Lang'                 : 'en_US',
			'Kickstart_Langsupport'          : 'en_US',
			'Kickstart_PrivateAddress'       : ip,
			'Kickstart_PrivateDNSDomain'     : domainname,
			'Kickstart_PrivateDNSServers'    : nameserver,
			'Kickstart_PrivateEthernet'      : mac,
			'Kickstart_PrivateGateway'       : gateway,
			'Kickstart_PrivateHostname'      : hostname,
			'Kickstart_PrivateInterface'     : private,
			'Kickstart_PrivateKickstartHost' : ip,
			'Kickstart_PrivateNetmask'       : net.netmask,
			'Kickstart_PrivateNetmaskCIDR'   : net.prefixlen,
			'Kickstart_PrivateNetwork'       : net.network_address,
			'Kickstart_PrivateRootPassword'  : '*',
			'Kickstart_PublicNTPHost'        : 'pool.ntp.org',
			'Kickstart_Timezone'             : 'UTC'
			}


		self.beginOutput()
		for key in sorted(attrs.keys()):
			self.addOutput('', '%s:%s' % (key, attrs[key]))
		self.endOutput()

