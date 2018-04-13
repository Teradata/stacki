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
	the appliance type and the attr 'switch_model'.

	<arg type='string' name='switch'>
	A single switch/host name. 
	</arg>

	<param type='string' name='model'>
	The model number of the switch. Used to call implementations during
	the switch configuration.
	</param>

	<param type='string' name='username'>
	The username for the switch.
	
	Default: 'admin'
	</param>

	<param type='string' name='password'>
	The password for the switch.
	
	Default: 'admin'
	</param>
	"""

	def addSwitch(self, switchname, params):
		# The model of the switch
		# Defaults to x1052
		(model, username, password) = self.fillParams([
		("model", "x1052"),
		("username", "admin"),
		("password", "admin"),
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


		# Set the model of the switch to 'switch_model' attr
		self.call('set.host.attr', [
			switchname,
			"attr=switch_model",
			"value=%s" % model,
			])

		# Set the username of the switch to 'switch_username' attr
		self.call('set.host.attr', [
			switchname,
			"attr=switch_username",
			"value=%s" % username,
			])

		# Set the password of the switch to 'switch_password' attr
		self.call('set.host.attr', [
			switchname,
			"attr=switch_password",
			"value=%s" % password,
			"shadow=True",
			])

		# Set the max allowable vlan ids of the switch to 'switch_max_vlan' attr
		self.call('set.host.attr', [
			switchname,
			"attr=switch_max_vlan",
			"value=128",
			])



	def run(self, params, args):

		if len(args) != 1:
			raise ArgUnique(self, 'switch')
		
		switchname = args[0].lower()

		self.addSwitch(switchname, params)
