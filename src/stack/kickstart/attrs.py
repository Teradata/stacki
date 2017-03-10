#!/opt/stack/bin/python
import os
import sys
import cgi

from itertools import groupby
from operator import itemgetter
import ipaddress

import stack.api
import stack.password
import stack.bool


remote_ip = os.environ.get('REMOTE_ADDR', None)

if not remote_ip:
	# we only get here if this is called as a script, not CGI, and without an env var
	print ''
	sys.exit()

# look up in hosts table
results = stack.api.Call('list.host.interface', [remote_ip])
results = [row for row in results if row['ip'] == remote_ip]
results = results[0]
hostname, macaddr, iface, network = itemgetter('host', 'mac', 'interface', 'network')(results)

# get the rest of the networking info from the database
results = stack.api.Call('list.network', ['private'])[0]
net_ip, netmask, gateway, domain = itemgetter('address', 'mask', 'gateway', 'zone')(results)

# create a dictionary of 'attr' => 'list.host.attr row' of only attrs that start with 'Kickstart_'
hostattrs = dict((k,next(v)) for k,v in groupby(
	stack.api.Call('list.host.attr', [remote_ip]),
	itemgetter('attr'))
	if k.startswith('Kickstart_'))

dns_servers = hostattrs['Kickstart_PrivateDNSServers']['value']
timezone = hostattrs['Kickstart_Timezone']['value']

p = stack.password.Password()
password = p.get_crypt_pw('password')


# calculate the broadcast address, cidr
ipnetwork = ipaddress.IPv4Network(unicode(net_ip + '/' + netmask))
broadcast = ipnetwork.broadcast_address
cidr = ipnetwork.prefixlen

out = '''Info_CertificateCountry:US
Info_CertificateLocality:Solana Beach
Info_CertificateOrganization:StackIQ
Info_CertificateState:California
Info_ClusterLatlong:N32.87 W117.22
'''

out += 'Info_FQDN:{0}.{1}\n'.format(hostname, domain)
for key in ['Kickstart_Keyboard', 'Kickstart_Lang', 'Kickstart_Langsupport']:
	out += '{0}:{1}\n'.format(key, hostattrs[key]['value'])

out += 'Kickstart_PrivateAddress:{0}\n'.format(remote_ip)
out += 'Kickstart_PrivateBroadcast:{0}\n'.format(broadcast)
out += 'Kickstart_PrivateDNSDomain:{0}\n'.format(domain)
out += 'Kickstart_PrivateDNSServers:{0}\n'.format(dns_servers)
out += 'Kickstart_PrivateEthernet:{0}\n'.format(macaddr)
out += 'Kickstart_PrivateGateway:{0}\n'.format(gateway)
out += 'Kickstart_PrivateHostname:{0}\n'.format(hostname)
out += 'Kickstart_PrivateInterface:{0}\n'.format(iface)
out += 'Kickstart_PrivateKickstartHost:{0}\n'.format(remote_ip)
out += 'Kickstart_PrivateNTPHost:{0}\n'.format(remote_ip)
out += 'Kickstart_PrivateNetmask:{0}\n'.format(netmask)
out += 'Kickstart_PrivateNetmaskCIDR:{0}\n'.format(cidr)
out += 'Kickstart_PrivateNetwork:{0}\n'.format(net_ip)
out += 'Kickstart_PrivateRootPassword:{0}\n'.format(password)
out += 'Kickstart_PublicNTPHost:{0}\n'.format('pool.ntp.org')
out += 'Kickstart_Timezone:{0}\n'.format(timezone)

params = cgi.FieldStorage()
nukeval = params.getfirst('nukedisks', False)

out += 'nukedisks:{0}'.format(stack.bool.str2bool(nukeval))

print 'Content-type: text/plaintext'
print 'Content-length: %d' % len(out)
print ''
print out
