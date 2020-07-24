# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import jinja2

import stack.commands

jtemp = """\
default stack
prompt 0
label stack
{% if kernel.startswith('vmlinuz') %}
	kernel {{ kernel }}
{% else %}
	{{ kernel }}
{% endif %}
{% if args %}
	append {{ args }}
{% endif %}
{% if boottype == 'install' %}
ipappend 2
{% endif %}
"""

class Implementation(stack.commands.Implementation):

	def run(self, args):
		h = args[0]
		i = args[1]

		host      = h['host']
		kernel    = h['kernel']
		ramdisk   = h['ramdisk']
		args      = h['args']
		attrs     = h['attrs']
		boottype  = h['type']

		interface = i['interface']
		ip        = i['ip']
		mask      = i['mask']
		gateway   = i['gateway']

		more_args = []
		# redhat only:
		# If the ksdevice= is set fill in the network
		# information as well.  This will avoid the DHCP
		# request inside anaconda.
		if h['os'] == 'redhat' and args and args.find('ksdevice=') != -1:
			more_args.append(f'ip={ip}')
			more_args.append(f'gateway={gateway}')
			more_args.append(f'netmask={mask}')
			more_args.append(f'dns={attrs.get("Kickstart_PrivateDNSServers")}')
			more_args.append(f'nextserver={attrs.get("Kickstart_PrivateKickstartHost")}')

		if ramdisk:
			more_args.append(f'initrd={ramdisk}')

		templ_vars = {
			'kernel': kernel,
			'args': ' '.join([args] + more_args),
			'boottype': boottype,
		}

		templ = jinja2.Template(jtemp, lstrip_blocks=True, trim_blocks=True)
		self.owner.addOutput(host, templ.render(**templ_vars).rstrip())
