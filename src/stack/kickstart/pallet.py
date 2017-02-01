#!/opt/stack/bin/python
import stack.api
import os

ip = os.popen('ifconfig em1 | grep -w "inet" | cut -d " " -f10').read().rstrip()

hosts = stack.api.Call('list.pallet')[:2]
out = '<rolls>'

for host in hosts:
	roll = '\n\t<roll '
	roll += '\n\t\tarch="{0}" '.format(host['arch'])
	roll += '\n\t\tdiskid="{0}" '.format('stacki-os - Disk 1')
	roll += '\n\t\tname="{0}" '.format(host['name'])
	roll += '\n\t\trelease="{0}" '.format(host['release'])
	roll += '\n\t\turl="http://{0}{1}" '.format(ip, '/install/pallets')
	roll += '\n\t\tversion="{0}" '.format(host['version'])
	roll += '\n\t/>'
	out += roll

out += '\n</rolls>'

print 'Content-type: text/xml'
print 'Content-length: %d' % len(out)
print ''
print out


rollsxml = open('rolls.xml', 'w')
rollsxml.write(out)
rollsxml.close()
