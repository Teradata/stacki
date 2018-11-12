#!/opt/stack/bin/python
import sys

sys.path.append('/tmp')
from stack_site import *

fname='/target/etc/network/interfaces'
f = open(fname,'w')
f.write('auto lo\n')
f.write('iface lo inet loopback\n\n')
f.write('source /etc/network/interfaces.d/*.cfg\n')
f.close()

for iface in interfaces:
	if iface['network'] == None:
		continue
	else:
		b = [net for net in networks if net['network'] == iface['network'] ]
	        eth,ip,mask,gw = iface['interface'],iface['ip'],b[0]['mask'],b[0]['gateway']
		f = open('/target/etc/network/interfaces.d/%s.cfg' % iface['interface'], 'w')
		f.write("auto %s\n" % eth)
		f.write("iface %s inet static\n" % eth)
		f.write("  address %s\n" % ip)
		f.write("  netmask %s\n" % mask)
		f.write("  gateway %s\n" % gw)
		f.write("  nameservers %s\n" % attributes['Kickstart_PrivateDNSServers'])
		f.close()

# create udev rules
for iface in interfaces:
	line = 'SUBSYSTEM=="net", ACTION=="add", DRIVERS=="?*", '
	line += 'ATTR{address}=="%s", ATTR{type}=="1", ' % iface['mac']
	line += 'KERNEL=="eth*", NAME="%s"\n' % iface['interface']
	f = open('/target/lib/udev/rules.d/10-network.rules','w')
	f.write(line)
	f.close()
