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
	is False.
	</param>

	<example cmd='list attr'>
	List the global attributes.
	</example>
	"""

	def addGlobalAttrs(self, attributes):
		readonly = {}

		for (ip, host, subnet, netmask) in self.db.select(
				"""
				net.ip, if (net.name <> NULL, net.name, hv.name), 
				s.address, s.mask from 
				networks net, appliances a, subnets s, host_view hv 
				where 
				net.node=hv.id and hv.appliance=a.id and 
				a.name='frontend' and net.subnet=s.id and 
				s.name='private'
				"""):
			readonly['Kickstart_PrivateKickstartHost'] = ip
			readonly['Kickstart_PrivateAddress'] = ip
			readonly['Kickstart_PrivateHostname'] = host
			ipnetwork = ipaddress.IPv4Network(subnet + '/' + netmask)
			readonly['Kickstart_PrivateBroadcast'] = '%s' % ipnetwork.broadcast_address

		for (ip, host, zone, subnet, netmask) in self.db.select(
				"""
				net.ip, if (net.name <> NULL, net.name, hv.name), 
				s.zone, s.address, s.mask from 
				networks net, appliances a, subnets s, host_view hv
				where 
				net.node=hv.id and hv.appliance=a.id and
				a.name='frontend' and net.subnet=s.id and 
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
			attributes['global'][key] = (readonly[key], None, 'const', 'global')

		return attributes


	def addComponentAttrs(self, attributes):
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
			osname  = row['os']
			
			name    = 'unknown'
			version = 'unknown'
			for pallet in pallets:
				if pallet in versions.keys():
					(name, version) = versions[pallet]
					break

			boxes[row['name']] = { 'pallets'    : pallets,
					       'carts'	    : carts,
					       'os'         : osname, 
					       'os.version' : version }

		for (_name, _rack, _rank, _make, _model, _appliance, _environment, _box) in self.db.select(
				"""
				c.name, c.rack, c.rank, c.make, c.model, a.name, e.name, b.name
				from components c
				left join appliances a   on c.appliance   = a.id
				left join environments e on c.environment = e.id
				left join boxes b        on b.id = (select h.box from hosts h where h.hostid = c.host)
				"""):
			readonly[_name]	             = { }
			readonly[_name]['component'] = _name
			readonly[_name]['rack']      = _rack
			readonly[_name]['rank']      = _rank
			if _make:
				readonly[_name]['make']  = _make
			if _model:
				readonly[_name]['model'] = _model
			if _appliance:
				readonly[_name]['appliance'] = _appliance
			if _environment:
				readonly[_name]['environment'] = _environment
			if _box: # only hosts have boxes
				readonly[_name]['type']       = 'host'
				readonly[_name]['box']        = _box
				readonly[_name]['pallets']    = boxes[_box]['pallets']
				readonly[_name]['carts']      = boxes[_box]['carts']
				readonly[_name]['os']         = boxes[_box]['os']
				readonly[_name]['os.version'] = boxes[_box]['os.version']

				
		for (_name, _zone, _address) in self.db.select(
				"""
				c.name, s.zone, net.ip from
				networks net, components c, subnets s where
				net.main=true and net.node=c.id and
				net.subnet=s.id
				"""):
			if _address:
				readonly[_name]['addr'] = _address
			readonly[_name]['domainname'] = _zone

		# Not all components are hosts but all hosts are components. So
		# for the host types find the host-specific attributes and mix
		# those into the component-specific attributes.
		#
		# The 'box' attribute was found using the host_view, so this is
		# really about attribute names not values. Things like
		# 'hostname' need to remain since so much XML uses it (should
		# really use 'component' instead).

		for _host in readonly:
			if readonly[_host].get('type') == 'host':
				readonly[_host]['hostname'] = readonly[_host]['component']
				if 'addr' in readonly[_host]:
					readonly[_host]['hostaddr'] = readonly[_host]['addr']

		for _row in self.call('list.host.group'):
			for group in _row['groups'].split():
				readonly[_row['host']]['group.%s' % group] = 'true'
			readonly[_row['host']]['groups'] = _row['groups']
		

		for component in attributes:
			a  = attributes[component]
			r  = readonly[component]
			ro = True

			if 'const_overwrite' in a:

				# This attribute allows a component to overwrite
				# constant attributes. This is crazy dangerous,
				# do not use this attribute.

				(n, v, t, s) = a['const_overwrite']
				ro = str2bool(v)

			if ro:
				for key in r: # slam consts on top of attrs
					a[key] = (r[key], None, 'const', 'component')
			else:
				for key in r: # only add new consts to attrs
					if key not in a:
						a[key] = (r[key], None, 'const', 'component')

		return attributes




	def run(self, params, args):

		(glob, shadow, scope, resolve, var, const) = self.fillParams([ 
			('attr',   None),
			('shadow', True),
			('scope',  'global'),
			('resolve', None),
			('var',     True),
			('const',   True)
		])

		shadow	= self.str2bool(shadow)
		var	= self.str2bool(var)
		const	= self.str2bool(const)
		lookup	= { 'global'	 : { 'scope'  : 'global',
					     'fn'     : lambda x=None: [ 'global' ],
					     'const'  : self.addGlobalAttrs,
					     'resolve': False,
					     'table'  : None },
			    'os'	 : { 'scope'  : 'os',
					     'fn'     : self.getOSNames,
					     'const'  : lambda x: x,
					     'resolve': False,
					     'table'  : 'oses' },
			    'appliance'	 : { 'scope'  : 'appliance',
					     'fn'     : self.getApplianceNames, 
					     'const'  : lambda x: x,
					     'resolve': False,
					     'table'  : 'appliances' },
			    'environment': { 'scope'  : 'environment',
					     'fn'     : self.getEnvironmentNames,
					     'const'  : lambda x: x,
					     'resolve': False,
					     'table'  : 'environments' },
			    'component'  : { 'scope'  : 'component',
					     'fn'     : self.getComponentNames,
					     'const'  : self.addComponentAttrs,
					     'resolve': True,
					     'table'  : 'components' },
			    'host'	 : { 'scope'  : 'component',
					     'fn'     : self.getHostnames,
					     'const'  : self.addComponentAttrs,
					     'resolve': True,
					     'table'  : 'components' }}

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

			if var:
				table = lookup[s]['table']
				if table:
					rows = self.db.select("""
						t.name, a.attr, a.value, a.shadow 
						from attributes a, %s t where
						a.scope = '%s' and a.scopeid = t.id
						""" % (table, s))
					if rows:
						for (o, a, v, x) in rows:
							attributes[s][o][a] = (v, x, 'var', s)
					else:
						for (o, a, v) in self.db.select("""
							t.name, a.attr, a.value
							from attributes a, %s t where
							a.scope = '%s' and a.scopeid = t.id
							""" % (table, s)):
							attributes[s][o][a] = (v, None, 'var', s)

				else:
					o = target
					rows = self.db.select("""
						attr, value, shadow from attributes
						where scope = '%s'
						""" % s)
					if rows:
						for (a, v, x) in rows:
							attributes[s][o][a] = (v, x, 'var', s)
					else:
						for (a, v) in self.db.select("""
							attr, value from attributes
							where scope = '%s'
							""" % s):
							attributes[s][o][a] = (v, None, 'var', s)

			if const:
				# Mix in any const attributes
				lookup[s]['const'](attributes[s])


		targets = sorted(lookup[scope]['fn'](args))

		if resolve and scope in [ 'component', 'host' ]:
			for o in targets:
				env = self.db.getComponentEnvironment(o)
				if env:
					parent = attributes['environment'][env]
					for (a, (v, x, t, s)) in parent.items():
						if a not in attributes[scope][o]:
							attributes[scope][o][a] = (v, x, t, s)

				app = self.db.getComponentAppliance(o)
				if app:
					parent = attributes['appliance'][app]
					for (a, (v, x, t, s)) in parent.items():
						if a not in attributes[scope][o]:
							attributes[scope][o][a] = (v, x, t, s)

				osname = self.db.getHostOS(o)
				if osname:
					parent = attributes['os'][osname]
					for (a, (v, x, t, s)) in parent.items():
						if a not in attributes[scope][o]:
							attributes[scope][o][a] = (v, x, t, s)

		if resolve and scope != 'global':
			for o in targets:
				for (a, (v, x, t, s)) in attributes['global']['global'].items():
					if a not in attributes[scope][o]:
						attributes[scope][o][a] = (v, x, t, s)

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
				(v, x, t, s) = attrs[a]
				if x:
					t = 'shadow'
					if shadow:
						v = x
				if scope == 'global':
					self.addOutput(s, (t, a, v))
				else:
					self.addOutput(o, (s, t, a, v))
					
		if scope == 'global':
			self.endOutput(header=['scope', 'type', 'attr', 'value' ])
		else:
			self.endOutput(header=[scope, 'scope', 'type', 'attr', 'value' ])



