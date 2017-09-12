# @SI_Copyright@
# Copyright (c) 2006 - 2017 StackIQ Inc.
# All rights reserved. stacki(r) v4.0 stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @SI_Copyright@

import stack.commands


class Implementation(stack.commands.Implementation):

	def run(self, args):
		host	= args[0]
		server	= args[1]
		osname	= args[2]
		box	= self.owner.getHostAttr(host, 'box')
		repo	= []

		if osname == 'redhat':
			filename = '/etc/yum.repos.d/stacki.repo'
		elif osname == 'sles':
			filename = '/etc/zypp/repos.d/stacki.repo'

		repo.append('<stack:file stack:name="%s">' % filename)

		for pallet in self.owner.getBoxPallets(box):
			pname, pversion, prel, parch, pos = pallet

			repo.append('[%s-%s-%s]' % (pname, pversion, prel))
			repo.append('name=%s %s %s' % (pname, pversion, prel))
			repo.append('baseurl=http://%s/install/pallets/%s/%s/%s/%s/%s' % (server, pname, pversion, prel, pos, parch))
			repo.append('assumeyes=1')
			repo.append('gpgcheck=0')

		for o in self.owner.call('list.cart'):
			if box in o['boxes'].split():
				repo.append('[%s-cart]' % o['name'])
				repo.append('name=%s cart' % o['name'])
				repo.append('baseurl=http://%s/install/carts/%s' % (server, o['name']))
				repo.append('assumeyes=1')
				repo.append('gpgcheck=0')

		repo.append('</stack:file>')

		if osname == 'redhat':
			repo.append('yum clean all')
		elif osname == 'sles':
			repo.append('zypper clean --all')

		for line in repo:
			self.owner.addOutput(host, line)


