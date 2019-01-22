import stack.commands
import stack.commands.sync.host.firmware

class Implementation(stack.commands.Implementation):

	def run(self, args):
		return stack.commands.sync.host.firmware.imp_Mellanox_m7800.Implementation(self.owner).run(args = args)
