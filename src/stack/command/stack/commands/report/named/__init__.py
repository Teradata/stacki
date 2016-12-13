# @SI_Copyright@
#                               stacki.com
#                                  v3.3
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
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


import os
import string
import stack.commands
import stack.ip
import stack.text

config_preamble = """options {
	directory "/var/named";
	dump-file "/var/named/data/cache_dump.db";
	statistics-file "/var/named/data/named_stats.txt";
	forwarders { %s; };
        allow-query { private; };
};

controls {
	inet 127.0.0.1 allow { localhost; } keys { rndc-key; };
};

zone "." IN {
	type hint;
	file "named.ca";
};

zone "localhost" IN {
	type master;
	file "named.localhost";
	allow-update { none; };
};

zone "0.0.127.in-addr.arpa" IN {
	type master;
	file "named.local";
	allow-update { none; };
};
"""
# zone mapping
zone_template = """
zone "%s" {
	type master;
	notify no;
	file "%s.domain";
};

zone "%s.in-addr.arpa" {
	type master;
	notify no;
	file "reverse.%s.domain.%s";
};
"""


class Command(stack.commands.report.command):
	"""
	Prints the nameserver daemon configuration file
	for the system.

	<example cmd="report named">
	Outputs /etc/named.conf
	</example>
	"""

	def run(self, params, args):
                
                networks = []
                for row in self.call('list.network', [ 'dns=true' ]):
                        networks.append(row)
                        		
		s = '<file name="/etc/named.conf" perms="0644">\n'
		s += stack.text.DoNotEdit()
                s += '# Site additions go in /etc/named.conf.local\n\n'
                

                acl = [ '127.0.0.0/24']
                for network in networks:
                        ip = stack.ip.IPGenerator(network['address'],
                                                  network['mask'])
                        cidr = ip.cidr()
                        acl.append('%s/%s' % (network['address'], cidr))
                s += 'acl private {\n\t%s;\n};\n\n' % ';'.join(acl)
                                           
		
		fwds = self.getAttr('Kickstart_PublicDNSServers')
		if not fwds:
			#
			# in the case of only one interface on the frontend,
			# then Kickstart_PublicDNSServers will not be
			# defined and Kickstart_PrivateDNSServers will have
			# the correct DNS servers
			#
			fwds = self.getAttr('Kickstart_PrivateDNSServers')

			if not fwds:
				return

		forwarders = string.join(fwds.split(','), ';')
		s += config_preamble % (forwarders)
                
                # For every network, get the base subnet,
                # and reverse it. This is basically the
                # format that named understands
                
                for network in networks:
                        sn = self.getSubnet(network['address'], network['mask'])
                        sn.reverse()
			r_sn = string.join(sn, '.')
                        s += zone_template % (network['zone'],
                                              network['network'],
                                              r_sn,
                                              network['network'],
                                              r_sn)
                        
		# Check if there are local modifications to named.conf
		if os.path.exists('/etc/named.conf.local'):
			f = open('/etc/named.conf.local', 'r')
			s += '\n#Imported from /etc/named.conf.local\n'
			s += f.read()
			f.close()
			s += '\n'
			
		s += '\ninclude "/etc/rndc.key";\n'
		s += '</file>\n'

		self.beginOutput()
		self.addOutput('', s)
		self.endOutput(padChar = '')
