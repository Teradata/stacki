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

import stack.graph
import stack
from stack.cond import EvalCondExpr
from stack.exception import CommandError, ParamRequired, ArgNotFound
from stack.bool import str2bool, bool2str

_logPrefix = ''
_debug     = False



def Log(message, level=syslog.LOG_INFO):
	"""
	Send a message to syslog
	"""
	syslog.syslog(level, '%s%s' % (_logPrefix, message))


def Debug(message, level=syslog.LOG_DEBUG):
	"""If the environment variable STACKDEBUG is set,
	send a message to syslog and stderr."""
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
		
Debug('__init__:commands')

class OSArgumentProcessor:
	"""An Interface class to add the ability to process os arguments."""

	def getOSNames(self, args=None):
		list = []
		if not args:
			args = ['%']		# find all appliances
		for arg in args:
			if arg == 'centos':
				arg = 'redhat'
			for name, in self.db.select(
					"""
					name from oses 
					where name like %s order by name
					""", arg):
				list.append(name)
			if len(list) == 0 and arg == '%':  # empty table is OK
				continue
			if len(list)  < 1:
				raise ArgNotFound(self, arg, 'OS')
		return list

	
class EnvironmentArgumentProcessor:
	"""An Interface class to add the ability to process environment
	arguments."""
		
	def getEnvironmentNames(self, args=None):
		environments = []
		if not args:
			args = [ '%' ]		 # find all appliances
		for arg in args:
			found = False
			for (envName, ) in self.db.select("name from environments where name like '%s'" % arg):
				found = True
				environments.append(envName)
			if not found and arg != '%':
				raise ArgNotFound(self, arg, 'environment')

		return environments


class ApplianceArgumentProcessor:
	"""An Interface class to add the ability to process appliance
	arguments."""
		
	def getApplianceNames(self, args=None):
		"""Returns a list of appliance names from the database.
		For each arg in the ARGS list find all the appliance
		names that match the arg (assume SQL regexp).  If an
		arg does not match anything in the database we raise
		an exception. If the ARGS list is empty return all appliance names.
		"""	
		appliances  = []
		if not args:
			args = [ '%' ]		 # find all appliances
		for arg in args:
			found = False
			for (appName, ) in self.db.select("name from appliances where name like '%s'" % arg):
				found = True
				appliances.append(appName)
			if not found and arg != '%':
				raise ArgNotFound(self, arg, 'appliance')

		return appliances


class BoxArgumentProcessor:
	"""An Interface class to add the ability to process box arguments."""
		
	def getBoxNames(self, args=None):
		"""Returns a list of box names from the database.
		For each arg in the ARGS list find all the box
		names that match the arg (assume SQL regexp).  If an
		arg does not match anything in the database we raise an
		exception.  If the ARGS list is empty return all box names.
		"""
		boxes = []
		if not args:
			args = [ '%' ]		      # find all boxes

		for arg in args:
			found = False
			for (boxName, ) in self.db.select("name from boxes where name like '%s'" % arg):
				found = True
				boxes.append(boxName)
			if not found and arg != '%':
				raise ArgNotFound(self, arg, 'box')

		return boxes

	def getBoxPallets(self, box='default'):
		"""Returns a list of pallets for a box"""

		#
		# make sure 'box' exists
		#
		self.getBoxNames([box])	

		pallets = []

		rows = self.db.select("""r.name, r.version, r.rel,
			r.arch, o.name from rolls r, boxes b,
			stacks s, oses o where b.name = '%s' and
			b.id = s.box and s.roll = r.id and b.os=o.id""" % box)

		for name, version, rel, arch, osname in rows:
			pallets.append((name, version, rel, arch, osname))

		return pallets
		

class NetworkArgumentProcessor:
	"""An Interface class to add the ability to process network (subnet)
	argument."""
	
	def getNetworkNames(self, args=None):
		"""Returns a list of network (subnet) names from the database.
		For each arg in the ARGS list find all the network
		names that match the arg (assume SQL regexp).  If an
		arg does not match anything in the database we raise
		an exception.  If the ARGS list is empty return all network names.
		"""
		networks = []
		if not args:
			args = [ '%' ]		   # find all networks
		for arg in args:
			found = False
			for (netName, ) in self.db.select("name from subnets where name like '%s'" % arg):
				found = True
				networks.append(netName)
# TODO - Release code actually doesn't do this, we should be there might
# be code that relies on this bug. Needs testing before using the below
# code.
#
#			if not found and arg != '%':
#				raise ArgNotFound(self, arg, 'network')

		return networks

	def getNetworkName(self, netid):
		"""Returns a network (subnet) name from the database that
		is associated with the id 'netid'.
		"""
		if not netid:
			return ''

		rows = self.db.execute("""select name from subnets where
			id = %s""" % netid)

		if rows > 0:
			netname, = self.db.fetchone()
		else:
			netname = ''

		return netname

class SwitchArgumentProcessor:
	"""An interface class to add the ability to process switch arguments."""

	def getSwitchNames(self, args=None):
		"""Returns a list of switch names from the database.
		For each arg in the ARGS list find all the switch
		names that match the arg (assume SQL regexp).  If an
		arg does not match anything in the database we raise
		an exception.  If the ARGS list is empty return all network names.
		"""
		switches = []
		if not args:
			args = ['%'] # find all switches
		for arg in args:
			rows = self.db.execute("""
			select name from nodes
			where name like '%s' and
			appliance=(select id from appliances where name='switch')
			""" % arg)

			if rows == 0 and arg == '%': # empty table is OK
				continue
			for name, in self.db.fetchall():
				switches.append(name)

		return switches

	def delSwitchEntries(self, args=None):
		"""Delete foreign key references from switchports"""
		if not args:
			return

		for arg in args:
			row = self.db.execute("""
			delete from switchports
			where switch=(select id from nodes where name='%s')
			""" % arg)

	def getSwitchNetwork(self, switch):
		"""Returns the network the switch's management interface is on.
		"""
		if not switch:
			return ''

		rows = self.db.execute("""
			select subnet from networks where
			node = (select id from nodes where name = '%s')
			""" % switch)

		if rows:
			network, = self.db.fetchone()
		else:
			network = ''

		return network

	def addSwitchHost(self, switch, host, port, interface):
		"""
		Add a host to switch.
		Check if host has an interface on the same network as
		the switch
		"""

		# Get the switch's network
		switch_network = self.db.select("""
			subnet from networks where node=(
				select id from nodes where name='%s'
				)
			""" % switch)

		if not switch_network:
			raise CommandError(self,
				"switch '%s' doesn't have an interface" % switch)

		# Get the interface of the host that is on the same
		# network as the switch

		# If the user entered an interface
		if interface:
			host_interface = self.db.select("""
				id from networks
				where subnet='%s'
				and node=(select id from nodes where name='%s')
				and device='%s'
				""" % (switch_network[0][0],  host, interface))

			if not host_interface:
				raise CommandError(self,
					"Interface '%s' isn't on a network with '%s'"
					% ( interface, switch ))

		# Grab the interface, if there is one, that is on the same network
		# as the switch
		else:
			host_interface = self.db.select("""
				id from networks where subnet='%s' and
				node=(select id from nodes where name='%s')
				""" % (switch_network[0][0],  host))

			if not host_interface:
				raise CommandError(self,
					"host '%s' is not on a network with switch '%s'"
					% ( host, switch ))

		# Check if the port is already managed by the switch
		rows = self.db.select("""
			* from switchports
			where port='%s'
			and switch=(select id from nodes where name='%s')
			""" % (port, switch))

		if rows:
			raise CommandError(self,
				"Switch '%s' is alredy managing a host on port '%s'"
				% (switch, port))

		# if we got here, add the host to be managed switch
		query = """
		insert into switchports
		(interface, switch, port)
		values ('%s',
			(select id from nodes where name = '%s'),
			'%s')
		""" % (host_interface[0][0], switch, port)

		self.db.execute(' '.join(query.split()))

	def delSwitchHost(self, switch, host):
		"""Add a host to switch"""
		query = """
		delete from switchports
		where interface in (
			select id from networks where
			node=(select id from nodes where name='%s') and
			subnet=(select subnet from networks where
				node=(select id from nodes where name='%s'))
			)
		and switch=(select id from nodes where name='%s')
		""" % (host, switch, switch)
		#print(query)
		self.db.execute(' '.join(query.split()))
	def setSwitchHostVlan(self, switch, host, vlan):
		self.db.execute("""
		update switchports
		set vlan=%s
		where host=(select id from nodes where name='%s')
		and switch=(select id from nodes where name='%s')
		""" % (vlan, host, switch))

	def getSwitchesForHosts(self, hosts):
		"""Return switches name for hosts"""
		_switches = []
		for host in hosts:
			_rows = self.db.select("""
			n.name from 
			nodes n, switchports s, networks i where
			s.interface in (select id from networks where node=(select id from nodes where name='%s')) and
			s.switch=n.id
			""" % host)

			for row, in _rows:
				_switches.append(row)

		return set(_switches)

	def getHostsForSwitch(self, switch):
		"""Return a dictionary of hosts that are connected to the switch.
		Each entry will be keyed off of the port since most of the information
		stored by the switch is based off port. 
		"""

		_hosts = {}
		_rows = self.db.select("""
		  n.name, i.device, s.port, i.vlanid, i.mac from
		  nodes n, networks i, switchports s where 
		  s.switch=(select id from nodes where name='%s') and
		  i.id = s.interface and
		  n.id = i.node
		""" % switch)
		for host, interface, port, vlanid, mac in _rows:
			_hosts[str(port)] = {
				  'host': host,
				  'interface': interface,
				  'port': port,
				  'vlan': vlanid,
				  'mac': mac,
				}

		return _hosts
	

class CartArgumentProcessor:
	"""An Interface class to add the ability to process cart arguments."""

	def getCartNames(self, args, params):
	
		carts = []
		if not args:
			args = [ '%' ]		 # find all cart names
		for arg in args:
			found = False
			for (cartName, ) in self.db.select("""
				name from carts where
				name like binary '%s'
				""" % arg):
				found = True
				carts.append(cartName)
			if not found and arg != '%':
				raise ArgNotFound(self, arg, 'cart')

		return carts

	
class RollArgumentProcessor:
	"""An Interface class to add the ability to process pallet arguments."""
	
	def getRollNames(self, args, params):
		"""Returns a list of (name, version, release) tuples from the pallet
		table in the database.	If the PARAMS['version'] is provided
		only pallets of that version are included otherwise no filtering
		on version number is performed.	 If the ARGS list is empty then
		all pallet names are returned.	SQL regexp can be used in 
		both the version parameter and arg list, but must expand to 
		something.
		"""

		if 'version' in params:
			version = params['version']
		else:
			version = '%' # SQL wildcard

		if 'release' in params:
			rel = params['release']
		else:
			rel = '%' # SQL wildcard

		if 'arch' in params:
			arch = params['arch']
		else:
			arch = "%" # SQL wildcard
	
		pallets = []
		if not args:
			args = [ '%' ]	       # find all pallet names
		for arg in args:
			found = False
			for (name, ver, rel) in self.db.select("""
				distinct name, version, rel from rolls where
				name like binary '%s' and 
				version like binary '%s' and 
				rel like binary '%s' and
				arch like binary '%s' 
				""" % (arg, version, rel, arch)):
				found = True
				pallets.append((name, ver, rel))
			if not found and arg != '%':
				raise ArgNotFound(self, arg, 'pallet')
		return pallets


class HostArgumentProcessor:
	"""An Interface class to add the ability to process host arguments."""

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

		rank = sorted((h for h in hosts if h['rank'].isnumeric()), key = ranksort)
		rank += sorted((h for h in hosts if not h['rank'].isnumeric()), key = ranksort)

		rack = sorted((h for h in rank if h['rack'].isnumeric()), key = racksort)
		rack += sorted((h for h in rank if not h['rack'].isnumeric()), key = racksort)

		hosts = []
		for r in rack:
			hosts.append((r['host'],))

		return hosts

	
	def getHostnames(self, names=[], managed_only=False, subnet=None, host_filter=None, order='asc'):
		"""Expands the given list of names to valid cluster hostnames.	A name
		can be:

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

		#
		# list the frontend first
		#
		frontends = self.db.select(
			"""
			n.name from
			nodes n, appliances a where a.name = "frontend"
			and a.id = n.appliance order by rack, rank %s
			""" % order)

		#
		# now get the backend appliances
		#
		rows = self.db.select("""n.name, n.rack, n.rank from
			nodes n, appliances a where a.name != "frontend"
			and a.id = n.appliance""")

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
				hostDict[host] = self.db.getNodeName(host, 
								     subnet)

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

			# ad-hoc group
			
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

			# glob regex hostname

			elif '*' in name or '?' in name or '[' in name:
				for host in fnmatch.filter(hostList, name):
					s = self.db.getHostname(host, subnet)
					hostDict[host] = s
					if host not in explicit:
						explicit[host] = False
					

			# simple hostname
						
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


class PartitionArgumentProcessor:
	"""An Interface class to add the ability to process a partition 
	argument."""
	
	def partsizeCompare(self, x, y):
		xsize = x[0]
		ysize = y[0]

		suffixes = ['KB', 'MB', 'GB', 'TB', 'PB']

		xsuffix = xsize[-2:].upper()
		ysuffix = ysize[-2:].upper()

		try:
			xindex = suffixes.index(xsuffix)
		except:
			xindex = -1

		try:
			yindex = suffixes.index(ysuffix)
		except:
			yindex = -1

		if xindex < yindex:
			return 1
		elif xindex > yindex:
			return -1
		else:
			try:
				xx = float(xsize[:-2])
				yy = float(ysize[:-2])

				if xx < yy:
					return 1
				elif xx > yy:
					return -1
			except:
				pass

		return 0


	def getPartitionsDB(self, host):
		partitions = []

		for (size, mnt, device) in self.db.select("""
			p.partitionsize, p.mountpoint,
			p.device from partitions p, nodes n where
			p.node = n.id and n.name = '%s' order by device
			""" % host):
			
			if mnt in ['', 'swap']:
				continue
			if len(mnt) > 0 and mnt[0] != '/':
				continue
			partitions.append((size, mnt, device))

		return partitions


	def getLargestPartition(self, host, disk=None):
		#
		# get the mountpoint for the largest partition for a host
		#
		maxmnt = None
		sizelist = []

		if not disk:
			sizelist = self.getPartitionsDB(host)
		else:
			for (size, mnt, device) in self.getPartitionsDB(host):
				dev = re.split('[0-9]+$', device)

				if len(dev) <= 1:
					continue 

				if dev[0] != disk:
					continue

				sizelist.append((size, mnt, device))

		if len(sizelist) > 0:
			sizelist.sort(self.partsizeCompare)
			(maxsize, maxmnt, device) = sizelist[0]

		return maxmnt


	def getPartitions(self, hostname='localhost', partition=None):
		#
		# get a list of partitions (mount points), that match
		# the argument 'partition'. 'partition' can be a regular
		# expression
		#
		partitions = []

		if partition:
			host = self.db.getHostname(hostname)
			parts = self.getPartitionsDB(host)
			pattern = re.compile(partition)

			for (size, mnt, device) in parts:
				if pattern.search(mnt):
					partitions.append(mnt)
			
		return partitions


	def getDisks(self, host):
		disks = {}
		disks['boot'] = []
		disks['data'] = []
		bootdisk = None
		alldisks = []

		#
		# first find the boot disk
		#
		for (device, mnt) in self.db.select("""
			p.device, p.mountpoint from
			partitions p, nodes n where p.node = n.id and
			n.name = '%s' order by p.device""" % host):
			
			dev = re.split('[0-9]+$', device)
			disk = dev[0]

			if disk not in alldisks:
				alldisks.append(disk)

			if mnt and mnt == '/':
				bootdisk = disk

		#
		# now put the drives into their correct bins
		#
		for disk in alldisks:
			if disk == bootdisk:
				disktype = 'boot'
			else:
				disktype = 'data'

			if disk not in disks[disktype]:
				disks[disktype].append(disk)
				
		return disks


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
		print('Docbook is no longer a viable format.')
		raise(CommandError(self, 'Use "markdown"'))
		s  = ''
		s += '<section id="stack-%s" xreflabel="%s">\n' % \
			('-'.join(self.name.split(' ')), self.name)
		s += '<title>%s</title>\n' % self.name
		s += '<cmdsynopsis>\n'
		s += '\t<command>stack %s</command>\n' % self.name
		for ((name, type, opt, rep), txt) in self.section['arg']:
			if opt:
				choice = 'opt'
			else:
				choice = 'req'
			if rep:
				repeat = 'repeat'
			else:
				repeat = 'norepeat'
			s += '\t<arg rep="%s" choice="%s">%s</arg>\n' % \
				(repeat, choice, name)
		for ((name, type, opt, rep), txt) in self.section['param']:
			if opt:
				choice = 'opt'
			else:
				choice = 'req'
			if rep:
				repeat = 'repeat'
			else:
				repeat = 'norepeat'
			s += '\t<arg rep="%s" choice="%s">' % (repeat, choice)
			s += '%s=<replaceable>%s</replaceable>' % (name, type)
			s += '</arg>\n'
		s += '</cmdsynopsis>\n'
		s += '<para>\n'
		s += saxutils.escape(self.section['description'])
		s += '\n</para>\n'
		if self.section['arg']:
			s += '<variablelist><title>arguments</title>\n'
			for ((name, type, opt, rep), txt) in \
				self.section['arg']:
				s += '\t<varlistentry>\n'
				if opt:
					term = '<optional>%s</optional>' % name
				else:
					term = name
				s += '\t<term>%s</term>\n' % term
				s += '\t<listitem>\n'
				s += '\t<para>\n'
				s += saxutils.escape(txt)
				s += '\n\t</para>\n'
				s += '\t</listitem>\n'
				s += '\t</varlistentry>\n'
			s += '</variablelist>\n'
		if self.section['param']:
			s += '<variablelist><title>parameters</title>\n'
			for ((name, type, opt, rep), txt) in \
				self.section['param']:
				s += '\t<varlistentry>\n'
				if opt:
					optStart = '<optional>'
					optEnd	 = '</optional>'
				else:
					optStart = ''
					optEnd	 = ''
				key = '%s=' % name
				val = '<replaceable>%s</replaceable>' % type
				s += '\t<term>%s%s%s%s</term>\n' % \
					(optStart, key, val, optEnd)
				s += '\t<listitem>\n'
				s += '\t<para>\n'
				s += saxutils.escape(txt)
				s += '\n\t</para>\n'
				s += '\t</listitem>\n'
				s += '\t</varlistentry>\n'
			s += '</variablelist>\n'
		if self.section['example']:
			s += '<variablelist><title>examples</title>\n'
			for (cmd, txt) in self.section['example']:
				s += '\t<varlistentry>\n'
				s += '\t<term>\n'
				if 'root' in self.users:
					s += '# '
				else:
					s += '$ '
				s += 'stack %s' % cmd
				s += '\n\t</term>\n'
				s += '\t<listitem>\n'
				s += '\t<para>\n'
				s += saxutils.escape(txt)
				s += '\n\t</para>\n'
				s += '\t</listitem>\n'
				s += '\t</varlistentry>\n'
			s += '</variablelist>\n'
		if self.section['related']:
			s += '<variablelist><title>related commands</title>\n'
			for related in self.section['related']:
				s += '\t<varlistentry>\n'
				s += '\t<term>'
				s += '<xref linkend="stack-%s">' % \
					'-'.join(related.split(' '))
				s += '</term>\n'
				s += '\t<listitem>\n'
				s += '\t<para>\n'
				s += '\n\t</para>\n'
				s += '\t</listitem>\n'
				s += '\t</varlistentry>\n'
			s += '</variablelist>\n'
		s += '</section>'
		return s

	
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

	"""Wrapper class for all database access.  The methods are based on
	those provided from the pymysql library and some other Stack
	specific methods are added.  All StackCommands own an instance of
	this object (self.db).
	"""

	cache   = {}

	def __init__(self, db, *, caching=True):
		# self.database : object returned from orginal connect call
		# self.link	: database cursor used by everyone else
		if db:
			self.database = db
			self.link     = db.cursor()
		else:
			self.database = None
			self.link     = None

		# Setup the global cache, new DatabaseConnections will all use
		# this cache. The envinorment variable STACKCACHE can be used
		# to override the optional CACHING arg.
		#
		# Note the cache is shared but the decision to cache is not.
		
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
		Debug('clearing cache of %d selects' % len(DatabaseConnection.cache))
		DatabaseConnection.cache = {}

	def select(self, command, args=None):
		if not self.link:
			return []
		
		rows = []
		
		m = hashlib.md5()
		m.update(command.strip().encode('utf-8'))
		if args:
			m.update(' '.join(arg for arg in args).encode('utf-8'))
		k = m.hexdigest()

#		 print 'select', k, command
		if k in DatabaseConnection.cache:
			Debug('select %s' % k)
			rows = DatabaseConnection.cache[k]
#			 print >> sys.stderr, '-\n%s\n%s\n' % (command, rows)
		else:
			try:
				self.execute('select %s' % command, args)
				rows = self.fetchall()
			except (OperationalError, ProgrammingError):
				# Permission error return the empty set
				# Syntax errors throw exceptions
				rows = []
				
			if self.caching:
				DatabaseConnection.cache[k] = rows

		return rows

					
	def execute(self, command, args=None):
		command = command.strip()

		if command.find('select') != 0:
			self.clearCache()
						
		if self.link:
			t0 = time.time()
			result = self.link.execute(command, args)
			t1 = time.time()
			Debug('SQL EX: %.3f %s' % ((t1 - t0), command))
			return result
		
		return None

	def fetchone(self):
		if self.link:
			row = self.link.fetchone()
#			Debug('SQL F1: %s' % row.__repr__())
			return row
		return None

	def fetchall(self):
		if self.link:
			rows = self.link.fetchall()
#			for row in rows:
#				Debug('SQL F*: %s' % row.__repr__())
			return rows
		return None
		

	def getHostOS(self, host):
		"""
		Return the OS name for the given host.
		"""

		for (name, osname) in self.select(
				"""
				n.name, o.name from
				boxes b, nodes n, oses o
				where n.box = b.id and
				b.os = o.id
				"""):
			if name == host:
				return osname
		return None

	def getHostAppliance(self, host):
		"""
		Returns the appliance for a given host.
		"""

		for (name, appliance) in self.select(
				"""
				n.name, a.name from
				nodes n, appliances a 
				where
				n.appliance = a.id
				"""):
			if name == host:
				return appliance
		return None

	def getHostEnvironment(self, host):
		"""
		Returns the environment for a given host.
		"""

		for (name, environment) in self.select(
				"""
				n.name, e.name from
				nodes n, environments e
				where
				n.environment=e.id
				"""):
			if name == host:
				return environment
		return None


	def getHostRoutes(self, host, showsource=0):

		_frontend = self.getHostname('localhost')
		host = self.getHostname(host)
		routes = {}

		# if needed, add default routes to support multitenancy
		if _frontend == host:
			_networks = self.select(
			"""
			n.ip, n.device, np.ip 
			from networks n
			left join networks np
			on np.node != (select id from nodes where name='%s') and n.subnet = np.subnet
			where n.node=(select id from nodes where name='%s')
			""" % (_frontend, _frontend))

			_network_dict = {}
			for _network in _networks:
				if None in _network:
					continue
				(gateway, interface, destination) = _network
				interface = interface.split('.')[0].split(':')[0]
				
				if destination in _network_dict:
					routes[destination] = _network_dict[destination]
				else:
					if showsource:
						_network_dict[destination] = (
							'255.255.255.255', 
							gateway, 
							interface, 
							'H')
					else:
						_network_dict[destination] = (
							'255.255.255.255', 
							gateway, 
							interface,)

				
		
		# global
		
		for (n, m, g, s, i) in self.select("""
			network, netmask, gateway, subnet, interface from
			global_routes
			"""):
			if s:
				for dev, in self.select("""
					net.device from
					subnets s, networks net, nodes n where
					s.id = %s and s.id = net.subnet and
					net.node = n.id and n.name = '%s'
					and net.device not like 'vlan%%' 
					""" % (s, host)):
					i = dev
			if showsource:
				routes[n] = (m, g, i, 'G')
			else:
				routes[n] = (m, g, i)

		# os
				
		for (n, m, g, s, i) in self.select("""
			r.network, r.netmask, r.gateway,
			r.subnet, r.interface from os_routes r, nodes n where
			r.os='%s' and n.name='%s'
			"""  % (self.getHostOS(host), host)):
			if s:
				for dev, in self.select("""
					net.device from
					subnets s, networks net, nodes n where
					s.id = %s and s.id = net.subnet and
					net.node = n.id and n.name = '%s' 
					and net.device not like 'vlan%%'
					""" % (s, host)):
					i = dev
			if showsource:
				routes[n] = (m, g, i, 'O')
			else:
				routes[n] = (m, g, i)

		# appliance

		for (n, m, g, s, i) in self.select("""
			r.network, r.netmask, r.gateway,
			r.subnet, r.interface from
			appliance_routes r,
			nodes n,
			appliances app where
			n.appliance=app.id and 
			r.appliance=app.id and n.name='%s'
			""" % host):
			if s:
				for dev, in self.select("""
					net.device from
					subnets s, networks net, nodes n where
					s.id = %s and s.id = net.subnet and
					net.node = n.id and n.name = '%s' 
					and net.device not like 'vlan%%'
					""" % (s, host)):
					i = dev
			if showsource:
				routes[n] = (m, g, i, 'A')
			else:
				routes[n] = (m, g, i)

		# host
		
		for (n, m, g, s, i) in self.select("""
			r.network, r.netmask, r.gateway,
			r.subnet, r.interface from node_routes r, nodes n where
			n.name='%s' and n.id=r.node
			""" % host):
			if s:
				for dev, in self.select("""
					net.device from
					subnets s, networks net, nodes n where
					s.id = %s and s.id = net.subnet and
					net.node = n.id and n.name = '%s'
					and net.device not like 'vlan%%'
					""" % (s, host)):
					i = dev
			if showsource:
				routes[n] = (m, g, i, 'H')
			else:
				routes[n] = (m, g, i)

		return routes


	def getNodeName(self, hostname, subnet=None):

		if not subnet:
			rows = self.select("name FROM nodes where name like '%s'" % hostname)
			if rows:
				(hostname, ) = rows[0]
			return hostname

		result = None
		
		for (netname, zone) in self.select("""
			net.name, s.zone from
			nodes n, networks net, subnets s where n.name like '%s'
			and net.node = n.id and net.subnet = s.id and
			s.name like '%s'
			""" % (hostname, subnet)):

			# If interface exists, but name is not set
			# infer name from nodes table, and append
			# dns zone
			if not netname:
				netname = hostname
			result = '%s.%s' % (netname, zone)
		
		return result


	def getHostname(self, hostname=None, subnet=None):
		"""Returns the name of the given host as referred to in
		the database.  This is used to normalize a hostname before
		using it for any database queries."""

		# Look for the hostname in the database before trying
		# to reverse lookup the IP address and map that to the
		# name in the nodes table.  This should speed up the
		# installer w/ the restore pallet

		if hostname and self.link:
			rows = self.link.execute("""select * from nodes where
				name like '%s'""" % hostname)
			if rows:
				return self.getNodeName(hostname, subnet)

		if not hostname:					
			hostname = socket.gethostname()

			if hostname == 'localhost':
				if self.link:
					return ''
				else:
					return 'localhost'
		try:

			# Do a reverse lookup to get the IP address.
			# Then do a forward lookup to verify the IP
			# address is in DNS.  This is done to catch
			# evil DNS servers (timewarner) that have a
			# catchall address.  We've had several users
			# complain about this one.  Had to be at home
			# to see it.
			#
			# If the resolved address is the same as the
			# hostname then this function was called with
			# an ip address, so we don't need the reverse
			# lookup.
			#
			# For truly evil DNS (OpenDNS) that have
			# catchall servers that are in DNS we make
			# sure the hostname matches the primary or
			# alias of the forward lookup Throw an Except,
			# if the forward failed an exception was
			# already thrown.


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
				self.link.execute("""select name from nodes
					where name="%s" """ % hostname)
				if self.link.fetchone():
					return self.getNodeName(hostname, subnet)

				#
				# see if this is a MAC address
				#
				self.link.execute("""select nodes.name from
					networks,nodes where
					nodes.id = networks.node and
					networks.mac = '%s' """ % (hostname))
				try:
					hostname, = self.link.fetchone()
					return self.getNodeName(hostname, subnet)
				except:
					pass

				#
				# see if this is a FQDN. If it is FQDN,
				# break it into name and domain.
				#
				n = hostname.split('.')
				if len(n) > 1:
					name = n[0]
					domain = '.'.join(n[1:])
					cmd = 'select n.name from nodes n, '	+\
						'networks nt, subnets s where '	+\
						'nt.subnet=s.id and '		+\
						'nt.node=n.id and '		+\
						's.zone="%s" and ' % domain     +\
						'(nt.name="%s" or n.name="%s")'	 \
						% (name, name)

					self.link.execute(cmd)
				try:
					hostname, = self.link.fetchone()
					return self.getNodeName(hostname, subnet)
				except:
					pass

				# Check if the hostname is a basename
				# and the FQDN is in /etc/hosts but
				# not actually registered with DNS.
				# To do this we need lookup the DNS
				# search domains and then do a lookup
				# in each domain.  The DNS lookup will
				# fail (already has) but we might
				# find an entry in the /etc/hosts
				# file.
				#
				# All this to handle the case when the
				# user lies and gives a FQDN that does
				# not really exist.  Still a common
				# case.
				
				try:
					fin = open('/etc/resolv.conf', 'r')
				except:
					fin = None
				if fin:
					domains = []
					for line in fin.readlines():
						tokens = line[:-1].split()
						if len(tokens) == 0:
							continue
						if tokens[0] == 'search':
							domains = tokens[1:]
					for domain in domains:
						try:
							name = '%s.%s' % (hostname, domain)
							addr = socket.gethostbyname(name)
							hostname = name
							break
						except:
							pass
					if addr:
						return self.getHostname(hostname)

					fin.close()

				# HostArgumentProcessor has changed
				# handling of appliances (and others)
				# as hsotnames.	 So do some work here
				# to point the user to the new syntax.

				s = ''
				for x, in self.select("""name from appliances"""):
					if x == hostname:
						s = '"a:%s" for %s appliances' % (hostname, hostname)
				if not s:
					for x, in self.select("""name from environments"""):
						if x == hostname:
							s = '"e:%s" for hosts in the %s environment' % (hostname, hostname)
				if not s:
					for x, in self.select("""name from oses"""):
						if x == hostname:
							s = '"o:%s" for %s hosts' % (hostname, hostname)
				if not s:
					for x, in self.select("""name from boxes"""):
						if x == hostname:
							s = '"b:%s" for hosts using the %s box' % (hostname, hostname)
				if not s:
					for x, in self.select("""name from groups"""):
						if x == hostname:
							s = '"g:%s" for host in the %s group' % (hostname, hostname)
				if not s:
					if hostname.find('rack') == 0:
						s = '"r:%s" for hosts in %s' % (hostname, hostname)
				if s:
					raise CommandError(self, 'use %s' % s)
				raise CommandError(self, 'cannot resolve host "%s"' % hostname)
					
		
		if addr == '127.0.0.1': # allow localhost to be valid
			if self.link:
				return self.getHostname(subnet=subnet)
			else:
				return 'localhost'
			
		if self.link:
			# Look up the IP address in the networks table
			# to find the hostname (nodes table) of the node.
			#
			# If the IP address is not found also see if the
			# hostname is in the networks table.  This last
			# check handles the case where DNS is correct but
			# the IP address used is different.
			rows = self.link.execute('select nodes.name from '
				'networks,nodes where '
				'nodes.id=networks.node and ip="%s"' % (addr))
			if not rows:
				rows = self.link.execute('select nodes.name ' 
					'from networks,nodes where '
					'nodes.id=networks.node and '
					'networks.name="%s"' % (hostname))
				if not rows:
					raise CommandError(self, 'host "%s" is not in cluster'
						% hostname)
			hostname, = self.link.fetchone()

		return self.getNodeName(hostname, subnet)


		

class Command:
	"""Base class for all Stack commands the general command line form
	is as follows:

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
		"""Creates a DatabaseConnection for the StackCommand to use.
		This is called for all commands, including those that do not
		require a database connection."""

		if debug is not None:
			stack.commands._debug = debug

		self.db = DatabaseConnection(database)

		self.text  = ''
		self.bytes = b''

		
		self.output = []
	
		self.arch = os.uname()[4]
		if self.arch in ['i386', 'i486', 'i586', 'i686']:
			self.arch = 'i386'
		elif self.arch in ['armv7l']:
			self.arch = 'armv7hl'

		if os.path.exists('/etc/centos-release') or \
				os.path.exists('/etc/redhat-release'):
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
			
		# Look up terminal colors safely using tput, uncolored if
		# this fails.
		
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
					p = subprocess.Popen(c.split(),
							     stdout=subprocess.PIPE)
				except:
					continue
				(o, e) = p.communicate()
				if p.returncode == 0:
					self.colors[key]['code'] = o


	def fillParams(self, names, params=None):
		"""Returns a list of variables with either default
		values of the values in the PARAMS dictionary.
		
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
		#print(self.level)
		if self.notifications:
			sys.stderr.write('%s%s' % (_logPrefix, message))

		
	def command(self, command, args=[]):
		"""Import and run a Stack command.
		Returns and output string."""

		modpath = 'stack.commands.%s' % command
		#print('+ ', command)
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

		self.rc = o.runWrapper(name, args, self.level + 1)
		#print ('- ', command)
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

			module = '%s.%s' % (self.__module__, 
				os.path.splitext(file)[0])

			if module in loadedModules:
				continue
			loadedModules.append(module)

			__import__(module)
			module = eval(module)
			try:
				o = getattr(module, 'Plugin')(self)
			except AttributeError:
				continue
			
			# All nodes point to TAIL.  This insures a fully
			# connected graph, otherwise partial ordering
			# will fail

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
		# Check to see if implementation list
		# has named implementation. If not, try
		# to load named implementation
		if name not in self.impl_list:
			self.loadImplementation(name)

		# If the named implementation was loaded,
		# return the output from running the
		# implementation
		if name in self.impl_list:
			return self.impl_list[name].run(args)




	def isRootUser(self):
		"""Returns TRUE if running as the root account."""
		if os.geteuid() == 0:
			return 1
		else:
			return 0
			
	def isApacheUser(self):
		"""Returns TRUE if running as the apache account."""
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
		"""Reset the output text buffer."""
		self.text  = ''
		self.bytes = b''
		
	def addText(self, s):
		"""Append a string to the output text buffer."""
		if s:
			if isinstance(s, str):
				self.text += s
			else:
				self.bytes += s
		
	def getText(self):
		"""Returns the output text buffer."""
		if self.text:
			return self.text
		if self.bytes:
			return self.bytes
		return None

	def beginOutput(self):
		"""Reset the output list buffer."""
		self.output = []
		
	def addOutput(self, owner, vals):
		"""Append a list to the output list buffer."""

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
		"""Pretty prints the output list buffer."""

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
				self.addText(json.dumps(list))
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
						o = ''.ljust(colwidth[i],
							padChar)
				# *BUT* if this is the last column, it might be super
				# long, so only pad it out as long as the header.
				elif padChar != '' and i == len(line) - 1 and not s:
					o = ''.ljust(len(output[0][i]),
							padChar)
				else:
					o = s
				if isHeader:
					o = '%s%s%s' % (self.colors['bold']['code'],
							o,
							self.colors['reset']['code'])
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
			# Installer has no supplemental groups so we need to
			# include the default group.
			# Outside the installer it is already in the
			# supplemental list.
			groups.append(gid)

		rows = self.db.select('command, groupid from access')
		if rows:
			for c, g in rows:
				if g in groups:
					if fnmatch.filter([name], c):
						allowed = True
		else:

			# If the access table does not exist fallback
			# onto the previous MustBeRoot style access
			# control.
			#
			# This is also the case for the installer.

			if self.MustBeRoot:
				if self.isRootUser() or self.isApacheUser():
					allowed = True
			else:
				allowed = True
			
		return allowed

			
	def runWrapper(self, name, argv, level=0):
		"""Performs various checks and logging on the command before 
		the run() method is called.  Derived classes should NOT
		need to override this."""

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
#			if arg[0] == '[': # ad-hoc group
#				list.append(arg)
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
				raise CommandError(self, 
						   'user "%s" does not have access "%s"' % 
						   (username, name))
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
		"""All derived classes should override this method.
		This method is called by the stack command line as the
		entry point into the Command object.
		
		flags: dictionary of key=value flags
		args: list of string arguments"""
		
		pass

	def getAttr(self, attr):
		return self.getHostAttr('localhost', attr)

	def getHostAttr(self, host, attr):
		for row in self.call('list.host.attr', [host, 'attr=%s' % attr]):
			return row['value']
		return None




class Module:
	def __init__(self, command):
		self.owner = command
		self.db	   = command.db

	def run(self, args):
		"""All derived classes should override this method. This
		is the entry point into the Plugin object."""
		pass


class Implementation(Module):
	"""Base class for all Stack command implementations."""
	pass

	
class Plugin(Module):
	"""Base class for all Stack command plug-ins."""
	
	def provides(self):
		"""Returns a unique string to identify the plug-in.  All
		Plugins must override this method."""

		return None
		
	def requires(self):
		"""Returns a list of plug-in identifiers that must be
		run before this Plugin.	 This is optional for all 
		derived classes."""

		return []

	def precedes(self):
		"""Returns a list of plug-in identifiers that can only by
		run after this Plugin.	This is optional for all derived
		classes."""

		return []
		


class PluginOrderIterator(stack.graph.GraphIterator):
	"""Iterator for Partial Ordering of Plugins"""

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

