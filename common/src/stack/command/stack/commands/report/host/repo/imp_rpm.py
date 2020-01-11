# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import jinja2

import stack.commands

class Implementation(stack.commands.Implementation):

	def run(self, args):
		host	= args[0]
		osname	= self.owner.host_attrs[host]['os']
		box	= self.owner.host_attrs[host]['box']
		server  = self.owner.host_attrs[host]['Kickstart_PrivateAddress']
		repo	= []

		if osname == 'sles':
			filename = '/etc/zypp/repos.d/stacki.repo'
		elif osname == 'redhat':
			filename = '/etc/yum.repos.d/stacki.repo'

		repo.append('<stack:file stack:name="%s">' % filename)

		for pallet in self.owner.get_box_pallets(box):
			repo.append('[%s-%s-%s]' % (pallet.name, pallet.version, pallet.rel))
			repo.append('name=%s %s %s' % (pallet.name, pallet.version, pallet.rel))
			repo.append('baseurl=http://%s/install/pallets/%s/%s/%s/%s/%s' % \
				(server, pallet.name, pallet.version, pallet.rel, pallet.os, pallet.arch))
			repo.append('gpgcheck=0')
			repo.append('')

		for o in self.owner.call('list.cart'):
			if box in o['boxes'].split():
				repo.append('[%s-cart]' % o['name'])
				repo.append('name=%s cart' % o['name'])
				repo.append('baseurl=http://%s/install/carts/%s' % (server, o['name']))
				repo.append('gpgcheck=0')
				repo.append('')

		# make a second jinja pass at the repo data, in case it has variables with stacki attributes
		repo_str = jinja2.Template(self.owner.box_repo_data[box]).render(**self.owner.host_attrs[host])
		repo.extend(repo_str.splitlines())

		repo.append('</stack:file>')
		if osname == 'sles':
			repo.append('zypper clean --all')
		if osname == 'redhat':
			# TODO rhel8 and dnf?
			repo.append('yum clean all')

		for line in repo:
			self.owner.addOutput(host, line)

