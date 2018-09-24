import stack.commands
from stack.switch.m7800 import SwitchMellanoxM7800
import stack.commands.sync.firmware as firm


class Implementation(stack.commands.Implementation):

	appliance = 'switch'

	def run(self, args):
		switch_name = args[0]
		make = args[1]
		model = args[2]
		version = args[3]	
		install_image = firm.getImageName(self.appliance, make, model, version)

		switch_attrs = self.owner.getHostAttrDict(switch_name)

		kwargs = {
			'username': switch_attrs[switch_name].get('username'),
			'password': switch_attrs[switch_name].get('password')
		}

		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		s = SwitchMellanoxM7800(switch_name, **kwargs)
		s.connect()
		show_images = s.show_images()
		images_to_delete = show_images['images_fetched_and_available']
		for image in images_to_delete:
			s.image_delete(image)

		url = self.getURLtoDrivers(switch_name, make, model, install_image)
		status = s.image_fetch(url)

		s.install_firmware(install_image)
		s.image_boot_next()
		s.reload()


	def getURLtoDrivers(self, switch_name, make, model, image):
		host_interface_switch = self.owner.call('list.host.interface', [ switch_name ])
		host_interface_frontend = self.owner.call('list.host.interface', [ 'a:frontend' ])

		switch_networks = set(switch['network'] for switch in host_interface_switch)
		frontend_networks = set(frontend['network'] for frontend in host_interface_frontend)
		common_networks = list(switch_networks & frontend_networks)

		if len(common_networks) == 0:
			return None

		common_network = common_networks[0]
		ip_addr = [ frontend['ip'] for frontend in host_interface_frontend if frontend['network'] in common_network ]

		if len(ip_addr) == 0:
			return None

		ip_addr = ip_addr[0]
		url = 'http://%s/install/firmware/%s/%s/%s/%s' %(ip_addr, self.appliance, make, model, image)

		return url
