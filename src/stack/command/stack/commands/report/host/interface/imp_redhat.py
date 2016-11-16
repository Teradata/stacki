#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
#

import os
import sys
import re
import stack.commands

class Implementation(stack.commands.Implementation):
	def run(self, args):
		
		host = args[0]
		
		self.owner.db.execute("""select id, name, mask, mtu
			from subnets""")

		#
		# need to prefetch the subnets data because we can't do a
		# self.owner.db.execute() in the middle of a self.owner.db.fetchall() loop
		# because it resets the MySQL cursor
		#
		subnets = {}
		for row in self.owner.db.fetchall():
			id = row[0]
			subnets[id] = row

		self.owner.db.execute("""select distinctrow 
			net.mac, net.ip, net.device, net.vlanid,
			net.subnet, net.module, net.options, net.channel,
			s.gateway from networks net, nodes n, subnets s
			where net.node = n.id and net.subnet = s.id 
			and n.name = "%s" order by net.device""" % (host))

		udev_output = ""

		for row in self.owner.db.fetchall():
			(mac, ip, device, vlanid, subnetid, module, options,
				channel, gateway) = row

			netname = None
			netmask = None
			mtu = None

			if subnetid:
				id, netname, netmask, mtu = subnets[subnetid]

			# Host attributes can override the subnets tables
			# definition of the netmask.

			x = self.owner.db.getHostAttr(host,
				'network.%s.netmask' % netname)
			if x:
				netmask = x
			
			optionlist = []
			if options:
				optionlist = shlex.split(options)
			if 'noreport' in optionlist:
				continue # don't do anything if noreport set

			if device == 'ipmi':
				self.owner.addOutput(host, '<file name="/etc/sysconfig/ipmi" perms="500">')
				self.owner.writeIPMI(host, ip, channel,
					netmask, gateway)
				self.owner.addOutput(host, '</file>')

				# ipmi is special, skip the standard stuff
				continue

			if device and device[0:4] != 'vlan':
				#
				# output a script to update modprobe.conf
				#
				self.owner.writeModprobe(host, device, module,
					optionlist)

			if vlanid:
				#
				# look up the name of the interface that
				# maps to this VLAN spec
				#
				rows = self.owner.db.execute("""select net.device from
					networks net, nodes n where
					n.id = net.node and n.name = '%s'
					and net.subnet = %d and
					net.device not like 'vlan%%' """ %
					(host, subnetid))

				if rows:
					dev, = self.owner.db.fetchone()
					#
					# check if already referencing 
					# a physical device
					#
					if dev != device:
						device = '%s.%d' % (dev, vlanid)

			#
			# for interfaces that have bridges attached, make sure
			# we get the MTU of the network that is associated
			# with the *bridge* and 
			#
			for opt in optionlist:
				if opt.startswith('bridgename='):
					bridge = opt.split('=')[1]

					rows = self.owner.db.execute("""select
						s.mtu from networks net,
						nodes n, subnets s where
						n.name = '%s' and
						n.id = net.node and 
						net.device = '%s' and
						net.subnet = s.id """ %
						(host, bridge))

					if rows:
						mtu, = self.owner.db.fetchone()

			if self.owner.interface:
				if self.owner.interface == device:
					self.owner.writeConfig(host, mac, ip, device,
						netmask, vlanid, mtu, optionlist,
						channel)
			else:
				s = '<file name="'
				s += '/etc/sysconfig/network-scripts/ifcfg-'
				s += '%s">' % (device)

				self.owner.addOutput(host, s)
				self.owner.writeConfig(host, mac, ip, device,
					netmask, vlanid, mtu, optionlist, channel)
				self.owner.addOutput(host, '</file>')

				ib_re = re.compile('^ib[0-9]+$')
				if not ib_re.match(device):
					udev_output += 'SUBSYSTEM=="net", '
					udev_output += 'ACTION=="add", '
					udev_output += 'DRIVERS=="?*", '
					udev_output += 'ATTR{address}=="%s", ' % mac
					udev_output += 'ATTR{type}=="1", '
					udev_output += 'KERNEL=="eth*", '
					udev_output += 'NAME="%s"\n\n' % device

		if udev_output:
			self.owner.addOutput(host, '<file name="/etc/udev/rules.d/70-persistent-net.rules">')
			self.owner.addOutput(host, udev_output)
			self.owner.addOutput(host, '</file>')

