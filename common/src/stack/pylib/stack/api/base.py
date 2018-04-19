# @copyright@
# @copyright@

import os
import importlib
import pkgutil

#importlib.import_module('stack.api.plugins')

#def iter_namespace(ns_pkg):
#	return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")
#
#myapp_plugins = {
#	name: importlib.import_module(name)
#	for finder, name, ispkg
#	in iter_namespace(stack.api.plugins)
#}
#print(__file__)

class Base:

	db      = None
	debug   = False
	plugins = None

	def __init__(self):
		print('----')
		if not Base.plugins:
			mods = [ ]
			path = os.path.join(os.path.dirname(os.path.abspath( __file__ )), 'plugins')
			for f in os.listdir(path):
				fname, ext = os.path.splitext(f)
				if ext == '.py':
					continue
				continue
				
#		print(self.__module__)
		print(d)
		for x in pkgutil.iter_modules(d):
			print(x)
#		print(type(self.__module__))
#		pkg = stack.api.plugins
#		for x in pkgutil.iter_modules():
#			print(x)


	# def __init__(self):
	# 	plugins = {
	# 		name: importlib.import_module(name)
	# 		for finder, name, ispkg
	# 		in self.__iter_namespace(stack.api.plugins)
	# 	}
	# 	print('--')
	# 	print(plugins)

	# def __iter_namespace(self, pkg):
	# 	return pkgutil.iter_modules(pkg.__path__, pkg.__name__ + '.')


	def setup(self, db, debug=False):
		Base.db    = db
		Base.debug = debug





