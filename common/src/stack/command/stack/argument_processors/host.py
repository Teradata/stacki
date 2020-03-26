# @copyright@
# Copyright (c) 2006 - 2019 Teradata
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
from functools import partial

from stack.exception import CommandError, ArgRequired, ArgUnique
from stack.bool import str2bool
from stack.cond import EvalCondExpr
from stack.util import flatten

class HostArgProcessor:
	"""
	An Interface class to add the ability to process host arguments.
	"""

	def sortHosts(self, hosts):
		def racksort(a):
			try:
				retval = int(a['rack'])
			except:
				retval = a['rack']
			return retval

		def ranksort(a):
			try:
				retval = int(a['rank'])
			except:
				retval = a['rank']
			return retval

		rank = sorted((h for h in hosts if h['rank'].isnumeric()), key=ranksort)
		rank += sorted((h for h in hosts if not h['rank'].isnumeric()), key=ranksort)

		rack = sorted((h for h in rank if h['rack'].isnumeric()), key=racksort)
		rack += sorted((h for h in rank if not h['rack'].isnumeric()), key=racksort)

		hosts = []
		for r in rack:
			hosts.append((r['host'],))

		return hosts

	def getHostnames(self, names=[], managed_only=False, subnet=None, host_filter=None, order='asc'):
		"""
		Expands the given list of names to valid cluster hostnames.	A name can be:

		- hostname
		- IP address
		- MAC address
		- where COND (e.g. 'where appliance=="backend"')

		Any combination of these is valid.  If the names list
		is empty a list of all hosts in the cluster is
		returned.

		The 'managed_only' flag means that the list of hosts will
		*not* contain hosts that traditionally don't have ssh login
		shells (for example, the following appliances usually don't
		have ssh login access: 'Ethernet Switches', 'Power Units',
		'Remote Management')

		The 'host_filter' flag is a callable (function, lambda, etc)
		that will be passed along with the final host list to filter().
		Equivalent code would look something like this:
		[host for host in final_host_list if host_filter(host)]

		Because filter() requires the callable to have only one arg,
		to allow access to 'self' as well as the host, host_filter()
		and 'self' are frozen with 'functools.partial', even if 'self'
		isn't required.	 The second arg will be each host name in the list.
		For example:
		host_filter = lambda self, host: self.db.getHostOS(host) == 'redhat'
		"""

		adhoc	 = False
		hostList = []
		hostDict = {}

		# List the frontend first
		frontends = self.db.select("""
			n.name from nodes n, appliances a
			where a.name='frontend' and a.id=n.appliance order by rack, rank %s
		""" % order)

		# Performance improvement for `list host profile`
		if (
			names==["a:frontend"]
			and managed_only == False
			and subnet == None
			and host_filter == None
		):
			return flatten(frontends)

		# Now get the backend appliances
		rows = self.db.select("""
			n.name, n.rack, n.rank from nodes n, appliances a
			where a.name != "frontend" and a.id=n.appliance
		""")

		hosts = []
		if frontends:
			hosts.extend(frontends)

		sortem = []
		for host, rack, rank in rows:
			sortem.append({ 'host' : host, 'rack' : rack, 'rank' : rank })

		backends = self.sortHosts(sortem)

		if backends:
			hosts.extend(backends)

		for host, in hosts:
			# If we have a list of hostnames (or groups) then
			# disable all the hosts first and selectively
			# turn them on later.
			# Otherwise just enable all the hosts.
			#
			# The hostList is used to preserve the SQL sort order
			# in the output, and the hostDict use use to map
			# the hosts on/off in the returned host list
			#
			# If the subnet names a network the hostname
			# stored in the hostDict will be the name of that
			# interface rather than the name in the nodes table

			hostList.append(host)

			if names:
				hostDict[host] = None
			else:
				hostDict[host] = self.db.getNodeName(host, subnet)

		l = []
		if names:
			for host in names:
				tokens = host.split(':', 1)
				if len(tokens) == 2:
					scope, target = tokens
					if scope == 'a':
						l.append('where appliance == "%s"' % target)
					elif scope == 'e':
						l.append('where environment == "%s"' % target)
					elif scope == 'o':
						l.append('where os == "%s"' % target)
					elif scope == 'b':
						l.append('where box == "%s"' % target)
					elif scope == 'g':
						l.append('where group.%s == True' % target)
					elif scope == 'r':
						l.append('where rack == "%s"' % target)
					adhoc = True
					continue

				if host.find('where') == 0:
					l.append(host)
					adhoc = True
					continue

				l.append(host.lower())
		names = l

		# If we have any Ad-Hoc groupings we need to load the attributes
		# for every host in the nodes tables.  Since this is a lot of
		# work handle the common case and avoid the work when just
		# a list of hosts.
		#
		# Also load the attributes if the managed_only argument is true
		# since we need to looked the managed attribute.

		hostAttrs  = {}
		for host in hostList:
			hostAttrs[host] = {}
		if adhoc or managed_only:
			for row in self.call('list.host.attr', hostList):
				h = row['host']
				a = row['attr']
				v = row['value']
				hostAttrs[h][a] = v

		# Finally iterate over all the host/groups
		list	 = []
		explicit = {}
		for name in names:
			# Ad-hoc group
			if name.find('where') == 0:
				for host in hostList:
					exp = name[5:]
					try:
						res = EvalCondExpr(exp, hostAttrs[host])
					except SyntaxError:
						raise CommandError(self, 'group syntax "%s"' % exp)
					if res:
						s = self.db.getHostname(host, subnet)
						hostDict[host] = s
						if host not in explicit:
							explicit[host] = False

			# Glob regex hostname
			#
			# Do extra work to make globbing case insensitve for
			# people that use uppercase hostname (don't be that
			# guy).
			elif '*' in name or '?' in name or '[' in name:
				for lower in fnmatch.filter([h.lower() for h in hostList], name):
					host = self.db.getHostname(lower) # fix case
					hostDict[host] = self.db.getHostname(host, subnet)
					if host not in explicit:
						explicit[host] = False

			# Simple hostname
			else:
				host = self.db.getHostname(name)
				explicit[host] = True
				hostDict[host] = self.db.getHostname(name, subnet)

		# Preserving the SQL ordering build the list of hostname
		# selected.
		#
		# For each sorted host in the hostList include host if
		# the is an entry in the hostDict (interface name).
		#
		# If called with managed_only==True, filter out all
		# unmanaged hosts unless they explicitly appear in
		# the names list.  This effectively enforces the
		# filtering only on groups.
		list = []
		for host in hostList:
			if not hostDict[host]:
				continue

			if managed_only:
				managed = str2bool(hostAttrs[host]['managed'])
				if not managed and not explicit.get(host):
					continue

			list.append(hostDict[host])

		# finally, apply the host_filter function, if it was passed
		# explicitly check host_filter, because filter(None, iterable) has a semantic meaning
		if host_filter:
			# filter(func, iterable) requires that func take a single argument
			# so we use functools.partial to get a function with one argument 'locked'
			part_func = partial(host_filter, self)
			list = filter(part_func, list)

		return list

	def getHosts(self, args):
		"""
		Return the host names for the hosts or patterns specified in args,
		and raise an ArgRequired if no hosts are found.
		"""

		if len(args) == 0:
			raise ArgRequired(self, 'host')

		hosts = self.getHostnames(args)

		if not hosts:
			raise ArgRequired(self, 'host')

		return hosts

	def getSingleHost(self, args):
		"""
		Return the host name for the host or pattern specified in args.
		Raise an ArgRequired if no hosts are found, and a ArgUnique if
		more than a single host is found.
		"""

		hosts = self.getHosts(args)

		if len(hosts) != 1:
			raise ArgUnique(self, 'host')

		return hosts[0]

	def getRunHosts(self, hosts):
		"""Return a mapping of hosts to their accessible network addresses.
		The network addresses are either user defined using the "stack.network"
		attribute, or defaults to the any pxe-enabled network, with the default
		network being priority.
		This function needs to be called for any command that connects to backends
		over SSH to run commands - typically "sync host..." or "run host" commands
		"""

		# Get a list of all attributes for the hosts, and convert the output
		# to a usable dictionary of host to attribute:value mapping
		attrs = {}
		for row in self.call('list.host.attr', hosts):
			host = row['host']
			attr = row['attr']
			value= row['value']
			if host not in attrs:
				attrs[host] = {}
			attrs[host][attr] = value

		# Create a dictionary of hosts to the names by which they will be accessed.
		# This defaults to the hostname known to Stacki will be used as the hostname
		# used to access the node.
		h = { host: host for host in hosts }

		# Get a list of all the host interfaces for the hosts specified.
		host_if = self.call('list.host.interface', hosts + ['expanded=True'])

		for host in hosts:
			# If "stack.network" attribute is specified and points to a valid network
			# use the hostname of the host on THAT network.
			if 'stack.network' in attrs[host]:
				h[host] = self.getHostnames([host], subnet = attrs[host]['stack.network'])[0]
			# If not get the list of all PXE-Enabled addresses for the host, with the "default"
			# network being prioritized. If one of the PXE-Enabled networks isn't default, then
			# just use the first one returned by the database.
			else:
				# List of PXE-enabled networks for host where default = True
				net = [ f['network'] for f in host_if if f['pxe'] == True and f['host'] == host and f['default'] == True ]
				if not net:
					# List of PXE-enabled networks for host if no default is found
					net = [ f['network'] for f in host_if if f['pxe'] == True and f['host'] == host ]
				if not net:
					# If no PXE-enabled networks are found, we still have the original hostname of the host
					continue
				else:
					h[host] = self.getHostnames([host], subnet=net[0])[0]

		run_hosts = [ {'host': host, 'name': h[host] } for host in h ]
		return run_hosts
