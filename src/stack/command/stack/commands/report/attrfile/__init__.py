#
# @SI_Copyright@
#                               stacki.com
#                                  v4.0
# 
#      Copyright (c) 2006 - 2017 StackIQ Inc. All rights reserved.
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

import os
import sys
import csv
import re
import cStringIO
import stack.commands
import stack.attr

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	This command outputs all the attributes
	of a system in a CSV format.
	<param name="filter" type="string" optional="1">
	Filter out only the attributes that you want.
	</param>
	"""
	def run(self, params, args):
		(attr_filter, ) = self.fillParams([
			("filter",None),
			])
		headers = []
		host_attrs = {}
		csv_attrs = []
		regex = None

		if attr_filter:
			regex = re.compile(attr_filter)

                #
                # use list host attr resolve=false to get only host attributes
                # look at 'internal' column and ignore intenal attributes
		#
		for host in self.getHostnames([]):
			host_attrs = self.call('list.host.attr',
				['resolve=false'])
			for host_attr in host_attrs:
				attr = host_attr['attr']
				if host_attr['internal'] == 'True' or \
					(regex and not regex.match(attr)):
					continue
				hostname = host_attr['host']
				csv_attrs.append({'target': hostname, attr:host_attr['value']})

				if attr not in headers:
					headers.append(attr)

		# Get Appliance Attributes
		appliance_attrs = self.call('list.appliance.attr')

		for appliance_attr in appliance_attrs:
			attr = appliance_attr['attr']
			if regex and not regex.match(attr):
				continue

			target = appliance_attr['appliance']
			csv_attrs.append({'target': target, attr:appliance_attr['value']})

			if attr not in headers:
				headers.append(attr)

		# Get OS Attributes
		os_attrs = self.call('list.os.attr')
		for os_attr in os_attrs:
			attr = os_attr['attr']
			if regex and not regex.match(attr):
				continue

			target = os_attr['os']
			csv_attrs.append({'target': target, attr:os_attr['value']})
			if attr not in headers:
				headers.append(attr)

		# Get Environment Attributes
		env_attrs = self.call('list.environment.attr')
		for env_attr in env_attrs:
			attr = env_attr['attr']
			if regex and not regex.match(attr):
				continue

			target = env_attr['environment']
			csv_attrs.append({'target': target, attr:env_attr['value']})
			if attr not in headers:
				headers.append(attr)

		# Get Global Attributes
		global_attrs = self.call('list.attr',
			['key=%s' % attr_filter])
		for global_attr in global_attrs:
			attr = global_attr['attr']
			if regex and not regex.match(attr):
				continue
			csv_attrs.append({'target': 'global', attr:global_attr['value']})
			if attr not in headers:
				headers.append(attr)

		headers.sort()
		headers.insert(0, 'target')

		# CSV writer requires fileIO.
		# Setup string IO processing
		csv_f = cStringIO.StringIO()
		csv_w = csv.writer(csv_f)
		csv_w.writerow(headers)
		csv_f.flush()
		csv_w = csv.DictWriter(csv_f, headers)
		csv_w.writerows(csv_attrs)

		# Get string from StringIO object
		s = csv_f.getvalue().strip()
		csv_f.close()

		self.beginOutput()
		self.addOutput('localhost', s)
		self.endOutput()
