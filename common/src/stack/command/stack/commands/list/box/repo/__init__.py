# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
#
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Command(stack.commands.list.box.command):
	"""
	List the repos enabled in each box.

	<arg optional='1' type='string' name='box' repeat='1'>
	List of boxes.  If no box is specified, all boxes are shown.
	</arg>

	<example cmd='list box repo default'>
	List the repos used in the "default" box.
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		for box in self.get_box_names(args):
			for repo_data in self.get_repos_by_box(box).values():
				for repo in repo_data.values():
					self.addOutput(box, (repo['name'], repo['alias']))

		self.endOutput(
			header=['box', 'repo', 'alias'],
			trimOwner=False
		)
