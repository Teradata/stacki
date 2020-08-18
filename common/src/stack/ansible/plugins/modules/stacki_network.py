# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_network
short_description: Manage Stacki networks
description:
  - Add, modify, and remove Stacki networks

options:
  name:
    description:
      - The name of the network to manage
    required: true
    type: str

  address:
    description:
      - The IP address space assigned to the network
    required: Only for new networks
    type: str

  mask:
    description:
      - The network mask for the network space
    required: Only for new networks
    type: str

  gateway:
    description:
      - The IP for the gateway in this network space
    required: false
    type: str

  mtu:
    description:
      - The MTU for the network space
    required: false
    type: int

  zone:
    description:
      - The DNS domain (zone) for this network
    type: str
    default: The network name

  dns:
    description:
      - Should the network will be included in the builtin DNS server
    type: bool
    default: no

  pxe:
    description:
      - Should the network be managed by the builtin DHCP/PXE server
    type: bool
    default: no

  state:
    description:
      - If present, then a network will be added (if needed) and options are set to match
      - If absent, then the network will be removed
    type: str
    choices: [ absent, present ]
    default: present
"""

EXAMPLES = """
- name: Add a network
  stacki_network:
    name: primary
    address: 192.168.0.0
    mask: 255.255.255.0
    gateway: 192.168.0.1
    mtu: 1500
    zone: local
    dns: yes
    pxe: yes

- name: Remove a network
  stacki_network:
    name: primary
    state: absent
"""

RETURN = """ # """

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError


def main():
	# Define the arguments for this module
	argument_spec = dict(
		name=dict(type="str", required=True),
		address=dict(type="str", required=False),
		mask=dict(type="str", required=False),
		gateway=dict(type="str", required=False),
		mtu=dict(type="int", required=False),
		zone=dict(type="str", required=False),
		dns=dict(type="bool", required=False),
		pxe=dict(type="bool", required=False),
		state=dict(type="str", default="present", choices=["absent", "present"])
	)

	# Create our module object
	module = AnsibleModule(
		argument_spec=argument_spec,
		supports_check_mode=True
	)

	# Initialize a blank result
	result = {
		"changed": False
	}

	# Bail if the user is just checking syntax of their playbook
	if module.check_mode:
		module.exit_json(**result)

	# Fetch our network info from Stacki
	try:
		networks = run_stack_command("list.network", [module.params["name"]])
	except StackCommandError as e:
		# If box doesn't exist, it will raise an error
		networks = []

	if len(networks) > 1:
		# No more than one network should match
		module.fail_json(msg="error - more than one network matches name", **result)

	try:
		# Are we adding or removing?
		if module.params["state"] == "present":
			if len(networks) == 0:
				# Adding a new network from scratch
				args = [module.params["name"]]
				for field in ("address", "mask", "gateway", "mtu", "zone", "dns", "pxe"):
					if module.params[field]:
						args.append(f"{field}={module.params[field]}")

				run_stack_command("add.network", args)
				result["changed"] = True

			else:
				# We are modifying an existing network
				for field in ("address", "mask", "gateway", "mtu", "zone", "dns", "pxe"):
					# Did the playbook specify a value for the field?
					if module.params[field] is not None:
						# Do we need to modify the field?
						if module.params[field] != networks[0][field]:
							run_stack_command(f"set.network.{field}", [
								module.params["name"], f"{field}={module.params[field]}"
							])
							result["changed"] = True

		else:
			# Only remove a network that actually exists
			if len(networks):
				run_stack_command("remove.network", [module.params["name"]])
				result["changed"] = True

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
