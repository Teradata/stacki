# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import jinja2

import stack.commands
from stack.repo import build_repo_files, yum_repo_template

class Implementation(stack.commands.Implementation):

	def run(self, args):
		host	= args[0]
		osname	= self.owner.host_attrs[host]['os']
		box	= self.owner.host_attrs[host]['box']

		if osname == 'sles':
			repo_location = '/etc/zypp/repos.d/stacki.repo'
		elif osname == 'redhat':
			repo_location = '/etc/yum.repos.d/stacki.repo'

		# if we ever decide to make the repo server ip address more abstract, this is where we'd change it:
		stacki_http_url_base = 'http://{{ Kickstart_PrivateAddress }}/install'

		repo_data = {}
		# convert the raw pallet and cart data into repo dictionaries
		for pallet in self.owner.box_data[box]['pallets']:
			repo_data[pallet.name] = {
				'alias': f'{pallet.name}-{pallet.version}-{pallet.rel}',
				'name': f'{pallet.name} {pallet.version} {pallet.rel}',
				'url': f'{stacki_http_url_base}/pallets/{pallet.name}/{pallet.version}/{pallet.rel}/{pallet.os}/{pallet.arch}',
				'gpgcheck': False,
			}

		for cart, _ in self.owner.box_data[box]['carts']:
			cart_url_base = 'http://{{ Kickstart_PrivateAddress }}/install/carts'
			repo_data[f'{cart}-cart'] = {
				'alias': f'{cart}-cart',
				'name': f'{cart} cart',
				'url': f'{stacki_http_url_base}/carts/{cart}',
				'gpgcheck': False,
			}

		# repo objects are already in the right format so merge that dict here.
		repo_data = {**repo_data, **self.owner.box_data[box]['repos']}

		# build the template string lines from all the repo objects, add an empty line between each repo
		repo_lines = '\n\n'.join(build_repo_files({box: repo_data}, yum_repo_template))

		# make a second jinja pass at the repo data, to render any stacki attributes used (eg. Kickstart_PrivateAddress)
		repo_str = jinja2.Template(repo_lines).render(**self.owner.host_attrs[host])

		repo = []
		repo.append('<stack:file stack:name="%s">' % repo_location)
		repo.extend(repo_str.splitlines())
		repo.append('</stack:file>')

		if osname == 'sles':
			repo.append('zypper clean --all')
		if osname == 'redhat':
			# TODO rhel8 and dnf?
			repo.append('yum clean all')

		for line in repo:
			self.owner.addOutput(host, line)

