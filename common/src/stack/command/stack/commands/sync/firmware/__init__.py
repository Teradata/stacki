import stack.commands
from stack.exception import ParamRequired, ArgRequired

class command(stack.commands.SwitchArgumentProcessor, stack.commands.sync.command):
	pass

class Command(command):
	"""
	Update the firmware of a particular switch (hardware)
	
	<arg type='string' name='host'>
	A single host name of the switch (hardware).
	</arg>

	<param type='string' name='image'>
	Name of the firmware image in the /export/install/drivers/ directory
	</param>

	<example cmd='sync firmware infiniband-10-12 image=image-X86_64-3.6.5009.img'>
	Updates the infiniband-10-12 switch with the firmware image-X86_64-3.6.5009.img.
	</example>
	"""
	def run(self, params, args):
		if len(args) != 1:
			raise ArgRequired(self, 'switch')

		switches = self.getSwitchNames(args)
		(image,) = self.fillParams([
			('image', None)
		])

		if not image:
			raise ParamRequired(self, 'image')

		for switch in self.call('list.host.interface', switches):
			switch_name = switch['host']
			model = self.getHostAttr(switch_name, 'component.model')
			self.runImplementation(model, [switch, image])
