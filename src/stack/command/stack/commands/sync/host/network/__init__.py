# $Id$
# 
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@
#
# $Log$
# Revision 1.21  2011/04/14 23:08:59  anoop
# Move parallel class up one level, so that all sync commands can
# take advantage of it.
#
# Added rocks sync host sharedkey. This distributes the 411 shared key
# to compute nodes
#
# Revision 1.20  2011/03/24 19:37:01  phil
# Wrap routes report inside of XML tag to make it like interfaces,networks.
# Add ability to report host addr to output a python dictionary
# mod routes-*.xml and sync host network to use new output format
#
# Revision 1.19  2011/02/01 21:14:00  bruno
# tweaks for the new OpenIPMI.
#
# also, can now set the IPMI password.
#
# Revision 1.18  2011/01/26 17:56:02  bruno
# restart the network after all the plugins have been run
#
# Revision 1.17  2010/10/27 22:25:01  bruno
# hack to get metrics to be reported after the network is restarted with
# 'rocks sync host network'
#
# Revision 1.16  2010/10/22 20:06:37  phil
# With Permission from the release god ... firewall rewrite and restart
# is now part of sync.host.firewall command
#
# Revision 1.15  2010/09/07 23:53:03  bruno
# star power for gb
#
# Revision 1.14  2010/05/27 00:11:33  bruno
# firewall fixes
#
# Revision 1.13  2010/05/20 22:07:33  bruno
# fix
#
# Revision 1.12  2010/05/20 00:31:45  bruno
# gonna get some serious 'star power' off this commit.
#
# put in code to dynamically configure the static-routes file based on
# networks (no longer the hardcoded 'eth0').
#
# Revision 1.11  2010/05/11 22:28:16  bruno
# more tweaks
#
# Revision 1.10  2010/02/22 21:32:48  bruno
# need to also update /etc/sysconfig/network
#
# Revision 1.9  2009/08/28 19:54:47  bruno
# also update the static routes file when syncing the network
#
# Revision 1.8  2009/05/01 19:07:04  mjk
# chimi con queso
#
# Revision 1.7  2009/02/24 00:53:04  bruno
# add the flag 'managed_only' to getHostnames(). if managed_only is true and
# if no host names are provide to getHostnames(), then only machines that
# traditionally have ssh login shells will be in the list returned from
# getHostnames()
#
# Revision 1.6  2009/02/09 00:29:04  bruno
# parallelize 'rocks sync host network'
#
# Revision 1.5  2009/01/13 23:11:33  bruno
# add full pathname to 'service' command so folks can run insert-ethers via
# sudo.
#
# Revision 1.4  2008/10/18 00:55:58  mjk
# copyright 5.1
#
# Revision 1.3  2008/09/22 20:20:42  bruno
# change 'rocks config host interface|network' to
# change 'rocks report host interface|network'
#
# Revision 1.2  2008/09/16 23:46:14  bruno
# wait for the network service to restart
#
# Revision 1.1  2008/08/22 23:26:38  bruno
# closer
#
#
#

import os
import time
import stack.commands
from stack.commands.sync.host import Parallel
from stack.commands.sync.host import timeout

class Command(stack.commands.sync.host.command):
	"""
	Reconfigure and optionally restart the network for the named hosts.

	<param type='boolean' name='restart'>
	If "yes", then restart the network after the configuration files are
	applied on the host.
	The default is: yes.
	</param>

	<example cmd='sync host network compute-0-0'>
	Reconfigure and restart the network on compute-0-0.
	</example>
	"""

	def run(self, params, args):
		restart, = self.fillParams([ ('restart', 'yes') ])

		restartit = self.str2bool(restart)

		hosts = self.getHostnames(args, managed_only=1)

		me = self.db.getHostname('localhost')

		threads = []
		for host in hosts:

			#
			# get the attributes for the host
			#
			attrs = self.db.getHostAttrs(host)

			cmd = '/opt/stack/bin/stack report host interface '
			cmd += '%s | ' % host
			cmd += '/opt/stack/bin/stack report script '
			cmd += 'attrs="%s" | ' % attrs
			if host != me:
				cmd += 'ssh -T -x %s ' % host
			cmd += 'bash > /dev/null 2>&1 '

			cmd += '; /opt/stack/bin/stack report host network '
			cmd += '%s | ' % host
			cmd += '/opt/stack/bin/stack report script '
			cmd += 'attrs="%s" | ' % attrs
			if host != me:
				cmd += 'ssh -T -x %s ' % host
			cmd += 'bash > /dev/null 2>&1 '

			cmd += '; /opt/stack/bin/stack report host route '
			cmd += '%s | ' % host
			cmd += '/opt/stack/bin/stack report script '
			cmd += 'attrs="%s" | ' % attrs
			if host != me:
				cmd += 'ssh -T -x %s ' % host
			cmd += 'bash > /dev/null 2>&1 '

			p = Parallel(cmd)
			threads.append(p)
			p.start()

		#
		# collect the threads
		#
		for thread in threads:
			thread.join(timeout)

		self.command('sync.host.firewall',
			[ 'restart=%s' % restart ] + hosts)

		self.runPlugins(hosts)

		if restartit:
			#
			# after all the configuration files have been rewritten,
			# restart the network
			#
			threads = []
			for host in hosts:
				cmd = '/sbin/service network restart '
				cmd += '> /dev/null 2>&1 ; '
				cmd += '/sbin/service ipmi restart > '
				cmd += '/dev/null 2>&1'
				if host != me:
					cmd = 'ssh %s "%s"' % (host, cmd)

				p = Parallel(cmd)
				threads.append(p)
				p.start()

			#
			# collect the threads
			#
			for thread in threads:
				thread.join(timeout)

		#
		# if IP addresses change, we'll need to sync the config (e.g.,
		# update /etc/hosts, /etc/dhcpd.conf, etc.).
		#
		self.command('sync.config')

		#
		# hack for ganglia on the frontend
		#
		if me in hosts and os.path.exists('/etc/ganglia/gmond.conf'):
			os.system('service gmond restart > /dev/null 2>&1')

