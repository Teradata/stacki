# @SI_Copyright@
#                             www.stacki.com
#                                  v1.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
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
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@

import time
import stack.commands.list.host

class Command(stack.commands.list.host.command):
	"""
        List host stats.

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied, info about
	all the known hosts is listed.
	</arg>

	<example cmd='list host stat compute-0-0'>
	List info for compute-0-0.
	</example>

	<param optional="1" type="string" name="minutes">
	The size of the sample window in minutes. Default: 10.
	</param>

	<param optional="1" type="string" name="samples">
	Number of samples to display. Default: 10.
	</param>

	<param optional="1" type="string" name="start">
	Start time for the sample window. Must be in the format of
	"%m/%d/%Y %H:%M:%S", for example: "07/10/2013 11:00:00".
	</param>

	<param optional="1" type="string" name="stop">
	Stop time for the sample window. Must be in the format of
	"%m/%d/%Y %H:%M:%S", for example: "07/10/2013 11:30:00".
	</param>

	<example cmd='list host stat'>
	List info for all known hosts.
	</example>
	"""

	def run(self, params, args):
                import salt.client

		(minutes, samples, start, stop) = self.fillParams([
			('minutes', '10'),
			('samples', '10'),
			('start', None),
			('stop', None)
			])

		try:
			minutes = int(minutes)
		except:
			minutes = 10

		try:
			samples = int(samples)
		except:
			samples = 10

		if not start or not stop:
			start = None
			stop = None
                
                fmt = '%m/%d/%Y %H:%M:%S'
                try:
                        t0  = int(time.mktime(time.strptime(start, fmt)))
                        t1  = int(time.mktime(time.strptime(stop,  fmt)))
                except:
                        t1 = int(time.time()) - 5
                        t0 = t1 - (int(minutes) * 60)

                if (t1 - t0) <= 0:
                        return None

                minutes = (t1 - t0) / 60
                
                hosts     = {}
                hostOrder = []

                for host in self.getHostnames(args, order='desc'):

			self.db.execute("""
                        	select rack, rank from nodes where name='%s'""" 
                                % host)
                        (rack, rank) = self.db.fetchone()
                        hosts[host] = { 'host'   : host,
                                        'rack'   : int(rack),
                                        'rank'   : int(rank) }
                        hostOrder.append(host)
                        

                client = salt.client.LocalClient()
                op = client.cmd(hosts.keys(), 
                                'rocks-stat.collect',
                                [ t0, t1, samples ], expr_form = 'list')

                stats = {}
                for host, stat in op.items():
                        try:
                                stats[host] = { 'host'   : host,
                                                'rack'   : hosts[host]['rack'],
                                                'rank'   : hosts[host]['rank'],
                                                'stats'  : stat['stats'] }
                        except:
                                # Something went wrong on the client and we 
                                # don't have any data, just ignore the host 
                                pass

                self.beginOutput()
                for host in hostOrder:
                        if stats.has_key(host):
                                for s in stats[host]['stats']:
                                        list = [ s['group'], 
                                                 s['device'],
                                                 s['metric'],
                                                 s['average'] ]
                                        for value in s['values']:
                                                list.append(value)
                                        self.addOutput(host, list)

                list = [ 'host', 'group', 'device', 'metric', 'average' ]
                for i in range(0, samples):
                        list.append('values')
                self.endOutput(header = list)

