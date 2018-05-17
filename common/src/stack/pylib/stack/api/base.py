# @copyright@
# @copyright@

from yapsy.PluginManager import PluginManager
import os
import sys
#import importlib
#import pkgutil

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

	db             = None
	debug          = False
	plugin_manager = None

	def __init__(self):
		if not Base.plugin_manager:
			path = __file__.split(os.sep)[:-1]
			path.append('plugins')
			path = os.sep.join(path)

			pm = PluginManager()
			pm.setPluginPlaces([ path ])
			pm.collectPlugins()
			for p in pm.getAllPlugins():
				print(p.plugin_object.name())

			Base.plugin_manager = pm

## Activate all loaded plugins
#for pluginInfo in simplePluginManager.getAllPlugins():
#   simplePluginManager.activatePluginByName(pluginInfo.name)


	def setup(self, db, debug=False):
		Base.db    = db
		Base.debug = debug





