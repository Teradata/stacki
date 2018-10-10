# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands


class Implementation(stack.commands.Implementation):

	def run(self, args):
		host	= args[0]
		server	= args[1]
		box	= self.owner.getHostAttr(host, 'box')
		repo	= []

		filename = '/etc/yum.repos.d/stacki.repo'

		repo.append('<stack:file stack:name="%s">' % filename)

		for pallet in self.owner.getBoxPallets(box):
			repo.append('[%s-%s-%s]' % (pallet.name, pallet.version, pallet.rel))
			repo.append('name=%s %s %s' % (pallet.name, pallet.version, pallet.rel))
			repo.append('baseurl=http://%s/install/pallets/%s/%s/%s/%s/%s' % \
				(server, pallet.name, pallet.version, pallet.rel, pallet.os, pallet.arch))
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

		repo.append('yum clean all')

		for line in repo:
			self.owner.addOutput(host, line)


