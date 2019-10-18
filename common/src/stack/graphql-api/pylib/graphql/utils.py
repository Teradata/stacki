from functools import wraps
import importlib
import os.path
from pkgutil import iter_modules


def dynamic_import(path, name):
	"""
	Dynamically import all the python modules in a directory.
	To use, simply call: `dynamic_import(__file__, __name__)`
	"""

	for _, module, _ in iter_modules([os.path.dirname(path)], prefix=name+"."):
		importlib.import_module(module)

def map_kwargs(mappings):
	"""
	This decorator will map a schema argument name to a different
	resolver parameter name. Useful for mapping `id` or `type`.
	"""

	def inner(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			mapped_kwargs = {}
			for key, value in kwargs.items():
				if key in mappings:
					mapped_kwargs[mappings[key]] = value
				else:
					mapped_kwargs[key] = value

			return func(*args, **mapped_kwargs)

		return wrapper
	return inner

def is_mysql_like_pattern(args):
	"""
	Accepts either a single str or an iterable of them, and
	returns true if they contain a '_' or '%' character.
	"""

	if isinstance(args, str):
		string = args
	else:
		string = ''.join(args)

	return '_' in string or '%' in string

def create_common_filters(id_, names, id_field="id", names_field="name"):
	"""
	Returns a tuple of filters and values for those filters for
	a common pattern of looking up data in the Stacki DB.
	"""

	filters = []
	values = []

	if id_ is not None:
		filters.append(f"{id_field} = %s")
		values.append(id_)

	if names:
		if is_mysql_like_pattern(names):
			# Gotta use LIKE for each pattern, joined with OR
			filters.append("(" + " OR ".join([
				f"{names_field} LIKE %s" for name in names
			]) + ")")
			values.extend(names)
		else:
			# Safe to just check if name is in the list of names
			filters.append(f"{names_field} IN %s")
			values.append(names)

	return filters, values
