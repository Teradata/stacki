# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import CommandError, ParamRequired, ArgUnique

class command(stack.commands.Command):
	pass

class Command(command):
	"""
	Add a new host with appliance type 'switch' to the cluster.
	This command calls 'add host'. It is a simpler way of setting 
	the appliance type and the attr 'model'.

	<arg type='string' name='switch'>
	A single switch/host name. 
	</arg>

	<param type='string' name='model'>
	The model number of the switch. Used to call implementations during
	the switch configuration.
	</param>
	"""

	def addSwitch(self, switchname, params):
		# The model of the switch
		# Defaults to x1052
		model, = self.fillParams([
		("model", "x1052"),
		])

		# Create a new list of params to add host call
		# instead of checking for params in two places.
		passthroughParams = list(map(
			    lambda x, y: "%s=%s" % (x,y),
			    params.keys(),
			    params.values()
			  ))

		self.call('add.host', [
			switchname, 
			"appliance=switch",
			] + passthroughParams
			)


		# Set the model of the switch to 'model' attr
		self.call('set.host.attr', [
			switchname,
			"attr=model",
			"value=%s" % model,
			])


	def run(self, params, args):

		if len(args) != 1:
			raise ArgUnique(self, 'switch')
		
		switchname = args[0].lower()

		self.addSwitch(switchname, params)
