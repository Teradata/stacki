import ipaddress
import stack.api as api


def test_hosts_in_correct_networks():
	'''
	Verifies for each interface with an ip and network, that the ip could exist in that network's ip space
	'''

	ifaces = api.Call('list.host.interface', ['expanded=true'])
	networks = api.Call('list.network')
	get_ip_space = lambda addr, mask: ipaddress.IPv4Network(f"{addr}/{mask}")
	networks = {net['network']: get_ip_space(net['address'], net['mask']) for net in api.Call('list.network')}

	errors = []
	for row in ifaces:
		if not row['ip']:
			continue
		if not row['network']:
			continue
		if ipaddress.IPv4Address(row['ip']) not in networks[row['network']]:
			errors.append(f"{row['ip']} ({row['host']}) not in {networks[row['network']]} ({row['network']})")

	assert not errors
