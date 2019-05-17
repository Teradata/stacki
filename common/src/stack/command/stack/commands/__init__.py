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

import os
import time
import socket
import string
import re
import fnmatch
import syslog
import pwd
import sys
import json
import marshal
import hashlib
import subprocess
from xml.sax import saxutils
from xml.sax import handler
from xml.sax import make_parser
from pymysql import OperationalError, ProgrammingError
from functools import partial
from operator import itemgetter
from itertools import groupby, cycle
from collections import OrderedDict, namedtuple
from concurrent.futures import ThreadPoolExecutor
import threading

import stack.graph
import stack
from stack.cond import EvalCondExpr
from stack.exception import (
	CommandError, ParamRequired, ArgNotFound, ArgRequired, ArgUnique, ParamError
)
from stack.bool import str2bool, bool2str
from stack.util import flatten
import stack.util

_logPrefix = ''
_debug     = False


def Log(message, level=syslog.LOG_INFO):
	"""
	Send a message to syslog
	"""
	syslog.syslog(level, '%s%s' % (_logPrefix, message))


def Warn(message):
	"""
	Send a warning to syslog
	"""
	syslog.syslog(syslog.LOG_WARNING, f'{_logPrefix}{message}')


def Debug(message, level=syslog.LOG_DEBUG):
	"""
	If the environment variable STACKDEBUG is set,
	send a message to syslog and stderr.
	"""

	if _debug:
		m = ''
		p = ''
		for c in message.strip():
			if c in string.whitespace and p in string.whitespace:
				pass
			else:
				if c == '\n':
					m += ' '
				else:
					m += c
			p = c
		Log(message, level)
		sys.__stderr__.write('%s\n' % m)


class OSArgumentProcessor:
	"""
	An Interface class to add the ability to process os arguments.
	"""

	def getOSNames(self, args=None):
		oses = []
		if not args:
			args = ['%']		# find everything in table

		for arg in args:
			if arg == 'centos':
				if 'redhat' in oses:
					continue
				arg = 'redhat'

			names = flatten(self.db.select(
				'name from oses where name like %s order by name', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'OS')

			oses.extend(names)

		return sorted(OrderedDict.fromkeys(oses))


class EnvironmentArgumentProcessor:
	"""
	An Interface class to add the ability to process environment arguments.
	"""

	def getEnvironmentNames(self, args=None):
		environments = []
		if not args:
			args = ['%']		# find everything in table

		for arg in args:
			names = flatten(self.db.select(
				'name from environments where name like %s', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'environment')

			environments.extend(names)

		return sorted(OrderedDict.fromkeys(environments))


class ApplianceArgumentProcessor:
	"""
	An Interface class to add the ability to process appliance arguments.
	"""

	def getApplianceNames(self, args=None):
		"""
		Returns a list of appliance names from the database. For each arg
		in the ARGS list find all the appliance names that match the arg
		(assume SQL regexp). If an arg does not match anything in the
		database we raise an exception. If the ARGS list is empty return
		all appliance names.
		"""

		appliances  = []
		if not args:
			args = ['%']		 # find all appliances

		for arg in args:
			names = flatten(self.db.select(
				'name from appliances where name like %s', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'appliance')

			appliances.extend(names)

		return appliances


class BoxArgumentProcessor:
	"""
	An Interface class to add the ability to process box arguments.
	"""

	def getBoxNames(self, args=None):
		"""
		Returns a list of box names from the database. For each arg in
		the ARGS list find all the box names that match the arg (assume
		SQL regexp). If an arg does not match anything in the database we
		raise an exception. If the ARGS list is empty return all box names.
		"""

		boxes = []
		if not args:
			args = ['%']		      # find all boxes

		for arg in args:
			names = flatten(self.db.select(
				'name from boxes where name like %s', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'box')

			boxes.extend(names)

		return boxes

	def getBoxPallets(self, box='default'):
		"""
		Returns a list of pallets for a box
		"""

		# Make sure 'box' exists
		self.getBoxNames([box])

		pallets = []

		Pallet = namedtuple(
			"Pallet", ['id', 'name', 'version', 'rel', 'arch', 'os', 'url']
		)

		rows = self.db.select("""
			r.id, r.name, r.version, r.rel, r.arch, o.name, r.url
			from rolls r, boxes b, stacks s, oses o
			where b.name=%s and b.id=s.box and s.roll=r.id and b.os=o.id
		""", (box,))

		pallets.extend([Pallet(*row) for row in rows])

		return pallets


class NetworkArgumentProcessor:
	"""
	An Interface class to add the ability to process network (subnet) argument.
	"""

	def getNetworkNames(self, args=None):
		"""
		Returns a list of network (subnet) names from the database. For
		each arg in the ARGS list find all the network names that match
		the arg (assume SQL regexp). If an arg does not match anything
		in the database we raise an exception. If the ARGS list is empty
		return all network names.
		"""

		networks = []
		if not args:
			args = [ '%' ]		   # find all networks

		for arg in args:
			names = flatten(self.db.select(
				'name from subnets where name like %s', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'network')

			networks.extend(names)

		return networks

	def getNetworkName(self, netid):
		"""
		Returns a network (subnet) name from the database that
		is associated with the id 'netid'.
		"""

		if not netid:
			return ''

		rows = self.db.select('name from subnets where id=%s', (netid,))

		if rows:
			netname = rows[0][0]
		else:
			netname = ''

		return netname


class SwitchArgumentProcessor:
	"""
	An interface class to add the ability to process switch arguments.
	"""

	def getSwitchNames(self, args=None):
		"""
		Returns a list of switch names from the database. For each arg
		in the ARGS list find all the switch names that match the arg
		(assume SQL regexp). If an arg does not match anything in the
		database we raise an exception. If the ARGS list is empty return
		all network names.
		"""

		switches = []
		if not args:
			args = ['%'] # find all switches

		for arg in args:
			names = flatten(self.db.select("""
				n.name from nodes n, appliances a
				where n.appliance=a.id and a.name='switch' and n.name like %s
				order by rack, rank
			""", (arg,)))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'switch')

			switches.extend(names)

		return switches

	def delSwitchEntries(self, args=None):
		"""
		Delete foreign key references from switchports
		"""

		if not args:
			return

		for arg in args:
			self.db.execute("""
				delete from switchports
				where switch=(select id from nodes where name=%s)
			""", (arg,))

	def getSwitchNetwork(self, switch):
		"""
		Returns the network the switch's management interface is on.
		"""

		if not switch:
			return ''

		rows = self.db.select("""
			subnet from networks
			where node=(select id from nodes where name=%s)
		""", (switch,))

		if rows:
			network = rows[0][0]
		else:
			network = ''

		return network

	def doSwitchHost(self, switch, port, host, interface, action):
		rows = self.db.select("""
			id from networks
			where node=(select id from nodes where name=%s) and device=%s
		""", (host, interface))

		try:
			host_interface = rows[0][0]
		except:
			host_interface = None

		if not host_interface:
			raise CommandError(self,
				"Interface '%s' isn't defined for host '%s'"
				% (interface, switch))

		# Check if the port is already managed by the switch
		rows = self.db.select("""
			* from switchports
			where interface=%s and port=%s
			and switch=(select id from nodes where name=%s)
		""", (host_interface, port, switch))

		if action == 'remove' and rows:
			# delete it
			self.db.execute("""
				delete from switchports
				where interface=%s and switch=(
					select id from nodes where name=%s
				) and port=%s
			""", (host_interface, switch, port))
		elif action == 'add' and not rows:
			# add it
			self.db.execute("""
				insert into switchports (interface, switch, port)
				values (%s, (select id from nodes where name=%s), %s)
			""", (host_interface, switch, port))

	def addSwitchHost(self, switch, port, host, interface):
		"""
		Add a host/interface to a switch/port
		"""
		self.doSwitchHost(switch, port, host, interface, 'add')

	def delSwitchHost(self, switch, port, host, interface):
		"""
		Remove a host/interface from a switch/port
		"""
		self.doSwitchHost(switch, port, host, interface, 'remove')

	def getHostsForSwitch(self, switch):
		"""
		Return a dictionary of hosts that are connected to the switch.
		Each entry will be keyed off of the port since most of the information
		stored by the switch is based off port.
		"""

		hosts = {}
		rows = self.db.select("""
			n.name, i.device, s.port, i.vlanid, i.mac
			from nodes n, networks i, switchports s
			where s.switch=(select id from nodes where name=%s)
			and i.id=s.interface and n.id=i.node
		""", (switch,))

		for host, interface, port, vlanid, mac in rows:
			hosts[str(port)] = {
				'host': host,
				'interface': interface,
				'port': port,
				'vlan': vlanid,
				'mac': mac,
			}

		return hosts


class CartArgumentProcessor:
	"""
	An Interface class to add the ability to process cart arguments.
	"""

	def getCartNames(self, args):
		carts = []
		if not args:
			args = ['%']		 # find all cart names

		for arg in args:
			names = flatten(self.db.select(
				'name from carts where name like binary %s', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'cart')

			carts.extend(names)

		return carts


class PalletArgumentProcessor:

	def getPallets(self, args, params):
		"""
		Returns a Pallet namedtuple with the fields:
			name, version, rel, arch, os, url

		If args is None or empty then all pallets are returned.

		SQL regexp can be used in both the parameter and arg lists, but
		must expand to something.
		"""

		# Load the params but default to SQL wildcards
		version = params.get('version', '%')
		rel = params.get('release', '%')
		arch = params.get('arch', '%')
		os = params.get('os', '%')

		# Find all pallet names if we weren't given one
		if not args:
			args = ['%']

		Pallet = namedtuple('Pallet', [
			'id', 'name', 'version', 'rel', 'arch', 'os', 'url'
		])

		pallets = []
		for arg in args:
			rows = self.db.select("""
				id, name, version, rel, arch, os, url from rolls
				where name like binary %s and version like binary %s
				and rel like binary %s and arch like binary %s
				and os like binary %s
			""", (arg, version, rel, arch, os))

			if not rows and arg != '%':
				raise ArgNotFound(self, arg, 'pallet', params)

			# Add our pallet models to the list
			pallets.extend([Pallet(*row) for row in rows])

		return pallets


class HostArgumentProcessor:
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
					# Debug('group %s is %s for %s' %
					# 	(exp, res, host))

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


class ScopeArgumentProcessor(
	ApplianceArgumentProcessor,
	OSArgumentProcessor,
	EnvironmentArgumentProcessor,
	HostArgumentProcessor
):
	def getScopeMappings(self, args=None, scope=None):
		# We will return a list of these
		ScopeMapping = namedtuple(
			'ScopeMapping',
			['scope', 'appliance_id', 'os_id', 'environment_id', 'node_id']
		)
		scope_mappings = []

		# Validate the different scopes and get the keys to the targets
		if scope == 'global':
			# Global scope has no friends
			if args:
				raise CommandError(
					cmd = self,
					msg = "Arguments are not allowed at the global scope.",
				)

			scope_mappings.append(
				ScopeMapping(scope, None, None, None, None)
			)

		elif scope == 'appliance':
			# Piggy-back to resolve the appliance names
			names = self.getApplianceNames(args)

			# Now we have to convert the names to the primary keys
			for appliance_id in flatten(self.db.select(
				'id from appliances where name in %s', (names,)
			)):
				scope_mappings.append(
					ScopeMapping(scope, appliance_id, None, None, None)
				)

		elif scope == 'os':
			# Piggy-back to resolve the os names
			names = self.getOSNames(args)

			# Now we have to convert the names to the primary keys
			for os_id in flatten(self.db.select(
				'id from oses where name in %s', (names,)
			)):
				scope_mappings.append(
					ScopeMapping(scope, None, os_id, None, None)
				)

		elif scope == 'environment':
			# Piggy-back to resolve the environment names
			names = self.getEnvironmentNames(args)

			if names:

				# Now we have to convert the names to the primary keys
				for environment_id in flatten(self.db.select(
					'id from environments where name in %s', (names,)
				)):
					scope_mappings.append(
						ScopeMapping(scope, None, None, environment_id, None)
					)

		elif scope == 'host':
			# Piggy-back to resolve the host names
			names = self.getHostnames(args)
			if not names:
				raise ArgRequired(self, 'host')

			# Now we have to convert the names to the primary keys
			for node_id in flatten(self.db.select(
				'id from nodes where name in %s', (names,)
			)):
				scope_mappings.append(
					ScopeMapping(scope, None, None, None, node_id)
				)

		else:
			raise ParamError(self, 'scope', 'is not valid')

		return scope_mappings


class DocStringHandler(handler.ContentHandler,
	handler.DTDHandler,
	handler.EntityResolver,
	handler.ErrorHandler):

	def __init__(self, name='', users=[]):
		handler.ContentHandler.__init__(self)
		self.text			= ''
		self.name			= name
		self.users			= users
		self.section			= {}
		self.section['description']	= ''
		self.section['optarg']		= []
		self.section['reqarg']		= []
		self.section['optparam']	= []
		self.section['reqparam']	= []
		self.section['example']		= []
		self.section['related']		= []
		self.parser = make_parser()
		self.parser.setContentHandler(self)

	def getDocbookText(self):
		raise CommandError(self, '"docbook" no longer supported - use "markdown"')

	def getUsageText(self, colors=None):
		if colors:
			bold   = colors['bold']['code']
			unbold = colors['reset']['code']
		else:
			bold   = ''
			unbold = ''

		s = ''
		for (name, type, rep, txt) in self.section['reqarg']:
			if rep:
				dots = ' ...'
			else:
				dots = ''
			s += '{%s%s%s%s} ' % (bold, name, unbold, dots)

		for (name, type, rep, txt) in self.section['optarg']:
			if rep:
				dots = ' ...'
			else:
				dots = ''
			s += '[%s%s%s%s] ' % (bold, name, unbold, dots)

		for (name, type, rep, txt) in self.section['reqparam']:
			if rep:
				dots = ' ...'
			else:
				dots = ''
			s += '{%s%s%s=%s%s} ' % (bold, name, unbold, type, dots)

		for (name, type, rep, txt) in self.section['optparam']:
			if rep:
				dots = ' ...'
			else:
				dots = ''
			s += '[%s%s%s=%s%s] ' % (bold, name, unbold, type, dots)

		if s and s[-1] == ' ':
			return s[:-1]
		else:
			return s

	def getPlainText(self, colors=None):
		if 'root' in self.users:
			prompt = '#'
		else:
			prompt = '$'

		if colors:
			bold   = colors['bold']['code']
			unbold = colors['reset']['code']
		else:
			bold   = ''
			unbold = ''

		s  = ''
		s += 'stack %s %s' % (self.name, self.getUsageText(colors))
		s += '\n\n%sDescription%s\n' % (bold, unbold)
		s += self.section['description']
		if self.section['reqarg'] or self.section['optarg']:
			s += '\n%sArguments%s\n\n' % (bold, unbold)

			for (name, type, rep, txt) in self.section['reqarg']:
				if rep:
					dots = ' ...'
				else:
					dots = ''
				s += '\t{%s%s%s%s}\n%s\n' % (bold, name, unbold, dots, txt)

			for (name, type, rep, txt) in self.section['optarg']:
				if rep:
					dots = ' ...'
				else:
					dots = ''
				s += '\t[%s%s%s%s]\n%s\n' % (bold, name, unbold, dots, txt)

		if self.section['reqparam'] or self.section['optparam']:
			s += '\n%sParameters%s\n\n' % (bold, unbold)

			for (name, type, rep, txt) in self.section['reqparam']:
				if rep:
					dots = ' ...'
				else:
					dots = ''
				s += '\t{%s%s%s=%s%s}\n%s\n' % (bold, name, unbold, type, dots, txt)

			for (name, type, rep, txt) in self.section['optparam']:
				if rep:
					dots = ' ...'
				else:
					dots = ''
				s += '\t[%s%s%s=%s%s]\n%s\n' % (bold, name, unbold, type, dots, txt)

		if self.section['example']:
			s += '\n%sExamples%s\n\n' % (bold, unbold)
			for (cmd, txt) in self.section['example']:
				s += '\t%s stack %s\n' % (prompt, cmd)
				s += '%s\n' % txt

		if self.section['related']:
			s += '\n%sRelated Commands%s\n\n' % (bold, unbold)
			for related in self.section['related']:
				s += '\tstack %s\n' % related

		return s

	def getParsedText(self):
		return '%s' % self.section

	def getMarkDown(self):
		s = '## %s\n\n' % self.name
		s = s + '### Usage\n\n'
		cmd = "stack %s %s" % (self.name, self.getUsageText().strip())
		s = s + '`%s`\n\n' % cmd.strip()

		if self.section['description']:
			s = s + '### Description\n\n'
			m = self.section['description'].split('\n')
			desc = '\n'.join(m)
			s = s + desc + '\n\n'

		if self.section['reqarg'] or self.section['optarg']:
			s = s + '### Arguments\n\n'

			for (name, type, rep, txt) in self.section['reqarg']:
				s += '* `[%s]`\n' % name

			for (name, type, rep, txt) in self.section['optarg']:
				s += '* `{%s}`\n' % name

			s += '\n   %s\n\n' % txt.strip()
			s = s + '\n'

		if self.section['reqparam'] or self.section['optparam']:
			s = s + '### Parameters\n'

			for (name, type, rep, txt) in self.section['reqparam']:
				s += '* `[%s=%s]`\n' % (name, type)

			for (name, type, rep, txt) in self.section['optparam']:
				s += '* `{%s=%s}`\n' % (name, type)

			s += '\n   %s\n' % txt.strip()
			s = s + '\n'

		if 'example' in self.section and self.section['example']:
			s = s + '### Examples\n\n'
			for (cmd, txt) in self.section['example']:
				s += '* `stack %s`\n' % cmd.strip()
				if txt:
					s += '\n   %s\n' % txt.strip()
				s += '\n'
			s = s + '\n'

		if 'related' in self.section and self.section['related']:
			s = s + '### Related\n'
			for related in self.section['related']:
				r = '-'.join(related.split()).strip()
				s += '[%s](%s)\n\n' % (related, r)

		s = s + '\n'
		return s

	def startElement(self, name, attrs):
		if not self.section['description']:
			self.section['description'] = self.text

		self.key  = None
		self.text = ''

		if name in ['arg', 'param']:
			type = attrs.get('type')
			if not type:
				type = 'string'

			try:
				optional = int(attrs.get('optional'))
			except:
				if name == 'arg':
					optional = 0
				if name == 'param':
					optional = 1

			try:
				repeat = int(attrs.get('repeat'))
			except:
				repeat = 0

			name = attrs.get('name')
			self.key = (name, type, optional, repeat)
		elif name == 'example':
			self.key = attrs.get('cmd')

	def endElement(self, tag):
		if tag == 'docstring':
			# we are done so sort the param and related lists
			self.section['reqparam'].sort()
			self.section['optparam'].sort()
			self.section['related'].sort()

		elif tag == 'arg':
			name, type, optional, repeat = self.key
			if optional:
				self.section['optarg'].append((name, type, repeat, self.text))
			else:
				self.section['reqarg'].append((name, type, repeat, self.text))

		elif tag == 'param':
			name, type, optional, repeat = self.key
			if optional:
				self.section['optparam'].append((name, type, repeat, self.text))
			else:
				self.section['reqparam'].append((name, type, repeat, self.text))

		elif tag == 'example':
			self.section['example'].append((self.key, self.text))

		else:
			if tag in self.section:
				self.section[tag].append(self.text)

	def characters(self, s):
		self.text += s


class DatabaseConnection:
	"""
	Wrapper class for all database access.  The methods are based on
	those provided from the pymysql library and some other Stack
	specific methods are added.  All StackCommands own an instance of
	this object (self.db).
	"""

	cache = {}
	_lookup_hostname_cache = {}

	def _lookup_hostname(self, hostname):
		"""
		Looks up a hostname in a case-insenstive manner to get how it is
		formarted in the DB, allowing MySQL LIKE patterns, and using the
		DatabaseConnection cache when possible.

		Returns None when the hostname doesn't exist.
		"""

		# See if we need to do MySQL LIKE
		if '%' in hostname or '_' in hostname:
			rows = self.select('name FROM nodes WHERE name LIKE %s', (hostname,))
			if rows:
				return rows[0][0]
		elif not self.caching:
			# If we aren't caching, just do a straight lookup
			rows = self.select('name FROM nodes WHERE name = %s', (hostname,))
			if rows:
				return rows[0][0]
		else:
			# Build the cache if needed
			if not DatabaseConnection._lookup_hostname_cache:
				DatabaseConnection._lookup_hostname_cache = {
					name.lower(): name
					for name in flatten(self.select('name FROM nodes'))
				}

			# Return the hostname if it was in the database
			if hostname.lower() in DatabaseConnection._lookup_hostname_cache:
				return DatabaseConnection._lookup_hostname_cache[hostname.lower()]

		# No match
		return None

	def __init__(self, db, *, caching=True):
		# self.database : object returned from orginal connect call
		# self.link	: database cursor used by everyone else
		if db:
			self.database = db
			self.name     = db.db.decode() # name of the database
			self.link     = db.cursor()
		else:
			self.database = None
			self.name     = None
			self.link     = None

		# Setup the global cache, new DatabaseConnections will all use
		# this cache. The envinorment variable STACKCACHE can be used
		# to override the optional CACHING arg.
		#
		# Note the cache is shared but the decision to cache is not.
		#
		# Each database has a unique cache, this way table names don't
		# need to be unique. Currently we use only one connection, but
		# that may change (thought about it for the shadow database)
		# hence the code.

		if self.name not in DatabaseConnection.cache:
			DatabaseConnection.cache[self.name] = {}

		if os.environ.get('STACKCACHE'):
			self.caching = str2bool(os.environ.get('STACKCACHE'))
		else:
			self.caching = caching

	def enableCache(self):
		self.caching = True

	def disableCache(self):
		self.caching = False
		self.clearCache()

	def clearCache(self):
		Debug('clearing cache of %d selects' % len(DatabaseConnection.cache[self.name]))
		DatabaseConnection.cache[self.name] = {}
		DatabaseConnection._lookup_hostname_cache = {}

	def count(self, command, args=None ):
		"""
		Return a count of the number of matching items in the database.
		The command query should start with the column in parentheses you
		wish to count.

		The return value will either be an int or None if something
		unexpected happened.

		Example: count('(ID) from subnets where name=%s', (name,))
		"""

		# Run our select count
		rows = self.select(f'count{command.strip()}', args)

		# We should always get a single row back
		if len(rows) != 1:
			return None

		return rows[0][0]

	def select(self, command, args=None, prepend_select=True):
		if not self.link:
			return []

		rows = []

		m = hashlib.md5()
		m.update(command.strip().encode('utf-8'))
		if args:
			m.update(' '.join(str(arg) for arg in args).encode('utf-8'))
		k = m.hexdigest()

		if k in DatabaseConnection.cache[self.name]:
			Debug('select %s' % k)
			rows = DatabaseConnection.cache[self.name][k]
		else:
			if prepend_select:
				command = f'select {command}'

			try:
				self.execute(command, args)
				rows = self.fetchall()
			except OperationalError:
				Debug('SQL ERROR: %s' % self.link.mogrify(command, args))
				# Permission error return the empty set
				# Syntax errors throw exceptions
				rows = []

			if self.caching:
				DatabaseConnection.cache[self.name][k] = rows
		return rows

	def execute(self, command, args=None, many=False):
		"""Executes the provided SQL command with the provided args.

		If many is True, this will use executemany instead of execute to perform the command.
		"""
		command = command.strip()

		if not command.lower().startswith('select'):
			self.clearCache()

		if self.link:
			# pick the executor to use
			if many:
				executor = self.link.executemany
			else:
				executor = self.link.execute

			try:
				t0 = time.time()
				result = executor(command, args)
				t1 = time.time()
			except ProgrammingError:
				# mogrify doesn't understand the executemany args, so we have to do some more work.
				if many:
					error = '\n'.join((self.link.mogrify(command, arg) for arg in args))
					Debug(f'SQL ERROR: {error}')
				else:
					Debug(f'SQL ERROR: {self.link.mogrify(command, args)}')

				raise ProgrammingError

			# Only spend cycles on mogrify if we are in debug mode
			if stack.commands._debug:
				# mogrify doesn't understand the executemany args, so we have to do some more work.
				if many:
					commands = '\n'.join((self.link.mogrify(command, arg) for arg in args))
					Debug('SQL EX: %.4d rows in %.3fs <- %s' % (result, (t1 - t0), commands))
				else:
					Debug('SQL EX: %.4d rows in %.3fs <- %s' % (result, (t1 - t0), self.link.mogrify(command, args)))

			return result

		return None

	def fetchone(self):
		if self.link:
			row = self.link.fetchone()
			# Debug('SQL F1: %s' % row.__repr__())
			return row
		return None

	def fetchall(self):
		if self.link:
			rows = self.link.fetchall()
			# for row in rows:
			# 	Debug('SQL F*: %s' % row.__repr__())
			return rows
		return None

	def getHostOS(self, host):
		"""
		Return the OS name for the given host.
		"""

		for (name, osname) in self.select("""
			n.name, o.name from boxes b, nodes n, oses o
			where n.box=b.id and b.os=o.id
		"""):
			if name == host:
				return osname
		return None

	def getHostAppliance(self, host):
		"""
		Returns the appliance for a given host.
		"""

		for (name, appliance) in self.select("""
			n.name, a.name from nodes n, appliances a
			where n.appliance=a.id
		"""):
			if name == host:
				return appliance
		return None

	def getHostEnvironment(self, host):
		"""
		Returns the environment for a given host.
		"""

		for (name, environment) in self.select("""
			n.name, e.name from nodes n, environments e
			where n.environment=e.id
		"""):
			if name == host:
				return environment
		return None

	def getNodeName(self, hostname, subnet=None):
		if not subnet:
			lookup = self._lookup_hostname(hostname)
			if lookup:
				hostname = lookup

			return hostname

		result = None

		for (netname, zone) in self.select("""
			net.name, s.zone from nodes n, networks net, subnets s
			where n.name like %s and s.name like %s
			and net.node = n.id and net.subnet = s.id
		""", (hostname, subnet)):
			# If interface exists, but name is not set
			# infer name from nodes table, and append
			# dns zone
			if not netname:
				netname = hostname
			if zone:
				result = '%s.%s' % (netname, zone)
			else:
				result = netname

		return result

	def getHostname(self, hostname=None, subnet=None):
		"""
		Returns the name of the given host as referred to in
		the database.  This is used to normalize a hostname before
		using it for any database queries.
		"""

		# Look for the hostname in the database before trying to reverse
		# lookup the IP address and map that to the name in the nodes
		# table. This should speed up the installer w/ the restore pallet.

		if hostname and self.link:
			if self._lookup_hostname(hostname):
				return self.getNodeName(hostname, subnet)

		if not hostname:
			hostname = socket.gethostname()

			if hostname == 'localhost':
				if self.link:
					return ''
				else:
					return 'localhost'
		try:
			# Do a reverse lookup to get the IP address. Then do a
			# forward lookup to verify the IP address is in DNS. This is
			# done to catch evil DNS servers (timewarner) that have a
			# catchall address. We've had several users complain about
			# this one. Had to be at home to see it.
			#
			# If the resolved address is the same as the hostname then
			# this function was called with an ip address, so we don't
			# need the reverse lookup.
			#
			# For truly evil DNS (OpenDNS) that have catchall servers
			# that are in DNS we make sure the hostname matches the
			# primary or alias of the forward lookup Throw an Except, if
			# the forward failed an exception was already thrown.

			addr = socket.gethostbyname(hostname)
			if not addr == hostname:
				(name, aliases, addrs) = socket.gethostbyaddr(addr)
				if hostname != name and hostname not in aliases:
					raise NameError

		except:
			if hostname == 'localhost':
				addr = '127.0.0.1'
			else:
				addr = None

		if not addr:
			if self.link:
				if self._lookup_hostname(hostname):
					return self.getNodeName(hostname, subnet)

				# See if this is a MAC address
				self.link.execute("""
					select nodes.name from networks,nodes
					where nodes.id=networks.node and networks.mac=%s
				""", (hostname,))

				try:
					hostname, = self.link.fetchone()
					return self.getNodeName(hostname, subnet)
				except:
					pass

				# See if this is a FQDN. If it is FQDN,
				# break it into name and domain.
				n = hostname.split('.')
				if len(n) > 1:
					name = n[0]
					domain = '.'.join(n[1:])

					self.link.execute("""
						select n.name from nodes n, networks nt, subnets s
						where nt.subnet=s.id and nt.node=n.id
						and s.zone=%s and (nt.name=%s or n.name=%s)
					""", (domain, name, name))

					try:
						hostname, = self.link.fetchone()
						return self.getNodeName(hostname, subnet)
					except:
						pass

				# Check if the hostname is a basename and the FQDN is
				# in /etc/hosts but not actually registered with DNS.
				# To do this we need lookup the DNS search domains and
				# then do a lookup in each domain. The DNS lookup will
				# fail (already has) but we might find an entry in the
				# /etc/hosts file.
				#
				# All this to handle the case when the user lies and gives
				# a FQDN that does not really exist. Still a common case.

				try:
					with open('/etc/resolv.conf', 'r') as f:
						domains = []
						for line in f.readlines():
							tokens = line[:-1].split()
							if len(tokens) == 0:
								continue

							if tokens[0] == 'search':
								domains = tokens[1:]

					for domain in domains:
						try:
							name = '%s.%s' % (hostname, domain)
							addr = socket.gethostbyname(name)
							if addr:
								return self.getHostname(name)
						except:
							pass
				except (OSError, IOError):
					pass

				# HostArgumentProcessor has changed handling of
				# appliances (and others) as hostnames. So do some work
				# here to point the user to the new syntax.
				message = None
				if self.count('(id) from appliances where name=%s', (hostname,)):
					message = f'use "a:{hostname}" for {hostname} appliances'
				elif self.count('(id) from environments where name=%s', (hostname,)):
					message = f'use "e:{hostname}" for hosts in the {hostname} environment'
				elif self.count('(id) from oses where name=%s', (hostname,)):
					message = f'use "o:{hostname}" for {hostname} hosts'
				elif self.count('(id) from boxes where name=%s', (hostname,)):
					message = f'use "b:{hostname}" for hosts using the {hostname} box'
				elif self.count('(id) from groups where name=%s', (hostname,)):
					message = f'use "g:{hostname}" for host in the {hostname} group'
				elif hostname.find('rack') == 0:
					message = f'use "r:{hostname}" for hosts in {hostname}'

				if message:
					raise CommandError(self, message)
				raise CommandError(self, f'cannot resolve host "{hostname}"')

		if addr == '127.0.0.1': # allow localhost to be valid
			if self.link:
				return self.getHostname(subnet=subnet)
			else:
				return 'localhost'

		if self.link:
			# Look up the IP address in the networks table to find the
			# hostname (nodes table) of the node.
			#
			# If the IP address is not found also see if the hostname is
			# in the networks table. This last check handles the case
			# where DNS is correct but the IP address used is different.

			rows = self.link.execute("""
				select nodes.name from networks,nodes
				where nodes.id=networks.node and ip=%s
			""", (addr,))

			if not rows:
				rows = self.link.execute("""
					select nodes.name from networks,nodes
					where nodes.id=networks.node and networks.name=%s
				""", (hostname,))

				if not rows:
					raise CommandError(self, f'host "{hostname}" is not in cluster')

			hostname, = self.link.fetchone()

		return self.getNodeName(hostname, subnet)


class Command:
	"""
	Base class for all Stack commands the general command line
	form is as follows:

		stack ACTION COMPONENT OBJECT [ <ARGNAME ARGS> ... ]

		ACTION(s):
			add
			create
			list
			load
			sync
	"""

	MustBeRoot = 1

	def __init__(self, database, *, debug=None):
		"""
		Creates a DatabaseConnection for the StackCommand to use.
		This is called for all commands, including those that do not
		require a database connection.
		"""

		if debug is not None:
			stack.commands._debug = debug

		self.db = DatabaseConnection(database)

		self.text  = []
		self.bytes = []

		self._exec = stack.util._exec

		self.output = []

		self.arch = os.uname()[4]
		if self.arch in ['i386', 'i486', 'i586', 'i686']:
			self.arch = 'i386'
		elif self.arch in ['armv7l']:
			self.arch = 'armv7hl'

		if os.path.exists('/etc/centos-release') or os.path.exists('/etc/redhat-release'):
			self.os = 'redhat'
		elif os.path.exists('/etc/SuSE-release'):
			self.os = 'sles'
		else:
			self.os = os.uname()[0].lower()
			if self.os == 'linux':
				self.os = 'redhat'

		self._args   = None
		self._params = None

		self.rc = None # return code
		self.level = 0

		# List of loaded implementations.
		self.impl_list = {}

		# Figure out the width of the terminal
		self.width = 0
		if sys.stdout.isatty():
			try:
				c, r = os.get_terminal_size()
				self.width = int(c)
			except:
				pass

		# Look up terminal colors safely using tput, uncolored if this fails.
		self.colors = {
			'bold': { 'tput': 'bold', 'code': '' },
			'reset': { 'tput': 'sgr0', 'code': '' },
			'beginline': { 'tput': 'smul', 'code': ''},
			'endline': { 'tput': 'rmul', 'code': ''}
		}

		if sys.stdout.isatty() and False:
			# TODO(p3) - figure out why we aren't capturing the tput code
			# correctly.  We get data but not the full escape seq
			for key in self.colors.keys():
				c = 'tput %s' % self.colors[key]['tput']
				try:
					p = subprocess.Popen(c.split(), stdout=subprocess.PIPE)
				except:
					continue

				(o, e) = p.communicate()
				if p.returncode == 0:
					self.colors[key]['code'] = o

	def graphql(self, query_string, variables = None):
		"""
		"""
		# TODO:  Clean this up
		import requests
		headers = { "x-hasura-admin-secret": "myadminsecretkey"}
		# Requires the http server to be running
		url = 'http://localhost:8081/v1/graphql'

		if not variables:
			variables = {}

		response = requests.post(url, headers=headers, json={"query":query_string,"variables":variables}).json()

		if "errors" in response:
			raise Exception(response['errors'][0]['message'])

		return response['data']

	def fillParams(self, names, params=None):
		"""
		Returns a list of variables with either default values of the
		values in the PARAMS dictionary.

		NAMES - list of (KEY, DEFAULT) tuples.
			KEY - key name of PARAMS dictionary
			DEFAULT - default value if key in not in dict
		PARAMS - optional dictionary
		REQUIRED - optional boolean (True means param is required)

		For example:

		(svc, comp) = self.fillParams(
			('service', None),
			('component', None))

		Can also be written as:

		(svc, comp) = self.fillParams(('service',), ('component', ))
		"""

		# make sure names is a list or tuple
		if not type(names) in [type([]), type(())]:
			names = [names]

		# for each element in the names list make sure it is also
		# a tuple.  If the second element (default value) is missing
		# use None.  If the third element is missing assume the
		# parameter is not required.

		pdlist = []
		for e in names:
			if type(e) in [type([]), type(())]:
				if len(e) == 3:
					tuple = ( e[0], e[1], e[2] )
				elif len(e) == 2:
					tuple = ( e[0], e[1], False )
				elif len(e) == 1:
					tuple = ( e[0], None, False )
				else:
					assert len(e) in [1, 2, 3]
			else:
				tuple = ( e[0], None, False )
			pdlist.append(tuple)

		if not params:
			params = self._params

		list = []
		for (key, default, required) in pdlist:
			if key in params:
				list.append(params[key])
			else:
				if required:
					raise ParamRequired(self, key)
				list.append(default)

		return list

	def call(self, command, args=[]):
		"""
		Similar to the command method but uses the output-format=binary
		to run a command and return a list of dictionary rows.
		"""
		# Do a copy of the args list
		a = args[:]
		a.append('output-format=binary')
		s = self.command(command, a)
		if s:
			return marshal.loads(s)

		return []

	def notify(self, message):
		print(f'{_logPrefix}{message}', file = sys.stderr, flush = True)

	def command(self, command, args=[]):
		"""
		Import and run a Stack command. Returns and output string.
		"""

		modpath = 'stack.commands.%s' % command
		__import__(modpath)
		mod = eval(modpath)

		try:
			o = getattr(mod, 'Command')(self.db.database)
			name = ' '.join(command.split('.'))
		except AttributeError:
			return ''

		# Call the command and store the return code in the
		# class member self.rc so the caller can check
		# the return code.  The actual text is what we return.

		try:
			self.rc = o.runWrapper(name, args, self.level + 1)
		except CommandError as e:
			# We need to catch any CommandError, point it to the calling cmd,
			# and then re-raise it so it will have the correct usage message
			e.cmd = self
			raise e

		return o.getText()

	def loadPlugins(self):
		dict	= {}
		graph	= stack.graph.Graph()

		loadedModules = []
		dir = eval('%s.__path__[0]' % self.__module__)
		for file in os.listdir(dir):
			if file.split('_')[0] != 'plugin':
				continue

			# Find either the .py or .pyc but only load each
			# module once.	This also plugins to be compiled
			# and does not require source code releases.

			if os.path.splitext(file)[1] not in ['.py', '.pyc']:
				continue

			module = '%s.%s' % (self.__module__, os.path.splitext(file)[0])
			if module in loadedModules:
				continue

			loadedModules.append(module)

			__import__(module)
			module = eval(module)
			try:
				o = getattr(module, 'Plugin')(self)
			except AttributeError:
				continue

			# All nodes point to TAIL. This insures a fullyconnected
			# graph, otherwise partial ordering will fail.

			if graph.hasNode(o.provides()):
				plugin = graph.getNode(o.provides())
			else:
				plugin = stack.graph.Node(o.provides())
			dict[plugin] = o

			if graph.hasNode('TAIL'):
				tail = graph.getNode('TAIL')
			else:
				tail = stack.graph.Node('TAIL')
			graph.addEdge(stack.graph.Edge(plugin, tail))

			for pre in o.precedes():
				if graph.hasNode(pre):
					tail = graph.getNode(pre)
				else:
					tail = stack.graph.Node(pre)
				graph.addEdge(stack.graph.Edge(plugin, tail))

			for req in o.requires():
				if graph.hasNode(req):
					head = graph.getNode(req)
				else:
					head = stack.graph.Node(req)
				graph.addEdge(stack.graph.Edge(head, plugin))

		list = []
		for node in PluginOrderIterator(graph).run():
			if node in dict:
				list.append(dict[node])

		return list

	def runPlugins(self, args='', plugins=None):
		if not plugins:
			plugins = self.loadPlugins()

		results = []
		for plugin in plugins:
			Log('run %s' % plugin)
			retval = plugin.run(args)

			if retval is not None:
				results.append((plugin.provides(), retval))

		return results

	def loadImplementation(self, name=None):
		dir = eval('%s.__path__[0]' % self.__module__)
		for file in os.listdir(dir):
			base, ext = os.path.splitext(file)

			if not base.startswith('imp_'):
				continue

			if name:
				if base != 'imp_%s' % name:
					continue

			# Find either the .py or .pyc but only load each
			# module once.	This allows plugins to be compiled
			# and does not require source code releases.

			if ext not in ['.py', '.pyc']:
				continue

			module = '%s.%s' % (self.__module__, base)

			__import__(module)
			module = eval(module)
			try:
				o = getattr(module, 'Implementation')(self)
				n = re.sub('^imp_', '', base)
				self.impl_list[n] = o
			except AttributeError:
				continue

	def runImplementation(self, name, args=None):
		# Check to see if implementation list has named implementation.
		# If not, try to load named implementation.
		if name not in self.impl_list:
			self.loadImplementation(name)

		# If the named implementation was loaded, return the output
		# from running the implementation.
		if name in self.impl_list:
			return self.impl_list[name].run(args)

	def run_implementations_parallel(self, implementation_mapping, display_progress = False):
		"""Runs each implementation in its own thread, passing it the mapped arguments.

		The implementation_mapping parameter is expected to be a dictionary where the keys are
		implementation names and the values are the arguments to call the implementation with.

		The display_progress parameter controls whether a spinner is displayed to keep a concerned
		observer assured that the process isn't dead. This defaults to False.

		The results are returned as a dictionary where the keys are the implementation names
		and the values are either namedtuples with the attributes "result" and "exception", or
		None if the implementation could not be loaded. If an exception was raised in the
		implementation thread, result will be None and the exception will be set to the
		exception raised. Otherwise, exception will be None and result will be set to the
		result that was returned.
		"""
		# load all the implementations if they aren't already loaded
		for imp_name in implementation_mapping:
			if imp_name not in self.impl_list:
				self.loadImplementation(imp_name)

		# only run the ones that are loaded
		imps_to_run = {
			imp_name: args for imp_name, args in implementation_mapping.items()
			if imp_name in self.impl_list
		}
		# set results to None for the implementations we couldn't load
		results_by_imp = {
			imp_name: None for imp_name in implementation_mapping
			if imp_name not in self.impl_list
		}
		with ThreadPoolExecutor(thread_name_prefix = 'run_imp_parallel') as executor:
			# submit each implementation to be run in a thread
			futures_by_imp = {
				imp: executor.submit(
					lambda name, args: self.impl_list[name].run(args),
					name = imp,
					args = args,
				)
				for imp, args in imps_to_run.items()
			}
			if display_progress and futures_by_imp:
				# setup a output spinner
				spinner = cycle('\\|/-')
				# try to evenly divide the progress over 100-ish characters, or
				# just print out one character per future completed if the division
				# rounds to 0.
				chunk_size = round(100 / len(futures_by_imp)) + 1
				futures_done = 0
				# use a 3 second timer to decide if we need to start the spinner
				# we use a no op lambda because we only care about timer expiration
				timer = threading.Timer(3, lambda: ())
				timer.start()
				while not all(future.done() for future in futures_by_imp.values()):
					if not timer.is_alive():
						new_futures_done = len([future for future in futures_by_imp.values() if future.done()])
						# print out a number of chunks of *s equal to the number of new futures done.
						if new_futures_done > futures_done:
							sys.stdout.write('*' * chunk_size * (new_futures_done - futures_done))
							futures_done = new_futures_done

						sys.stdout.write(next(spinner))
						sys.stdout.flush()
						sys.stdout.write('\b')

					# don't peg the cpu you fool
					time.sleep(0.25)

				# finalize the output with a newline and flush the stream.
				timer.cancel()
				print(flush = True)

		# Gather the results from each implementation run and collect them by name.
		# This will also save the exception if one was raised.
		for imp, future in futures_by_imp.items():
			results_by_imp[imp] = namedtuple('ParallelImpResults', ('result', 'exception'))(
				result = future.result() if future.exception() is None else None,
				exception = future.exception(),
			)

		return results_by_imp

	def isRootUser(self):
		"""
		Returns TRUE if running as the root account.
		"""

		if os.geteuid() == 0:
			return 1
		else:
			return 0

	def isApacheUser(self):
		"""
		Returns TRUE if running as the apache account.
		"""

		try:
			if os.geteuid() == pwd.getpwnam('apache')[3]:
				return 1
		except:
			pass
		return 0

	def str2bool(self, s):
		return str2bool(s)

	def bool2str(self, b):
		return bool2str(b)

	def strWordWrap(self, line, indent=''):
		if 'COLUMNS' in os.environ:
			cols = os.environ['COLUMNS']
		else:
			cols = 80

		l = 0
		s = ''
		for word in line.split(' '):
			if l + len(word) < cols:
				s += '%s ' % word
				l += len(word) + 1 # space
			else:
				s += '\n%s%s ' % (indent, word)
				l += len(indent) + len(word) + 1 # space
		return s

	def clearText(self):
		"""
		Reset the output text buffer.
		"""

		self.text  = []
		self.bytes = []

	def addText(self, s):
		"""
		Append a string to the output text buffer.
		"""

		if s:
			if isinstance(s, str):
				self.text.append(s)
			else:
				self.bytes.append(s)

	def getText(self):
		"""
		Returns the output text buffer.
		"""

		if self.text:
			return ''.join(self.text)

		if self.bytes:
			return b''.join(self.bytes)

		return None


	def reportFile(self, file, contents, *, perms=None, host=None):
		if file[0] == os.sep:
			file = file[1:]
		attr = '_'.join(os.path.split(file))

		if host:
			override = self.getHostAttr(host, attr)
		else:
			override = self.getAttr(attr)
		if override is not None:
			contents = override

		text = []
		text.append('<stack:file stack:name="/etc/resolv.conf">')
		text.append(contents)
		text.append('</stack:file>')
		return '\n'.join(text)

	def beginOutput(self):
		"""
		Reset the output list buffer.
		"""
		self.output = []

	def addOutput(self, owner, vals):
		"""
		Append a list to the output list buffer.
		"""

		# VALS can be a list, tuple, or primitive type.
		out = ['%s' % owner]

		if isinstance(vals, type([])):
			out.extend(vals)
		elif isinstance(vals, tuple):
			for e in vals:
				out.append(e)
		else:
			out.append(vals)

		self.output.append(out)

	def endOutput(self, header=[], padChar='-', trimOwner=False, trimHeader=False):
		"""
		Pretty prints the output list buffer.
		"""

		# Handle the simple case of no output, and bail out
		# early.  We do this to avoid printing out nothing
		# but a header w/o any rows.
		if not self.output:
			return

		# The OUTPUT-FORMAT option can change the default from
		# human readable text to something else.  Currently
		# supports:
		#
		# json		- text json
		# python	- text python
		# binary	- marshalled python
		# text		- default (for humans)

		format = self._params.get('output-format')
		if not format:
			format = 'text'

		tokens = format.split(':')
		if len(tokens) == 1:
			format	    = tokens[0]
			format_args = None
		else:
			format	    = tokens[0]
			format_args = tokens[1].lower()

		if format in ['col', 'shell', 'json', 'python', 'binary']:
			if not header: # need to build a generic header
				if len(self.output) > 0:
					rows = len(self.output[0])
				else:
					rows = 0

				header = []
				for i in range(0, rows):
					header.append('col-%d' % i)

			list = []
			for line in self.output:
				dict = {}
				for i in range(0, len(header)):
					if header[i]:
						key = header[i]
						val = line[i]

						if key in dict:
							if not isinstance(dict[key], list):
								dict[key] = [dict[key]]
							dict[key].append(val)
						else:
							dict[key] = val
				list.append(dict)

			if format == 'col':
				for row in list:
					try:
						self.addText('%s\n' % row[format_args])
					except KeyError:
						pass
			elif format == 'shell':
				rows = len(list)
				for i in range(0, rows):
					if rows > 1:
						n = '%d_' % i
					else:
						n = ''

					for k, v in list[i].items():
						self.addText('stack_%s%s="%s"\n' % (n, k, v))

					self.addText('\n')
			elif format == 'python':
				self.addText('%s' % list)
			elif format == 'binary':
				self.addText(marshal.dumps(list))
			else:
				self.addText(json.dumps(list, indent=8))
			return

		if format == 'null':
			return

		# By default always display the owner (col 0), but if
		# all lines have no owner set skip it.
		#
		# If trimOwner=True optimize the output to not display
		# the owner IFF all lines have the same owner.	This
		# looks like grep output across multiple or single
		# files.

		if trimOwner:
			owner = ''
			startOfLine = 1
			for line in self.output:
				if not owner:
					owner = line[0]
				if not owner == line[0]:
					startOfLine = 0
		else:
			startOfLine = 1
			for line in self.output:
				if line[0]:
					startOfLine = 0

		# Add the header to the output and start formatting.  We
		# keep the header optional and separate from the output
		# so the above decision (startOfLine) can be made.

		if header and not trimHeader:
			list = []
			for field in header:
				if field:
					list.append(field.upper())
				else:
					list.append('')

			output = [list]
			output.extend(self.output)
		else:
			output = self.output

		colwidth = []
		for line in output:
			for i in range(0, len(line)):
				if len(colwidth) <= i:
					colwidth.append(0)

				if not isinstance(line[i], str):
					if line[i] is None:
						itemlen = 0
					else:
						itemlen = len(repr(line[i]))
				else:
					itemlen = len(line[i])

				if itemlen > colwidth[i]:
					colwidth[i] = itemlen

		# If we know the output is too long for the terminal
		# switch from table view to a field view that will
		# display nicer (e.g. stack list os boot).
		if self.width and header and startOfLine == 0 and (sum(colwidth) + len(line)) > self.width:
			maxWidth = 0
			for label in output[0]:
				n = len(label)
				if n > maxWidth:
					maxWidth = n

			for line in output[1:]:
				for i in range(0, len(line)):
					if line[i] in [None, 'None']:
						s = ''
					else:
						s = str(line[i])

					if s:
						self.addText('%s%s%s %s\n' % (
							self.colors['bold']['code'],
							output[0][i].ljust(maxWidth),
							self.colors['reset']['code'], s))

				self.addText('\n')
			return

		if header:
			isHeader = True
		else:
			isHeader = False

		o = ''
		for line in output:
			list = []
			for i in range(startOfLine, len(line)):
				if line[i] in [None, 'None']:
					s = ''
				else:
					s = str(line[i])

				# fill "cell" with padChar so it's as long
				# as the longest field/header.
				if padChar != '' and i != len(line) - 1:
					if s:
						o = s.ljust(colwidth[i])
					else:
						o = ''.ljust(colwidth[i], padChar)

				# *BUT* if this is the last column, it might be super
				# long, so only pad it out as long as the header.
				elif padChar != '' and i == len(line) - 1 and not s:
					o = ''.ljust(len(output[0][i]), padChar)
				else:
					o = s

				if isHeader:
					o = '%s%s%s' % (
						self.colors['bold']['code'],
						o,
						self.colors['reset']['code']
					)

				list.append(o)

			self.addText('%s\n' % ' '.join(list))
			isHeader = False

	def usage(self):
		if self.__doc__:
			handler = DocStringHandler()
			parser = make_parser()
			parser.setContentHandler(handler)

			try:
				parser.feed('<docstring>%s</docstring>' %
					self.__doc__)
			except:
				return '-- invalid doc string --'

			return handler.getUsageText(self.colors)
		else:
			return '-- missing doc string --'

	def help(self, command, flags={}):
		if not self.__doc__:
			return

		if self.MustBeRoot:
			users = ['root', 'apache']
		else:
			users = []

		if 'format' in flags:
			format = flags['format'].lower()
		else:
			format = 'plain'

		if format == 'raw':
			i = 1
			for line in self.__doc__.split('\n'):
				self.addText('%d:%s\n' % (i, line))
				i += 1
		else:
			handler = DocStringHandler(command, users)
			parser = make_parser()
			parser.setContentHandler(handler)
			parser.feed('<docstring>%s</docstring>' % self.__doc__)

			if format == 'docbook':
				self.addText(handler.getDocbookText())
			elif format == 'parsed':
				self.addText(handler.getParsedText())
			elif format == 'md':
				self.addText(handler.getMarkDown())
			else:
				self.addText(handler.getPlainText(self.colors))

	def hasAccess(self, name):
		allowed = False
		gid	= os.getgid()
		groups	= os.getgroups()

		if gid not in groups:
			# Installer has no supplemental groups so we need to include
			# the default group. Outside the installer it is already in
			# the supplemental list.
			groups.append(gid)

		rows = self.db.select('command, groupid from access')
		if rows:
			for c, g in rows:
				if g in groups:
					if fnmatch.filter([name], c):
						allowed = True
		else:
			# If the access table does not exist fallback onto the
			# previous MustBeRoot style access control.
			#
			# This is also the case for the installer.

			if self.MustBeRoot:
				if self.isRootUser() or self.isApacheUser():
					allowed = True
			else:
				allowed = True

		return allowed

	def runWrapper(self, name, argv, level=0):
		"""
		Performs various checks and logging on the command before
		the run() method is called.  Derived classes should NOT
		need to override this.
		"""

		username = pwd.getpwuid(os.geteuid())[0]

		self.level = level

		if argv:
			command = '%s %s' % (name, ' '.join(argv))
		else:
			command = name

		global _logPrefix
		_logPrefix = ''
		for i in range(0, self.level):
			_logPrefix += '	       '

		Log('user %s called "%s"' % (username, command))

		# Split the args and flags apart.  Args have no '='
		# with the exception of select statements (special case), and
		# flags have one or more '='.

		dict = {} # flags
		list = [] # arguments

		# Allow ad-hoc groups (e.g. [ rack == 0 ] ) to be split
		# across several arguments, this prevents the need to
		# quote them into a single argument.
		#
		# We only do this when we find an argument and starts with
		# '['.	So the '[' character is safe anywhere else on the
		# command line.	 But if you start an argument with one it
		# need to be closed eventually.

		s = ''
		n = 0
		l = []
		ingroup = False

		for arg in argv:
			if not arg:
				continue

			if arg[0] == '[' and arg[-1] != ']':
				s += '%s' % arg
				n += 1
				if n == 1:
					ingroup = True
			elif arg[0] != '[' and arg[-1] == ']':
				s += '%s' % arg
				n -= 1
				if n <= 0:
					l.append(s)
					ingroup = False
			elif ingroup:
				s += ' %s' % arg
			else:
				l.append(arg)
		argv = l

		# Convert the argument vector into a list of
		# arguments and a dictionary of parameters.
		# A parameter is a key=val string and an
		# argument is anything else.  Parameters can
		# be before, after, or even in between arguments.

		for arg in argv:
			if not arg:
				continue

			if arg.find('where') == 0:
				list.append(arg)
			elif len(arg.split('=', 1)) == 2:
				(key, val) = arg.split('=', 1)
				dict[key] = val
			else:
				list.append(arg)

		if list and list[0] == 'help':
			self.help(name, dict)
		else:
			if not self.hasAccess(name):
				raise CommandError(
					self, f'user "{username}" does not have access "{name}'
				)
			else:
				self._argv   = argv # raw arg list
				self._args   = list # required arguments
				self._params = dict # optional parameters

				rc = self.run(self._params, self._args)

				# if a command does not explicitly return
				# assume it succeeded, otherwise use the
				# actual return code.
				if rc is None:
					return True

				return rc

	def run(self, flags, args):
		"""
		All derived classes should override this method. This method is
		called by the stack command line as the entry point into the
		Command object.

		flags: dictionary of key=value flags
		args: list of string arguments
		"""

		pass

	def getAttr(self, attr):
		return self.getHostAttr('localhost', attr)

	def getHostAttr(self, host, attr):
		for row in self.call('list.host.attr', [host, 'attr=%s' % attr]):
			return row['value']

		return None

	def getHostAttrDict(self, host, attr=None):
		"""
		For `host` return all of its attrs in a dictionary
		return {'host1': {'rack': '0', 'rank': '1', ...}, 'host2': {...}, ...}
		This works because multiple attr's cannot have the same name.
		"""

		if type(host) == type([]):
			params = host
		else:
			params = [host]

		if attr:
			params.append(f'attr={attr}')

		return {
			k: {i['attr']: i['value'] for i in v}
			for k, v in groupby(
				self.call('list.host.attr', params),
				itemgetter('host')
			)
		}


class Module:
	def __init__(self, command):
		self.owner = command
		self.db	   = command.db

	def run(self, args):
		"""
		All derived classes should override this method. This
		is the entry point into the Plugin object.
		"""
		pass


class Implementation(Module):
	"""
	Base class for all Stack command implementations.
	"""
	pass


class Plugin(Module):
	"""
	Base class for all Stack command plug-ins.
	"""

	def provides(self):
		"""
		Returns a unique string to identify the plug-in. All Plugins
		must override this method.
		"""

		return None

	def requires(self):
		"""
		Returns a list of plug-in identifiers that must be run before
		this Plugin. This is optional for all derived classes.
		"""

		return []

	def precedes(self):
		"""
		Returns a list of plug-in identifiers that can only by run after
		this Plugin. This is optional for all derived classes.
		"""

		return []


class PluginOrderIterator(stack.graph.GraphIterator):
	"""
	Iterator for Partial Ordering of Plugins
	"""

	def __init__(self, graph):
		stack.graph.GraphIterator.__init__(self, graph)
		self.nodes = []
		self.time  = 0

	def run(self):
		stack.graph.GraphIterator.run(self)
		list = []
		self.nodes.sort()

		for tm, node in self.nodes:
			list.append(node)

		list.reverse()
		return list

	def visitHandler(self, node, edge):
		stack.graph.GraphIterator.visitHandler(self, node, edge)
		self.time = self.time + 1

	def finishHandler(self, node, edge):
		stack.graph.GraphIterator.finishHandler(self, node, edge)
		self.time = self.time + 1
		self.nodes.append((self.time, node))
