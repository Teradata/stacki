# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import fnmatch
import ipaddress
import stack.attr
import stack.commands
from stack.bool import str2bool
from stack.exception import CommandError


class Command(stack.commands.Command,
	      stack.commands.OSArgumentProcessor,
	      stack.commands.ApplianceArgumentProcessor,
	      stack.commands.EnvironmentArgumentProcessor,
	      stack.commands.HostArgumentProcessor):
	"""
	Lists the set of global attributes.

	<param type='string' name='attr'>
	A shell syntax glob pattern to specify to attributes to
	be listed.
	</param>

	<param type='boolean' name='shadow'>
	Specifies is shadow attributes are listed, the default
	is True.
	</param>

	<example cmd='list attr'>
	List the global attributes.
	</example>
	"""

	def addGlobalAttrs(self, attributes):
		readonly = {}

		for (ip, host, subnet, netmask) in self.db.select(
				"""
				n.ip, if (n.name <> NULL, n.name, nd.name), 
				s.address, s.mask from 
				networks n, appliances a, subnets s, nodes nd 
				where 
				n.node=nd.id and nd.appliance=a.id and 
				a.name='frontend' and n.subnet=s.id and 
				s.name='private'
				"""):
			readonly['Kickstart_PrivateKickstartHost'] = ip
			readonly['Kickstart_PrivateAddress'] = ip
			readonly['Kickstart_PrivateHostname'] = host
			ipnetwork = ipaddress.IPv4Network(subnet + '/' + netmask)
			readonly['Kickstart_PrivateBroadcast'] = '%s' % ipnetwork.broadcast_address

		for (ip, host, zone, subnet, netmask) in self.db.select(
				"""
				n.ip, if (n.name <> NULL, n.name, nd.name), 
				s.zone, s.address, s.mask from 
				networks n, appliances a, subnets s, nodes nd 
				where 
				n.node=nd.id and nd.appliance=a.id and
				a.name='frontend' and n.subnet=s.id and 
				s.name='public'
				"""):
			readonly['Kickstart_PublicAddress'] = ip
			readonly['Kickstart_PublicHostname'] = '%s.%s' % (host, zone)
			ipnetwork = ipaddress.IPv4Network(u'%s/%s' % (subnet, netmask))
			readonly['Kickstart_PublicBroadcast'] = '%s' % ipnetwork.broadcast_address

		for (name, subnet, netmask, zone) in self.db.select(
				"""
				name, address, mask, zone from 
				subnets
				"""):
			ipnetwork = ipaddress.IPv4Network(u'%s/%s' % (subnet, netmask))
			if name == 'private':
				readonly['Kickstart_PrivateDNSDomain'] = zone
				readonly['Kickstart_PrivateNetwork'] = subnet
				readonly['Kickstart_PrivateNetmask'] = netmask
				readonly['Kickstart_PrivateNetmaskCIDR'] = '%s' % ipnetwork.prefixlen
			elif name == 'public':
				readonly['Kickstart_PublicDNSDomain'] = zone
				readonly['Kickstart_PublicNetwork'] = subnet
				readonly['Kickstart_PublicNetmask'] = netmask
				readonly['Kickstart_PublicNetmaskCIDR'] = '%s' % ipnetwork.prefixlen

		readonly['release'] = stack.release
		readonly['version'] = stack.version

		for key in readonly:
			attributes['global'][key] = (readonly[key], 'const', 'global')

		return attributes


	def addHostAttrs(self, attributes):
		readonly = {}

		versions = {}
		for row in self.call('list.pallet'):
			# Compute a version number for each os pallet
			#
			# If the pallet already has a '.' take everything
			# before the '.' and add '.x'. If the version has no
			# '.' add '.x'
			name    = row['name']
			version = row['version']
			release = row['release']
			key     = '%s-%s-%s' % (name, version, release)

			if name in [ 'SLES', 'CentOS' ]: # FIXME: Ubuntu is missing
				versions[key] = (name, '%s.x' % version.split('.')[0])

		boxes = {}
		for row in self.call('list.box'):
			pallets = row['pallets'].split()
			carts   = row['carts'].split()
			
			name    = 'unknown'
			version = 'unknown'
			for pallet in pallets:
				if pallet in versions.keys():
					(name, version) = versions[pallet]
					break

			boxes[row['name']] = { 'pallets'    : pallets,
					       'carts'	    : carts,
					       'os.name'    : name, 
					       'os.version' : version }

		for (name, environment, rack, rank, metadata) in self.db.select(
				"""
				n.name, e.name, n.rack, n.rank, n.metadata 
				from nodes n
				left join environments e on n.environment=e.id
				"""):
			readonly[name]	       = {}
			readonly[name]['rack'] = rack
			readonly[name]['rank'] = rank
			if environment:
				readonly[name]['environment'] = environment
			if metadata:
				readonly[name]['metadata'] = metadata

		for (name, box, appliance) in self.db.select(
				""" 
				n.name, b.name,
				a.name from
				nodes n, boxes b, appliances a where
				n.appliance=a.id and n.box=b.id
				"""):
			readonly[name]['box']		     = box
			readonly[name]['pallets']	     = boxes[box]['pallets']
			readonly[name]['carts']		     = boxes[box]['carts']
#			readonly[name]['os.name']            = boxes[box]['os.name']
			readonly[name]['os.version']         = boxes[box]['os.version']
			readonly[name]['appliance']	     = appliance

				
		for (name, zone, address) in self.db.select(
				"""
				n.name, s.zone, nt.ip from
				networks nt, nodes n, subnets s where
				nt.main=true and nt.node=n.id and
				nt.subnet=s.id
				"""):
			if address:
				readonly[name]['hostaddr']   = address
			readonly[name]['domainname'] = zone

		for host in readonly:
			readonly[host]['os']	   = self.db.getHostOS(host)
			readonly[host]['hostname'] = host

		for row in self.call('list.host.group'):
			for group in row['groups'].split():
				readonly[row['host']]['group.%s' % group] = 'true'
			readonly[row['host']]['groups'] = row['groups']
		

		for host in attributes:
			a  = attributes[host]
			r  = readonly[host]
			ro = True

			if 'const_overwrite' in a:

				# This attribute allows a host to overwrite
				# constant attributes. This is crazy dangerous,
				# do not use this attribute.

				(n, v, t, s) = a['const_overwrite']
				ro = str2bool(v)

			if ro:
				for key in r: # slam consts on top of attrs
					a[key] = (r[key], 'const', 'host')
			else:
				for key in r: # only add new consts to attrs
					if key not in a:
						a[key] = (r[key], 'const', 'host')

		return attributes




	def run(self, params, args):

		(glob, shadow, scope, resolve, var, const) = self.fillParams([ 
			('attr',   None),
			('shadow', True),
			('scope',  'global'),
			('resolve', None),
			('var', True),
			('const', True)
		])

		shadow	= self.str2bool(shadow)
		var	= self.str2bool(var)
		const	= self.str2bool(const)
		lookup	= { 'global'	 : { 'fn'     : lambda x=None: [ 'global' ],
					     'const'  : self.addGlobalAttrs,
					     'resolve': False,
					     'table'  : None },
			    'os'	 : { 'fn'     : self.getOSNames,
					     'const'  : lambda x: x,
					     'resolve': False,
					     'table'  : 'oses' },
			    'appliance'	 : { 'fn'     : self.getApplianceNames, 
					     'const'  : lambda x: x,
					     'resolve': False,
					     'table'  : 'appliances' },
			    'environment': { 'fn'     : self.getEnvironmentNames,
					     'const'  : lambda x: x,
					     'resolve': False,
					     'table'  : 'environments' },
			    'host'	 : { 'fn'     : self.getHostnames,
					     'const'  : self.addHostAttrs,
					     'resolve': True,
					     'table'  : 'nodes' }}

		if scope not in lookup.keys():
			raise CommandError(self, 'invalid scope "%s"' % scope)

		if resolve is None:
			resolve = lookup[scope]['resolve']
		else:
			resolve = self.str2bool(resolve)

		attributes = {}
		for s in lookup.keys():
			attributes[s] = {}
			for target in lookup[s]['fn']():
				attributes[s][target] = {}

			# Do a UNION select for the attributes in the cluster
			# and shadow database. This is done to minimize the
			# calls/context switches to the database. If the user
			# doesn't have permission to access the shadow
			# database, we fallback to just selecting out of the
			# cluster database.

			if var:
				table = lookup[s]['table']
				if table:
					rows = self.db.select(
						"""
						t.name, true, a.attr, a.value from
						shadow.attributes a, %s t where
						a.scope = %%s and a.scopeid = t.id
						union select
						t.name, false, a.attr, a.value from 
						attributes a, %s t where
						a.scope = %%s and a.scopeid = t.id
						""" % (table, table), (s, s))
					if not rows:
						rows = self.db.select(
							"""
							t.name, false, a.attr, a.value from 
							attributes a, %s t where
							a.scope = %%s and a.scopeid = t.id
							""" % table, s)

					for (o, x, a, v) in rows:
						if not x:
							attributes[s][o][a] = (v, 'var', s)
					if shadow:
						for (o, x, a, v) in rows:
							if x:
								attributes[s][o][a] = (v, 'shadow', s)
				else:
					o = target

					rows = self.db.select(
						"""
						true, attr, value from shadow.attributes
						where scope = %s
						union select 
						false, attr, value from attributes
						where scope = %s
						""", (s, s))
					if not rows:
						rows = self.db.select(
							"""
							false, attr, value from attributes
							where scope = %s
							""", s)

					for (x, a, v) in rows:
						if not x:
							attributes[s][o][a] = (v, 'var', s)
					if shadow:
						for (x, a, v) in rows:
							if x:
								attributes[s][o][a] = (v, 'shadow', s)

			if const:
				# Mix in any const attributes
				lookup[s]['const'](attributes[s])


		targets = sorted(lookup[scope]['fn'](args))

		if resolve and scope == 'host':
			for o in targets:
				env = self.db.getHostEnvironment(o)
				if env:
					parent = attributes['environment'][env]
					for (a, (v, t, s)) in parent.items():
						if a not in attributes[scope][o]:
							attributes[scope][o][a] = (v, t, s)

				parent = attributes['appliance'][self.db.getHostAppliance(o)]
				for (a, (v, t, s)) in parent.items():
					if a not in attributes[scope][o]:
						attributes[scope][o][a] = (v, t, s)

				parent = attributes['os'][self.db.getHostOS(o)]
				for (a, (v, t, s)) in parent.items():
					if a not in attributes[scope][o]:
						attributes[scope][o][a] = (v, t, s)

		if resolve and scope != 'global':
			for o in targets:
				for (a, (v, t, s)) in attributes['global']['global'].items():
					if a not in attributes[scope][o]:
						attributes[scope][o][a] = (v, t, s)

		if glob:
			for o in targets:
				matches = {}
				for key in fnmatch.filter(attributes[scope][o].keys(), glob):
					matches[key] = attributes[scope][o][key]
				attributes[scope][o] = matches

			

		self.beginOutput()

		for o in targets:
			attrs = attributes[scope][o]
			for a in sorted(attrs.keys()):
				(v, t, s) = attrs[a]
				if scope == 'global':
					self.addOutput(s, (t, a, v))
				else:
					self.addOutput(o, (s, t, a, v))
					
		if scope == 'global':
			self.endOutput(header=['scope', 'type', 'attr', 'value' ])
		else:
			self.endOutput(header=[scope, 'scope', 'type', 'attr', 'value' ])



