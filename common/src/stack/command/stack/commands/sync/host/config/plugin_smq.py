import stack.commands
from pathlib import Path
from stack.util import _exec

class Plugin(stack.commands.Plugin):
	"""
	Sync smq settings to hosts and restart all smq related services
	"""

	def provides(self):
		return 'smq'

	def requires(self):
		return []

	def run(self, args):
		hosts = args['hosts']
		settings_file = Path('/opt/stack/etc/stacki.yml')
		services = ['smq-processor', 'smq-producer', 'smq-publisher', 'smq-shipper']

		for host in hosts:
			self.owner.notify('Sync SMQ Settings')
			if settings_file.is_file():
				copy_settings = _exec(f'scp {settings_file} {host}:{settings_file}', shlexsplit=True)
				if copy_settings.returncode != 0:
					self.owner.notify(f'Failed to copy settings file to {host}:{copy_settings.stderr}')
			for service in services:
				restart_smq = _exec(f'ssh -t {host} "systemctl restart {service}" ', shlexsplit=True)
				if restart_smq.returncode != 0:
					self.owner.notify(f'Failed to restart service {service} on host {host}')
