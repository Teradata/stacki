# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from stack.exception import ArgRequired, ArgUnique, ParamValue, CommandError
import stack.commands


class command(stack.commands.set.command, stack.commands.OSArgumentProcessor):

	def getBootActionTypeOS(self, params, args):
		if not len(args):
			raise ArgRequired(self, 'action')
		if len(args) != 1:
			raise ArgUnique(self, 'action')
		b_action = args[0]

		(b_type, b_os) = self.fillParams([
			('type', None, True),
			('os', '')])

		if b_type not in [ 'os', 'install' ]:
			raise ParamValue(self, 'type', '"os" or "install"')

		if not b_os:
			b_os = self.os

		if b_os:
			b_os = self.getOSNames([b_os])[0]

		return (b_action, b_type, b_os)

	def actionExists(self, b_action, b_type, b_os=None):
		for row in self.call('list.bootaction', 
				     [ b_action, 
				       'type=%s' % b_type, 
				       'os=%s' % b_os ]):
			if b_os == '':
				b_os = None
			if b_action == row['bootaction'] and b_type == row['type'] and b_os == row['os']:
				return True
		return False


	def bootNameExists(self, b_action, b_type):

		for a, t in self.db.select('name, type from bootnames'):
			if b_action == a and b_type == t:
				return True
		return False


class Command(command):
	"""
	Updates bootaction parameters.
	"""

	def run(self, params, args):
		(b_action, b_type, b_os) = self.getBootActionTypeOS(params, args)

		(b_kernel, b_ramdisk, b_args, force) = self.fillParams([
			('kernel',  '', True),
			('ramdisk', ''),
			('args',    ''),
			('force',   False)
			])


		force = self.str2bool(force)

		if self.actionExists(b_action, b_type, b_os):
			raise CommandError(self, 'action "%s" exists' % b_action)

		if not self.bootNameExists(b_action, b_type):
			self.db.execute(
				"""
				insert into bootnames
				(name, type)
				values
				('%s', '%s')""" % (b_action, b_type))
		if b_os:
			self.db.execute(
				"""
				insert into bootactions
				(bootname, os)
				values
				(
				(select id from bootnames where name='%s' and type='%s'),
				(select id from oses where name='%s')
				)""" % (b_action, b_type, b_os))
		else:
			self.db.execute(
				"""
				insert into bootactions
				(bootname)
				values
				(
				(select id from bootnames where name='%s' and type='%s')
				)""" % (b_action, b_type))
			

		for (flag, command) in [ (b_kernel,  'kernel'),
					 (b_args,    'args'),
					 (b_ramdisk, 'ramdisk') ]:
			if flag:
				self.command('set.bootaction.%s' % command, 
					     (b_action,
					      'type=%s' % b_type, 
					      'os=%s'   % b_os,
					      '%s=%s'   % (command, flag)))
			
			

