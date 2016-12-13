#
# @SI_Copyright@
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

		csvwriter = csv.writer(sys.stdout)
		csvwriter.writerow(headers)
		sys.stdout.flush()

		csvwriter = csv.DictWriter(sys.stdout, headers)
		csvwriter.writerows(csv_attrs)
