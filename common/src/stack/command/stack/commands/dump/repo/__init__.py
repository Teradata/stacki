# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack
import stack.commands
from collections import OrderedDict
import json


class Command(stack.commands.dump.command):
	"""
	Dump the contents of the stacki database as json.

	This command dumps specifically the repository data.
	For each repo, output the name of the repo, as
	well as its alias, and other configuration flags.

	<example cmd='dump repo'>
	Dump json data for repos in the stacki database
	</example>

	<related>load</related>
	"""

	def run(self, params, args):

		self.set_scope('software')

		dump = []
		for row in self.call('list.repo', ['expanded=true']):
			name          = row['name']
			alias         = row['alias']
			url           = row['url']
			autorefresh   = row['autorefresh']
			assumeyes     = row['assumeyes']
			_type         = row['type']
			is_mirrorlist = row['is_mirrorlist']
			gpgcheck      = row['gpgcheck']
			gpgkey        = row['gpgkey']
			os            = row['os']

			dump.append(OrderedDict(name          = name,
						alias         = alias,
						url           = url,
						autorefresh   = autorefresh,
						assumeyes     = assumeyes,
						type          = _type,
						is_mirrorlist = is_mirrorlist,
						gpgcheck      = gpgcheck,
						gpgkey        = gpgkey,
						os            = os,
			))

		self.addText(json.dumps(OrderedDict(version  = stack.version,
						    software = {'repo' : dump}),
					indent=8))
