from collections import defaultdict

from stack.graphql.utils import dynamic_import


class Registry:
	def __init__(self):
		self._plugins = defaultdict(list)

	def run_plugins(self, tag, *args, **kwargs):
		results = []
		for func in self._plugins[tag]:
			result = func(*args, **kwargs)
			if result:
				results.append(result)
		return results

	def plugin(self, tag):
		def inner(func):
			self._plugins[tag].append(func)
			return func

		return inner

registry = Registry()

# Dynamically import the plugins in this folder
dynamic_import(__file__, __name__)
