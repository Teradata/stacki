# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
import stack.switch
import os

class command(stack.commands.list.command):
	pass

class Command(command):
	"""
	List all supported switches

	<example cmd='list switch support'>
	List all supported switches.
	</example>

	"""
	def run(self, params, args):

		# collect all of the modules (read: files) in the stack.switch path and import them
		for fi in os.listdir(stack.switch.__path__[0]):
			if fi[0] != '_' and fi.split('.')[-1] in ('py', 'pyw'):
				modulename = fi.split('.')[0]
				pkg = '.'.join([stack.switch.__name__, modulename])
				module = __import__(pkg)

		allmodels = []
		# importing modules with subclasses automatically adds them to the base class' __sublcasses__()
		for sub_cls in stack.switch.Switch.__subclasses__():
			# for each sublcass, ask it what its supported models are
			allmodels.extend(sub_cls.supported())

		self.beginOutput()
		for make, model in allmodels:
			self.addOutput(make, model)

		header = ['make', 'model']
		self.endOutput(header=header, trimOwner=True)

