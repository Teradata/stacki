# flatten the api a bit for argument_processors while allowing for new arg-procs to be dropped in

import importlib
import pkgutil
import pathlib
import inspect

__all__ = []

# get *this* directory
path = pathlib.Path(__file__).resolve().parent
pkg_paths = {fi.parent for fi in path.glob('*.py') if fi.parent != '__init__.py'}

# get all arg_proc modules loaded...
arg_proc_pkg = {}
for _, name, _ in pkgutil.walk_packages(pkg_paths):
	arg_proc_pkg[name] = importlib.import_module('.' + name, 'stack.argument_processors')

# for each module, find any '*ArgProcessor' class add it to the stack.argument_processors namespace
for module in arg_proc_pkg.values():
	for _, cls in inspect.getmembers(module, inspect.isclass):
		if cls.__name__.endswith('ArgProcessor'):
			globals()[cls.__name__] = cls
			__all__.append(cls.__name__)
