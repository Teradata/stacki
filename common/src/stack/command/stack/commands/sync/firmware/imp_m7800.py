import stack.commands
from stack.switch.m7800 import SwitchMellanoxM7800

class Implementation(stack.commands.Implementation):

	def run(self, args):
		switch = args[0]['host']
		image_name = args[1]

		switch_attrs = self.owner.getHostAttrDict(switch)

		kwargs = {
			'username': switch_attrs[switch].get('username'),
			'password': switch_attrs[switch].get('password')
		}

		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		s = SwitchMellanoxM7800(switch, **kwargs)
		s.connect()
		show_images = s.show_images()
		images_to_delete = show_images['Available images']
		for image in images_to_delete:
			s.image_delete(image)

		url = self.get_url_to_drivers(switch, image_name)
		status = s.image_fetch(url)

		if status != 200:
			s.disconnect()
			return

		s.install_firmware(image_name)
		s.image_boot_next()
		s.reload()


	def get_url_to_drivers(self, switch, image):
		host_interface_switch = self.owner.call('list.host.interface', [ switch ])
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
		url = 'http://%s/install/drivers/%s' %(ip_addr, image)
		
		return url
