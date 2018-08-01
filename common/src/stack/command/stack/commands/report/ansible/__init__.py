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

		attrs, = self.fillParams([ ('attribute', None) ])

		if attrs is not None:
			attrs = attrs.split(',')
		else:
			attrs = []

		groups = {}
		for row in self.call('list.host.attr'):

			host = row['host']
			attr = row['attr']
			val  = row['value']

			# TODO - Update to use the qualifier to scope these
			# groups (e.g. a:backend)

			if attr == 'appliance':
				if val not in groups:
					groups[val] = { 'hosts': [] }
				groups[val]['hosts'].append(host)

			elif attr == 'rack':
				rack = 'rack%s' % val
				if rack not in groups:
					groups[rack] = { 'hosts': []}
				groups[rack]['hosts'].append(host)

			elif attr == 'managed':
				if str2bool(val) is True:
					if attr not in groups:
						groups[attr] = { 'hosts': [] }
					groups['managed']['hosts'].append(host)

			elif attr in attrs:
				if attr not in groups:
					groups[attr] = { 'hosts': []}
				groups[attr]['hosts'].append(host)


		self.beginOutput()
		self.addOutput('', '<stack:file stack:name="/etc/ansible/hosts">')
		for cat in groups:
			self.addOutput('', '[%s]' % cat)
			hostlist = '\n'.join(groups[cat]['hosts'])
			self.addOutput('', hostlist)
			self.addOutput('', '')
		self.addOutput('', '</stack:file>')
		self.endOutput(padChar='')
