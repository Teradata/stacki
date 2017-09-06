# @SI_Copyright@
# @SI_Copyright@

import sys
import re
import ipaddress
import stack.commands

class Implementation(stack.commands.Implementation):
	def run(self, args):

		host = args[0]

		result = self.owner.call('list.host.interface', [ host ])
		udev_output = ""
		for o in result:
			interface = None
			ip = None
			netmask = None
			netname = None
			network = None
			broadcast = None

			interface = o['interface']
			ip = o['ip']
			netname = o['network']
			vlanid = o['vlan']
			mac = o['mac']

			ib_re = re.compile('^ib[0-9]+$')
			if mac:
				if not ib_re.match(interface) and interface != 'ipmi':
					udev_output += 'SUBSYSTEM=="net", '
					udev_output += 'ACTION=="add", '
					udev_output += 'DRIVERS=="?*", '
					udev_output += 'ATTR{address}=="%s", ' % mac
					udev_output += 'ATTR{type}=="1", '
					udev_output += 'KERNEL=="eth*", '
					udev_output += 'NAME="%s"\n\n' % interface

			if not netname or not ip or not interface:
				continue

			netresult = self.owner.call('list.network', [ netname ])
			for net in netresult:
				if net['network'] == netname:
					network = net['address']
					netmask = net['mask']
					ipnet = ipaddress.IPv4Network('%s/%s' % (network, netmask))
					broadcast = '%s' % ipnet.broadcast_address
					gateway = net['gateway']
					if gateway == 'None':
						gateway = None
					break

			if not network or not netmask or not broadcast:
				continue

			if interface == 'ipmi':
				channel = o['channel']

				ipmisetup = '/tmp/ipmisetup'
				self.owner.addOutput(host, '<stack:file stack:name="%s">' % ipmisetup)
				self.owner.writeIPMI(host, ip, channel, netmask, gateway, vlanid)
				self.owner.addOutput(host, '</stack:file>')
				self.owner.addOutput(host, 'chmod 500 %s' % ipmisetup)
				continue

			self.owner.addOutput(host, 
					     '<stack:file stack:name="/etc/sysconfig/network/ifcfg-%s">' 
					     % interface)
			if vlanid:
				parent_device = interface.strip().split('.')[0]
				self.owner.addOutput(host, 'ETHERDEVICE=%s' % parent_device)
				self.owner.addOutput(host, 'VLAN=yes')
			else:
				self.owner.addOutput(host, 'USERCONTROL=no')

			self.owner.addOutput(host, 'STARTMODE=auto')
			self.owner.addOutput(host, 'IPADDR=%s' % ip.strip())
			self.owner.addOutput(host, 'NETMASK=%s' % netmask.strip())
			self.owner.addOutput(host, 'NETWORK=%s' % network.strip())
			self.owner.addOutput(host, 'BROADCAST=%s' % broadcast.strip())
			self.owner.addOutput(host, 'HWADDR=%s' % mac.strip())
			self.owner.addOutput(host, '</stack:file>')

		if udev_output:
			self.owner.addOutput(host, 
					     '<stack:file stack:name="/etc/udev/rules.d/70-persistent-net.rules">')
			self.owner.addOutput(host, udev_output)
			self.owner.addOutput(host, '</stack:file>')

