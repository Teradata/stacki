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
# Revision 1.5  2010/10/28 21:11:36  bruno
# no need to protect the firewall dump output with CDATA, the restore roll
# already does that and embedded CDATA statements is an XML error.
#
# Revision 1.4  2010/09/07 23:52:52  bruno
# star power for gb
#
# Revision 1.3  2010/05/13 21:50:14  bruno
# almost there
#
# Revision 1.2  2010/05/07 18:27:43  bruno
# closer
#
# Revision 1.1  2010/04/30 22:07:16  bruno
# first pass at the firewall commands. we can do global and host level
# rules, that is, we can add, remove, open (calls add), close (also calls add),
# list and dump the global rules and the host-specific rules.
#
#

import stack.commands

class command(stack.commands.NetworkArgumentProcessor, 
	stack.commands.dump.command):

	def dump_firewall(self, level='', id=''):
		for t, n, i, o, s, p, a, c, f, cmt in self.db.fetchall():
			cmd = []
			if i == 0:
				name = 'all'
			else:
				name = self.getNetworkName(i)
			if name:
				cmd.append('network=%s' % name)

			if o == 0:
				name = 'all'
			else:
				name = self.getNetworkName(o)
			if name:
				cmd.append('output-network=%s' % name)
			if t:
				cmd.append('table=%s' % t)
			if n:
				cmd.append('rulename=%s' % n)
			if s:
				cmd.append('service="%s"' % s)
			if p:
				cmd.append('protocol="%s"' % p)
			if a:
				cmd.append('action="%s"' % a)
			if c:
				cmd.append('chain="%s"' % c)
			if f:
				cmd.append('flags="%s"' % f)
			if cmt:
				cmd.append('comment="%s"' % cmt)

			self.dump('add %s firewall %s %s' % (level, id,
				' '.join(cmd)))


class Command(command):
	"""
	Dump the global firewall services and rules
	"""
	def run(self, params, args):
		self.db.execute("""select tabletype, name, insubnet,
			outsubnet, service, protocol, action, chain, flags,
			comment from global_firewall""")

		self.dump_firewall()

