# @copyright@
# @copyright@

from stack.exception import ParamRequired, CommandError
from stack.bool import bool2str, str2bool


class Options:

	class Example:

		def __init__(self, command, description):
			self.command     = command
			self.description = description

	class Arg:

		def __init__(self, name, description, required, unique):
			self.name        = name
			self.description = description
			self.required    = required
			self.unique      = unique


	class Param(Arg):

		def __init__(self, name, description, required, default, type):
			Options.Arg.__init__(self, name, description, required, True)

			if type == bool:
				default = bool2str(default)

			self.default = default
			self.type    = type


	def __init__(self):
		self._description = None
		self._examples    = []
		self._arg         = None
		self._params      = []

	def set_description(self, description):
		self._description = description

	def get_description(self):
		return self._description

	def add_example(self, command, *, description=None):
		self._examples.insert(0, Options.Example(command, description))

	def get_examples(self):
		return self._examples

	def set_arg(self, name, *, 
		    description=None, required=True, unique=False):
		self._arg = Options.Arg(name, 
					description, required, unique)
		return self

	def get_arg(self):
		return self._arg

	def add_param(self, name, *, 
		      description=None, required=False, default=None, type=str):
		self._params.insert(0, Options.Param(name, 
						     description, required, default, type))
		return self

	def get_params(self):
		return self._params


class opt:

	class _decorator:
		def __init__(self, *args, **kwargs):
			self.args   = args
			self.kwargs = kwargs

		def __call__(self, cmd):
			if not hasattr(cmd, 'options'):
				cmd.options = Options()

	class desc(_decorator):

		def __call__(self, cmd):
			opt._decorator.__call__(self, cmd)
			cmd.options.set_description(*self.args, **self.kwargs)
			return cmd

	class eg(_decorator):

		def __call__(self, cmd):
			opt._decorator.__call__(self, cmd)
			cmd.options.add_example(*self.args, **self.kwargs)
			return cmd


	class arg(_decorator):
	
		def __call__(self, cmd):
			opt._decorator.__call__(self, cmd)
			cmd.options.set_arg(*self.args, **self.kwargs)
			return cmd


	class param(_decorator):

		def __call__(self, cmd):
			opt._decorator.__call__(self, cmd)
			cmd.options.add_param(*self.args, **self.kwargs)
			return cmd

	def parse(func):
		def wrapper(self, old_params, old_args):
			if not hasattr(self, 'options'):
				raise CommandError(self, 'missing opt.* decorators')

			new_params = {}
			for param in self.options.get_params():

				if param.name in old_params:
					value = old_params[param.name]
				else:
					if param.required:
						raise ParamRequired(self, param.name)
					value = param.default
			
				if param.type == bool:
					value = str2bool(value)
				elif param.type == int:
					value = int(value)
				elif param.type == float:
					value = float(value)
				new_params[param.name] = value

			return func(self, new_params, old_args)
		return wrapper
