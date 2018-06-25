#
# @SI_COPYRIGHT@
# @SI_COPYRIGHT@
# 

import stack.commands
from stack.bool import str2bool
from stack.exception import CommandError

class Command(stack.commands.Command,
	stack.commands.HostArgumentProcessor):
	"""
	Report an Ansible Inventory Script.

	File defaults to /etc/ansible/hosts in "ini" format.

	Does not do vars.

	<param type='string' name='attribute'>
	A shell syntax glob pattern to specify attributes to
	be listed. The attribute is the stanza header.
	</param>

	<example cmd='report ansible'>
	Create an inventory file of the managed hosts, rack, and
	appliances currently available.
	</example>

	<example cmd='report ansible attribute=kube_master,kube_worker'>
	Create an inventory file of the managed hosts, rack, and
	appliances and nodes that have kube_master or kube_minion set to
	"True". The attribute name is the group target.

	..snip..

	[kube_master]
	backend-0-0

	[kube_worker]
	backend-0-1
	backend-0-2
	backend-0-3
	backend-0-4
	..snip..
	</example>
	"""
	def run(self, params, args):
		prms = self._params
		# Get Host Attributes
		s = self.call('list.host.attr')

		host_bucket = {'managed': {'hosts': []}}
		for i in s:
			host = i['host']
			attr = i['attr']
			val = i['value']
			# Categorize by appliances
			if attr == 'appliance':
				if val not in host_bucket:
					host_bucket[val] = { 'hosts':[] }
				host_bucket[val]['hosts'].append(host)
			# Categorize by rack
			if attr == 'rack':
				rack = 'rack%s' % val
				if rack not in host_bucket:
					host_bucket[rack] = { 'hosts': []}
				host_bucket[rack]['hosts'].append(host)
			# Managed Hosts
			if attr == 'managed':
				if str2bool(val) == True:
					host_bucket['managed']['hosts'].append(host)
			# if len(prms) > 0:
			if prms:
				k = list(prms.keys())
				if 'attribute' in k:
					for i in prms['attribute'].split(','):
						if attr == i:
							if attr not in host_bucket:
								host_bucket[attr] = { 'hosts': []}
							host_bucket[attr]['hosts'].append(host)
				else:
					raise CommandError(self,'argument "%s" not recognized' % k[0])
		self.beginOutput()
		self.addOutput('','<stack:file stack:name="/etc/ansible/hosts">')
		for cat in host_bucket:
			self.addOutput('','[%s]' % cat)
			hostlist = '\n'.join(host_bucket[cat]['hosts'])
			self.addOutput('',hostlist)
			self.addOutput('','')
		self.addOutput('','</stack:file>')
		self.endOutput()
