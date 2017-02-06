#!/opt/stack/bin/python
import stack.api
import os

ip = ''
for row in stack.api.Call('list.attr'):
	if row['attr'] == 'Kickstart_PrivateAddress':
		ip = row['value']

# get IP of connecting client, look up in hosts table,
# offer pallets in that host's box
remote_ip = os.environ.get('REMOTE_ADDR', None)
box = None
if remote_ip:
	for row in stack.api.Call('list.host.attr', [remote_ip]):
		if row['attr'] == 'box':
			box = row['value']

pallets_to_use = ['stacki', 'os']
if box:
	pallets_to_use = [row['pallet'] for row in stack.api.Call('list.box.pallet', [box])]

out = '<rolls>'
for pallet in stack.api.Call('list.pallet'):
	if pallet['name'] not in pallets_to_use:
		continue

	roll = '\n\t<roll '
	roll += '\n\t\tarch="{0}" '.format(pallet['arch'])
	roll += '\n\t\tdiskid="{0}" '.format('stacki-os - Disk 1')
	roll += '\n\t\tname="{0}" '.format(pallet['name'])
	roll += '\n\t\trelease="{0}" '.format(pallet['release'])
	roll += '\n\t\turl="http://{0}{1}" '.format(ip, '/install/pallets')
	roll += '\n\t\tversion="{0}" '.format(pallet['version'])
	roll += '\n\t/>'
	out += roll

out += '\n</rolls>'

print 'Content-type: text/xml'
print 'Content-length: %d' % len(out)
print ''
print out
