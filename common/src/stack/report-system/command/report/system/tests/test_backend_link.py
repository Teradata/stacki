import pytest
import testinfra
import paramiko
import socket
from stack import api
from collections import namedtuple


testinfra_hosts = [host['host'] for host in api.Call('list host', args=['a:backend'])]
class TestLinkUp:
	""" See if the interfaces stacki configures are actually up on the hosts """

	def test_link_status(self, host):
		errors = []
		interface_fields = namedtuple('interface', ['name', 'ip', 'options'])

		# Get all interfaces for this host
		try:
			hostname = host.check_output('hostname')

		except paramiko.ssh_exception.NoValidConnectionsError:
			pytest.fail(f'Could not ssh into host')

		interfaces = [
			interface_fields(name=backend['interface'], ip=backend['ip'], options=backend['options'])
			for backend in api.Call(f'list host interface {hostname}')
		]

		for link in interfaces:
			# Only want to check interfaces that have a valid ip or have dhcp set in options
			if (link.ip or (link.options and 'dhcp' in link.options.lower())) and link.name.lower() != 'ipmi':
				# Run ethtool on the interface
				ethtool_output = host.run(f'ethtool {link.name}').stdout.splitlines()
			else:
				continue

			# Flag which is set to true if ethtool reports the link is up
			link_up = False

			for line in ethtool_output:
				if 'link detected: yes' in line.lower():
					link_up = True

			if not link_up:
				errors.append(f'{link.name}')

		assert not errors, f'On host {hostname} the following links were found not connected or down: {", ".join(errors)}'
