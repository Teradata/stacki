#! /opt/stack/bin/python3
#
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


import sys
import os
import time
import snack
import bisect
import syslog
import ipaddress
import traceback
import stack.sql
import stack.util
import stack.app
import stack.kickstart
from gettext import gettext as _
from stack.api.get import *
from stack.api import *
from stack.exception import *


class InsertError(Exception):
	pass


class InsertDone(Exception):
	pass


class ServiceController:

	def __init__(self):
		self.services = {}
		self.ignoreList		= []
		self.plugins		= []
		self.plugindir		= os.path.abspath('/opt/stack/var/plugins/')


	def isIgnored(self, service):
		return service in self.ignoreList
	
	def ignore(self, service):
		if service not in self.ignoreList:
			self.ignoreList.append(service)


	def restart(self, service):
		for name in self.services[service]:
			if service not in self.ignoreList:
				eval('self.restart_%s()' % name)


	def loadPlugins(self, app):
		
		if not os.path.exists(self.plugindir):
			return

		if self.plugindir not in sys.path:
			sys.path.append(self.plugindir)
			
		info = _("loading plugins: ")

		modlist = os.listdir(self.plugindir + '/insertethers')
		modlist.sort()
		for f in modlist:
			
			modname, ext = os.path.splitext(f)
			if modname == '__init__' or ext != '.py':
				continue

			info += "%s " % modname
			mods = __import__('insertethers.%s' % modname)
			m = getattr(mods, modname)
			try:
				plugin_class = getattr(m, 'Plugin')
				if not issubclass(plugin_class, 
						stack.sql.InsertEthersPlugin):
					raise Exception('Invalid class')
				
				# Instantiate plugin
				p = plugin_class(app)
				self.plugins.append(p)
			except:
				info += _("(invalid, skipping) ")
		syslog.syslog(syslog.LOG_INFO, info)
		
		
	def logError(self, o=''):
		"Logs the last exception to syslog"
		
		oops = "%s threw exception '%s %s'" % \
			(o, sys.exc_type, sys.exc_value)
		syslog.syslog(syslog.LOG_ERR, oops)
		
				
	def added(self, nodename, nodeid):
		"Tell all plugins this node has been added."

		for p in self.plugins:
			try:
				p.added(nodename, nodeid)
			except:
				self.logError(p)	
	
	
	def done(self):
		"Tell plugins we are finished"
		
		for p in self.plugins:
			try:
				p.done()
			except:
				self.logError(p)

	def update(self):
		"Tell plugins to reload"
		
		for p in self.plugins:
			try:
				p.update()
			except:
				self.logError(p)
			

class GUI:

	def __init__(self):
		self.screen = None
	
	def startGUI(self):
		self.screen = snack.SnackScreen()

	def endGUI(self):
		self.screen.finish()

	def errorGUI(self, message, l1=_("Quit"), l2=None):
		return self.modalGUI(str(message), _("Error"), l1, l2)

	def warningGUI(self, message, l1=_("OK"), l2=None):
		return self.modalGUI(str(message), _("Warning"), l1, l2)

	def infoGUI(self, message, l1=_("OK"), l2=None):
		return self.modalGUI(str(message), _("Information"), l1, l2)
		
	def modalGUI(self, message, title, l1, l2):
		form = snack.GridForm(self.screen, title, 2, 2)

		textbox = snack.TextboxReflowed(40, message)
		form.add(textbox, 0, 0)
		if not l2:
			b1 = snack.Button(l1)
			form.add(b1, 0, 1)
		else:
			b1 = snack.Button(l1)
			b2 = snack.Button(l2)
			form.add(b1, 0, 1)
			form.add(b2, 1, 1)

		if form.runOnce() == b1:
			return 0
		else:
			return 1

	
class InsertEthers(GUI):

	def __init__(self, app):
		GUI.__init__(self)
		self.sql		= app
		self.controller		= ServiceController()
		self.cabinet		= int(GetAttr('discovery.base.rank'))
		self.rank		= -1
		self.only_add_one	= 0
		self.maxNew		= -1 
		self.appliance		= None
		self.basename		= None
		self.ksid		= None
		self.restart_services	= 0
		self.inserted		= []
		self.kickstarted	= {}
		self.lastmsg		= ''
		self.client		= ''
		self.box		= 'default'
		self.bootaction		= 'default'

		self.ipnetwork		= None
		self.currentip		= None

		# Things for Dumping/Restoring 
		self.doRestart		= 1
		self.mac		= None
		self.ipaddr		= None
		self.netmask		= None
		self.subnet		= 'private'
		self.broadcast		= None
		self.appliance_name	= None
		self.device		= None
		self.module		= None
		self.hostname		= None
		self.logfile		= None

		self.kickstartable	= True

	def setBasename(self, name):
		self.basename = name 

	def setHostname(self, name):
		self.hostname = name 

	def setIPaddr(self, ipaddr):
		self.ipaddr = ipaddr 

	def setNetmask(self, netmask):
		self.netmask = netmask 

	def setBroadcast(self, bcast):
		self.broadcast = bcast 

	def setApplianceName(self, appliance_name):
		self.appliance_name = appliance_name 

	def setCabinet(self, n):
		self.cabinet = n

	def setRank(self, n):
		self.rank = n

	def setMax(self, max):
		self.maxNew = max

	def setBox(self, box):
		self.box = box

	def setBootaction(self, bootaction):
		self.bootaction = bootaction 

	def setSubnet(self, subnet):
		self.subnet = subnet

	def startGUI(self):

		GUI.startGUI(self)

		self.form = snack.GridForm(self.screen,
					   _("Discovered Hosts"), 1, 1)
		self.textbox = snack.Textbox(50, 4, "", scroll=1)
		self.form.add(self.textbox, 0, 0)

		self.screen.drawRootText(0, 0, _("%s -- version %s") % 
					 (self.sql.usage_name,
					  self.sql.usage_version))

		self.screen.pushHelpLine(' ')


	def applianceLongNameGUI(self):
		#
		# if self.appliance_name is not empty don't ask
		# 
		if self.appliance_name is not None: 
			app_string = []
			app_string.append(self.appliance_name)
			index = 0

		else:
			#
			# display all longnames to the user -- let them choose
			# which type of machine they want to integrate
			#
			query = """
				select longname from appliances where
				public = 'yes' order by longname
				"""

			if self.sql.execute(query) == 0:
				self.errorGUI(_("No appliance names in database"))
				raise InsertError(msg)

			app_string = []
			for row in self.sql.fetchall():
				(name, ) = row
				app_string.append(name)

			(button, index) = \
			snack.ListboxChoiceWindow(self.screen,
			_("Choose Appliance Type"), 
			_("Select An Appliance Type:"),
			app_string, buttons=(_("OK"), ), default=0)

		#
		# Now try do sanity checking that appliance is OK
		#
		query = """
			select a.id, a.name from appliances a where
			a.longname = '%s'
			""" % app_string[index]

		if self.sql.execute(query) == 0:
			msg = _("Could not find appliance (%s) in database") \
				% (app_string[index])
			raise InsertError(msg)

		self.appliance, basename = self.sql.fetchone()
		
		# Check if the appliance is kickstartable. We only need
		# to check the appliance_attributes table in this instance
		# since this value cannot be in any other table yet.
		query = """select if(aa.value="yes", True, False) from 
			attributes aa, appliances a where a.name="%s" 
			and aa.scope="appliance" and aa.attr="kickstartable" 
			and aa.scopeid=a.id;""" % basename
		rows = self.sql.execute(query)
		if rows > 0:
			self.ksid = 1
			self.kickstartable = bool(self.sql.fetchone()[0])

		#
		# if the basename was not overridden on the command line
		# use what we just read from the database
		#
		if self.basename is None:
			self.basename = basename
			
		self.setApplianceName(app_string[index])
			

	def statusGUI(self):
		"Updates the list of nodes in 'Inserted Appliances' window"

		macs_n_names = ''
		ks = ''
		for (mac, name) in self.inserted:
			if name not in self.kickstarted:
				ks = ''
			elif self.kickstarted[name] == 0:
				ks = '( )'
			elif self.kickstarted[name] == 200:
				ks = '(*)'
			else:	# An error
				ks = '(%s)' % self.kickstarted[name]
			macs_n_names += '%s    %s    %s	   %s\n' % (mac, name, self.box, ks)
		
		self.textbox.setText(macs_n_names)
		self.form.draw()
		self.screen.refresh()


	def waitGUI(self):
		"""Shows a list of discovered but not kickstarted nodes
		for a few seconds."""

		not_done = ''
		hosts = self.kickstarted.keys()
		hosts.sort()
		for name in hosts:
			status = self.kickstarted[name]
			if status != 200:
				ks = '( )'
				if status:
					ks = '(%s)' % status
				not_done += '%s \t %s\n' % (name, ks)

		form = snack.GridForm(self.screen, 
			_("Not kickstarted, please wait..."), 1, 1)
		textbox = snack.Textbox(35, 4, not_done, scroll=1)
		form.add(textbox, 0, 0)

		form.draw()
		self.screen.refresh()
		time.sleep(1)
		self.screen.popWindow()

	def initializeRank(self):
		if self.rank != -1:
			return # The user specified the rank

		# the 'select rack,' and 'group by rack' clauses are
		# there because there is a weird side-effect with
		# using just max(rank) *and* when there are no rows
		# that match the appliance/rack specification. the
		# select will return one row with the NULL value.
		# but, if we add 'select rack,' and 'group by rack'
		# then if no rows match, the select will return 0
		# rows, just like we want.

		query = """
			select rank,max(rank) from nodes where
			appliance = %d and rack = %d
			group by rack
			""" % (self.appliance, self.cabinet)

		if self.sql.execute(query) > 0:
			(rank, max_rank) = self.sql.fetchone()
			try:
				self.rank = int(max_rank) + 1
			except:
				self.rank = 0
		else:
			self.rank = int(GetAttr('discovery.base.rack'))




	def getnetmask(self, dev):
		import subprocess
		import shlex

		#
		# check if bcast,netmask already specified
		#
		if self.netmask is not None and self.broadcast is not None:
			# The user specified broadcast, netmask
			return(self.broadcast, self.netmask)
		#
		# get an IP address
		#
		bcast = ''
		mask  = ''

		cmd = '/sbin/ifconfig %s' % dev
		p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)

		for line in p.stdout.readlines():
			tokens = line.decode().split()

			for i in tokens:
				values = i.split(':')

				if values[0] == 'Bcast':
					bcast = values[1]
				elif values[0] == 'Mask':
					mask = values[1]

		# Set the values into this node's in-memory object
		self.setNetmask(mask)
		self.setBroadcast(bcast)

		return (bcast, mask)

	def getnetwork(self, subnet):
		self.sql.execute("select address,mask from subnets where name='%s'" % subnet)
		network, netmask = self.sql.fetchone()
		return network, netmask
			
	def getnextIP(self, subnet):
		if not self.ipnetwork:
			network, mask = self.getnetwork(subnet)
			self.ipnetwork = ipaddress.IPv4Network(network + '/' + mask)
		
		if self.ipaddr and self.maxNew == 1:
			return self.ipaddr

		# if this is our first call of getnextIP(), we need to find our starting IP in the range of IP's
		if not self.currentip:
			# if we weren't given one, default to broadcast-1
			if not self.sql.ipBaseAddress:
				self.sql.ipBaseAddress = str(self.ipnetwork.broadcast_address - 1)

			starting_ip = int(ipaddress.IPv4Address(self.sql.ipBaseAddress))
			# iterating over a /8 IPv4Network() object to get to the right
			# starting point is very slow. pathological case: minutes
			# so we do a bisect over the int representation of the IP's
			# to get there faster, then instead of iterating over hosts()
			# keep track of our index and increment by hand.

			# get index of starting ip into the list of IP's (not hosts!) in this network
			network_range = range(int(self.ipnetwork.network_address), int(self.ipnetwork.broadcast_address + 1))
			host_index = bisect.bisect_left(network_range, starting_ip)
			# add this index to the int() value of the bottom IP address (eg '10.0.0.0' -> 167772160)
			# This new number is the integer value of the IP.  Use *that* to track the IP addresses.
			self.currentip = ipaddress.IPv4Address(host_index + int(self.ipnetwork.network_address))

		while True:
			# start out with the current IP
			next_ip = int(self.currentip)
			# if we increment to the network or broadcast IP we should stop
			if int(self.ipnetwork.network_address) >= next_ip:
				raise InsertError('Error: Next IP is below allowable hosts in the "%s" network' % subnet)
			if int(self.ipnetwork.broadcast_address) <= next_ip:
				raise InsertError('Error: Next IP is above allowable hosts in the "%s" network' % subnet)

			# if the ip is already associated with a node, increment and loop
			nodeid = self.sql.getNodeId(str(ipaddress.IPv4Address(next_ip)))
			if nodeid:
				self.currentip = next_ip + self.sql.ipIncrement
				msg = 'IP %s is taken, adding %s to find next available' % (next_ip, self.sql.ipIncrement)
				syslog.syslog(syslog.LOG_DEBUG, msg)
			else:
				return str(ipaddress.IPv4Address(next_ip))


	def addit(self, mac, nodename, ip, netmask):

		syslog.syslog(syslog.LOG_DEBUG, 'addit: %s %s %s %s' %
			      (mac, nodename, ip, netmask))
		
		# Check to make sure mac does not already exist
		rows = self.sql.execute('select id from networks where mac="%s"' % mac)
		if rows:
			return

		cmd = '/opt/stack/bin/stack add host %s ' % nodename +\
			'longname="%s" '% self.appliance_name +\
			'rack=%d rank=%d box="%s"' % \
			(self.cabinet , self.rank, self.box)

		s = os.system(cmd)
		if s != 0:
			raise InsertError("Could not insert %s into database" % nodename)

		cmd = '/opt/stack/bin/stack add host interface %s interface=NULL ' % nodename +\
			'default=true mac=%s name=%s ip=%s network=%s' % \
			(mac, nodename, ip, self.subnet)
		s = os.system(cmd)
		if s != 0:
			raise InsertError("Could not insert %s into database" % nodename)

		rows = self.sql.execute('select id from nodes where name="%s"' %
			nodename)
		if not rows:
			raise InsertError("Could not find %s in database" % nodename)

		if self.bootaction:
			Call('set.host.installaction', [nodename, 'action=%s' % self.bootaction])

		Call('set.host.boot', [nodename, 'action=install'])

		nodeid = self.sql.fetchone()[0]
		self.controller.added(nodename, nodeid)
		self.restart_services = 1
			
		list = [(mac, nodename)]
		list.extend(self.inserted)
		self.inserted = list
		if self.ksid is not None:
			self.kickstarted[nodename] = 0

		syslog.syslog(syslog.LOG_DEBUG, 'addit: inserted')

		return 


	def printDiscovered(self, mac):
		form = snack.GridForm(self.screen,
			      _("Discovered New Appliance"), 1, 1)

		new_app = _("Discovered a new appliance with MAC (%s)") % (mac)
		textbox = snack.Textbox(len(new_app), 1, new_app)
		form.add(textbox, 0, 0)

		#
		# display the message for 2 seconds
		#
		form.draw()
		self.screen.refresh()
		time.sleep(2)
		self.screen.popWindow()
			

	def getNodename(self):
		# if the hostname was explicitly set on command line use it
		if self.hostname is not None:
			return self.hostname
		else:
			return '%s-%d-%d' % (self.basename, 
				self.cabinet, self.rank)

	
	def discover(self, mac, dev):
		"Returns 'true' if we inserted a new node, 'false' otherwise."
		
		retval = False

		query = 'select mac from networks where mac="%s"' % (mac)

		if self.sql.execute(query) == 0:
			nodename = self.getNodename()

			(bcast, netmask) = self.getnetmask(dev)
			ipaddr = self.getnextIP(self.subnet)
			self.addit(mac, nodename, ipaddr, netmask)
			self.printDiscovered(mac)
				
			retval = True

		return retval


	def checkDone(self, result, suggest_done):
		"""Returns true if we are ready to exit, false if some nodes
		have been discovered but not yet requested their kickstart
		file. """

		# Normal case
		if result == 'TIMER' and not suggest_done:
			return 0

		if result == 'F9':
			return 1

		# If the nodes are not kickstartable
		if self.kickstartable is False:
			return 1

		# Check if we can really go.
		ok = 1
		for status in self.kickstarted.values():
			if status != 200:
				ok = 0
				break
		if not ok:
			if result == 'F8':
				self.waitGUI()
		else:
			if suggest_done or result == 'F8':
				return 1
		return 0

	
	def listenKs(self, line):
		"""Look in log line for a kickstart request."""
		
		# Track accesses both with and without local certs.
		interesting = line.count('install/sbin/public/profile.cgi') \
			or line.count('install/sbin/profile.cgi')
		if not interesting:
			return 

		fields = line.split()
		try:
			status = int(fields[8])
		except:
			raise ValueError("Apache log file not well formed!")

		nodeid = int(self.sql.getNodeId(fields[0]))
		self.sql.execute('select name from nodes where id=%d' % nodeid)
		try:
			name, = self.sql.fetchone()
		except:
			if status == 200:
				raise InsertError("Unknown node %s got a kickstart file!" % fields[0])
			return

		if name not in self.kickstarted:
			return

		self.kickstarted[name] = status

		self.statusGUI()


	def listenDhcp(self, line):
		"""Look in log line for a DHCP discover message."""

		# Split in the service name since redhat/sles/? prefix log
		# messages in different ways. Also find the mac/eth relative to
		# the DHCPDISCOVER message to handle the case for the collapsed
		# syslog repeated output.

		tokens = line.split('dhcpd:')
		if len(tokens) == 2:
			tokens = tokens[1].split()
			try:
				i   = tokens.index('DHCPDISCOVER')
				mac = tokens[i+2]
				eth = tokens[i+4].replace(':', '').strip()
			except:
				return 
			    
			if self.discover(mac, eth) is False:
				return

			self.statusGUI()

			#
			# for the cases where insert-ethers will only add one
			# node to the database (replace or rank flags are set),
			# then exit after one node is added
			#
			if self.only_add_one == 1:
				self.screen.drawRootText(0, 2, 
					_("Waiting for %s to kickstart...") %
					self.kickstarted.keys()[0])
				# Use exception structure so we dont have 
				# to keep track of the state.
				raise InsertDone("Suggest Done")

			if self.maxNew > 0:
				self.maxNew -= 1
				if self.maxNew == 0:
					raise InsertDone("Suggest Done")

			self.rank = self.rank + 1


	def getBox(self):
		self.sql.execute("select id from boxes where name='%s'" % (self.box))
		box = self.sql.fetchone()
		if box is None:
			self.warningGUI(_("There is no box named: %s\n\n\n\n" % self.box)
			+ _("Create it and try again.\n"))
			return 0
		return 1

	def getBootaction(self):
		self.sql.execute("select name from bootnames where name='%s'" % \
				(self.bootaction))
		box = self.sql.fetchone()
		if box is None:
			self.warningGUI(_("There is no bootaction named: \
					%s\n\n\n\n" % self.bootaction)
			+ _("Create it and try again.\n"))
			return 0
		return 1

			
	def run(self):
		self.startGUI()

		#
		# make sure the box requested exists 
		#
		if self.getBox() == 0:
			self.endGUI()
			return

		if self.getBootaction() == 0:
			self.endGUI()
			return

		self.controller.loadPlugins(self.sql)

		try:

			self.applianceLongNameGUI()
			self.initializeRank()

			if self.hostname:
				query = 'select id from nodes ' +\
					'where name="%s"' % self.hostname
				rows = self.sql.execute(query)
				if rows:
					raise InsertError("Node %s already exists" % self.hostname)

		except (ValueError, InsertError) as msg:
			self.errorGUI(msg)
			self.endGUI()
			sys.stderr.write(_("%s\n") % str(msg))
			return

		log = open('/var/log/messages', 'r')
		log.seek(0, 2)

		for dir in [ 'httpd', 'apache2' ]:
			try:
				kslog = open('/var/log/%s/ssl_access_log' % dir, 'r')
			except:
				pass
		kslog.seek(0, 2)

		#
		# key used to quit
		#
		self.screen.pushHelpLine(
			_(" Press <F8> to quit, press <F9> to force quit"))
		self.form.addHotKey('F8')
		self.form.addHotKey('F9')
		self.form.setTimer(1000)

		self.statusGUI()

		result = self.form.run()
		suggest_done = 0
		done = 0
		while not done:

			# Check syslog for a new line

			syslog_line = log.readline()
			if syslog_line and not suggest_done:
				try:
					self.listenDhcp(syslog_line)
				except InsertDone:
					suggest_done = 1

				except (ValueError, InsertError) as msg:
					self.warningGUI(msg)
				continue

			# Check http log for a new line

			access_line = kslog.readline()
			if access_line:
				try:
					self.listenKs(access_line)
				except InsertError as msg:
					self.warningGUI(msg)
				continue

			result = self.form.run()
			done = self.checkDone(result, suggest_done)

		#
		# if there was a change to the database, restart some
		# services
		#
		if self.restart_services == 1:
			form = snack.GridForm(self.screen,
					      _("Restarting Services"), 1, 1)

			message = _("Restarting Services...")
			textbox = snack.Textbox(len(message), 1, message)
			form.add(textbox, 0, 0)
			form.draw()
			self.screen.refresh()

			self.controller.done()
				
			self.screen.popWindow()

		#
		# cleanup
		#
		log.close()
		self.endGUI()

		if self.lastmsg != '':
			sys.stderr.write(_("%s\n") % self.lastmsg)
			
	
class App(stack.sql.Application):

	def __init__(self, argv):
		stack.sql.Application.__init__(self, argv)
		self.insertor		= InsertEthers(self)
		self.controller		= ServiceController()
		self.lockFile		= '/var/lock/insert-ethers'
		self.ipBaseAddress	= None
		self.ipIncrement	= -1
		self.doUpdate		= 0
		self.batch		= 0

		self.getopt.l.extend([
			('baseip=', 'ip address'),
			('basename=', 'basename'),
			('hostname=', 'hostname'),
			('ipaddr=', 'ip address'),
			('cabinet=', 'number'),
			('rack=', 'number'),
			('inc=', 'number'),
			('rank=', 'number'),
			('box=', 'box'),
			('bootaction=', 'set the bootaction'),
			('update'),
			('network=', 'network name')
		])


	def parseArg(self, c):
		if stack.sql.Application.parseArg(self, c):
			return 1
		elif c[0] == '--baseip':
			self.ipBaseAddress = c[1]
		elif c[0] == '--basename':
			self.insertor.setBasename(c[1])
		elif c[0] == '--hostname':
			self.insertor.setHostname(c[1])
			self.insertor.setMax(1)
		elif c[0] == '--ipaddr':
			self.insertor.setIPaddr(c[1])
			self.insertor.setMax(1)
		elif c[0] in ('--cabinet', '--rack'):
			self.insertor.setCabinet(int(c[1]))
		elif c[0] == '--inc':
			self.ipIncrement = int(c[1])
		elif c[0] == '--rank':
			self.insertor.setRank(int(c[1]))
		elif c[0] == '--update':
			self.doUpdate = 1
		elif c[0] == '--box':
			self.insertor.setBox(c[1])
		elif c[0] == '--network':
			self.insertor.setSubnet(c[1])
		elif c[0] == '--bootaction':
			self.insertor.setBootaction(c[1])
		return 0


	def cleanup(self):
		try:
			os.unlink(self.lockFile)
		except:
			pass


	def run(self):
		self.connect()

		if self.batch:
			# We may not be running as root user
			self.insertor.run()
			return

		if os.path.isfile(self.lockFile):
			raise Exception("error - lock file %s exists" % self.lockFile)
			sys.exit(-1)
		else:
			os.system('touch %s' % self.lockFile)
			
		if self.doUpdate:
			self.controller.loadPlugins(self)
			self.controller.update()
			os.unlink(self.lockFile)
			return

		self.insertor.run()

		self.cleanup()

syslog.openlog('insert-ethers', syslog.LOG_PID, syslog.LOG_LOCAL0)

app = App(sys.argv)
app.parseArgs()
try:
	app.run()
except Exception as msg:
	app.cleanup()
	sys.stderr.write('error - ' + str(msg) + '\n')
	syslog.syslog(syslog.LOG_ERR, 'error - %s' % msg)
	syslog.syslog(syslog.LOG_ERR, traceback.format_exc())
	sys.exit(1)
