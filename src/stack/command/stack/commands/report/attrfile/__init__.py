#
# @SI_Copyright@
#                               stacki.com
#                                  v3.3
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
		targets = {}
		host_attrs = {}
		csv_attrs = []

                # TODO 
                #
                # getHostAttrs is dead
                # use list * attr commands
                # use list host attr resolve=false to get only host attributes
                # look at 'internal' column and ignore intenal attributes

		for host in self.getHostnames([]):

			attrs = self.db.getHostAttrs(host, showsource=True, slash=True,
				filter=attr_filter, shadow=False)
			attrs = [(k, v) for k, v in attrs.iteritems()]
			# Filter out all attributes except host attrs
			host_f = lambda x: x[1][1] == 'H'
			a = filter(host_f, attrs)
			if len(a) == 0:
				continue
			h_a_f = lambda x: {'target':host,x[0]: x[1][0]}
			csv_attrs.extend(map(h_a_f, a))
			for attr in map(lambda x: x[0], a):
				if attr not in headers:
					headers.append(attr)

		# Get Appliance Attributes
		appliance_attrs = self.call('list.appliance.attr',
			['key=%s' % attr_filter])
		t_f = lambda x: x["appliance"]
		appliance_targets = map(t_f, appliance_attrs)
		for t in appliance_targets:
			if not targets.has_key(t):
				targets[t] = []
		for appliance_attr in appliance_attrs:
			#if attr_filter:
			#	attr = stack.attr.ConcatAttr(appliance_attr['scope'],
			#		appliance_attr['attr'], slash=False)
			#	regex = re.compile(attr_filter)
			#	if not regex.match(attr):
			#		continue
			attr = stack.attr.ConcatAttr(appliance_attr['scope'],
				appliance_attr['attr'], slash=True)
			target = appliance_attr['appliance']
			csv_attrs.append({'target': target, attr:appliance_attr['value']})
			if attr not in headers:
				headers.append(attr)

		# Get OS Attributes
		os_attrs = self.call('list.os.attr',
			['key=%s' % attr_filter])
		t_f = lambda x: x["os"]
		os_targets = map(t_f, os_attrs)
		for t in os_targets:
			if not targets.has_key(t):
				targets[t] = []
		for os_attr in os_attrs:
			#if attr_filter:
			#	attr = stack.attr.ConcatAttr(os_attr['scope'],
			#		os_attr['attr'], slash=False)
			#	regex = re.compile(attr_filter)
			#	if not regex.match(attr):
			#		continue
			attr = stack.attr.ConcatAttr(os_attr['scope'],
					os_attr['attr'], slash=True)
			target = os_attr['os']
			csv_attrs.append({'target': target, attr:os_attr['value']})
			if attr not in headers:
				headers.append(attr)

		# Get Environment Attributes
		env_attrs = self.call('list.environment.attr',
			['key=%s' % attr_filter])
		t_f = lambda x: x["environment"]
		env_targets = map(t_f, env_attrs)
		for t in env_targets:
			if not targets.has_key(t):
				targets[t] = []
		for env_attr in env_attrs:
			#if attr_filter:
			#	attr = stack.attr.ConcatAttr(env_attr['scope'],
			#		env_attr['attr'], slash=False)
			#	regex = re.compile(attr_filter)
			#	if not regex.match(attr):
			#		continue
			attr = stack.attr.ConcatAttr(env_attr['scope'],
					env_attr['attr'], slash=True)
			target = env_attr['environment']
			csv_attrs.append({'target': target, attr:env_attr['value']})
			if attr not in headers:
				headers.append(attr)

		# Get Global Attributes
		global_attrs = self.call('list.attr',
			['key=%s' % attr_filter])
		# Filter out intrinsic attributes
		i_f = lambda x: x["source"] == 'G'
		global_attrs = filter(i_f, global_attrs)
		targets['global'] = []
		for global_attr in global_attrs:
			#if attr_filter:
			#	attr = stack.attr.ConcatAttr(global_attr['scope'],
			#		global_attr['attr'], slash=False)
			#	regex = re.compile(attr_filter)
			#	if not regex.match(attr):
			#		continue
			attr = stack.attr.ConcatAttr(global_attr['scope'],
					global_attr['attr'], slash=True)
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

