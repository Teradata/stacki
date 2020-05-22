from collections import defaultdict

from stack.argument_processors.box import BoxArgProcessor
from stack.argument_processors.host import HostArgProcessor
from stack.argument_processors.repo import RepoArgProcessor

import stack.commands

class Command(BoxArgProcessor,
	HostArgProcessor,
	RepoArgProcessor,
	stack.commands.report.command):
	"""
	Create a report that describes the repository configuration file
	that should be put on hosts.

	<arg optional='0' type='string' name='host'>
	Host name of machine
	</arg>

	<example cmd='report host repo backend-0-0'>
	Create a report of the repository configuration file for backend-0-0.
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		hosts = self.getHostnames(args)
		self.host_attrs = self.getHostAttrDict(hosts)

		# create a data structure for each box's repo data
		# this will have all cart/pallet/repo data for all enabled boxes in stacki
		# implementations can use this to build repo files as needed
		self.box_data = defaultdict(lambda: {'carts': [], 'pallets': [], 'repos': []})

		# get the boxes that are actually in use by the hosts we're running against
		enabled_boxes = {attrs['box'] for attrs in self.host_attrs.values()}

		for box in enabled_boxes:
			# format is [(cartname, box), ... ]
			self.box_data[box]['carts'] = self.get_box_carts(box)

			# format is [PalletNamedTuple(**Pallet_fields), ...]
			self.box_data[box]['pallets'] = self.get_box_pallets(box)

			# format is {'default': {reponame: {**repo_fields}, ...]
			self.box_data[box]['repos'] = self.get_repos_by_box(box)[box]

		# now for each host, build its customized repo file
		# NOTE: in theory, we should be able to construct one repo file per box and reuse that for hosts...
		for host in hosts:
			# TODO: ubuntu
			imp = 'rpm'
			self.runImplementation(imp, (host,))

		self.endOutput(padChar='', trimOwner=True)
