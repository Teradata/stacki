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

from collections import namedtuple

from stack.exception import CommandError, ArgRequired, ParamError
from stack.util import flatten

from . import (
	ApplianceArgumentProcessor
	OSArgumentProcessor
	EnvironmentArgumentProcessor
	HostArgumentProcessor
)

class ScopeArgumentProcessor(
	ApplianceArgumentProcessor,
	OSArgumentProcessor,
	EnvironmentArgumentProcessor,
	HostArgumentProcessor
):
	def getScopeMappings(self, args=None, scope=None):
		# We will return a list of these
		ScopeMapping = namedtuple(
			'ScopeMapping',
			['scope', 'appliance_id', 'os_id', 'environment_id', 'node_id']
		)
		scope_mappings = []

		# Validate the different scopes and get the keys to the targets
		if scope == 'global':
			# Global scope has no friends
			if args:
				raise CommandError(
					cmd = self,
					msg = "Arguments are not allowed at the global scope.",
				)

			scope_mappings.append(
				ScopeMapping(scope, None, None, None, None)
			)

		elif scope == 'appliance':
			# Piggy-back to resolve the appliance names
			names = self.getApplianceNames(args)

			# Now we have to convert the names to the primary keys
			for appliance_id in flatten(self.db.select(
				'id from appliances where name in %s', (names,)
			)):
				scope_mappings.append(
					ScopeMapping(scope, appliance_id, None, None, None)
				)

		elif scope == 'os':
			# Piggy-back to resolve the os names
			names = self.getOSNames(args)

			# Now we have to convert the names to the primary keys
			for os_id in flatten(self.db.select(
				'id from oses where name in %s', (names,)
			)):
				scope_mappings.append(
					ScopeMapping(scope, None, os_id, None, None)
				)

		elif scope == 'environment':
			# Piggy-back to resolve the environment names
			names = self.getEnvironmentNames(args)

			if names:

				# Now we have to convert the names to the primary keys
				for environment_id in flatten(self.db.select(
					'id from environments where name in %s', (names,)
				)):
					scope_mappings.append(
						ScopeMapping(scope, None, None, environment_id, None)
					)

		elif scope == 'host':
			# Piggy-back to resolve the host names
			names = self.getHostnames(args)
			if not names:
				raise ArgRequired(self, 'host')

			# Now we have to convert the names to the primary keys
			for node_id in flatten(self.db.select(
				'id from nodes where name in %s', (names,)
			)):
				scope_mappings.append(
					ScopeMapping(scope, None, None, None, node_id)
				)

		else:
			raise ParamError(self, 'scope', 'is not valid')

		return scope_mappings
