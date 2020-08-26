# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_host_info
short_description: Return data about Stacki hosts
description:
  - If name is supplied, returns data about a single host
  - If name is not supplied, returns data about all hosts in the system

options:
  name:
    description:
      - The name of the host to return data about
    required: false
"""

EXAMPLES = """
- name: Get info for a single host
  stacki_host_info:
    name: backend-0-0
  register: output

- name: Get info for all the hosts
  stacki_host_info:
  register: output
"""

RETURN = """
hosts:
  description:
    - List of hosts
  returned: on success
  type: list
  elements: dict
  contains:
    name:
      description:
        - Name of the host
      type: str

    rack:
      description:
        - Rack number of the host
      type: str

    rank:
      description:
        - Location of the host in the rack
      type: str

    appliance:
      description:
        - The appliance of the host
      type: str

    os:
      description:
        - OS of the host
      type: str

    box:
      description:
        - The box of the host
      type: str

    environment:
      description:
        - Environment of the host
      type: str

    osaction:
      description:
        - Action used during boot of the host
      type: str

    installaction:
      description:
        - Action used during installation of the host
      type: str

    comment:
      description:
        - Freeform string about the host
      type: str

    interfaces:
      description:
        - List of network interfaces for the host
      type: list
      elements: dict
      contains:
        interface:
	  description:
	    - Device for this interface
	  type: str

        default:
	  description:
	    - True if the interface is the default for the host
	  type: bool

        network:
	  description:
	    - Network attached to this interface
	  type: str

        mac:
	  description:
	    - Hardware MAC address for this interface
	  type: str

        ip:
	  description:
	    - IP address for this interface
	  type: str

        name:
	  description:
	    - Logical name for this interface
	  type: str

	module:
	  description:
	    - Device module for this interface
	  type: str

	vlan:
	  description:
	    - The VLAN ID for this interface
	  type: str

	options:
	  description:
	    - Module options for this interface
	  type: str

	channel:
	  description:
	    - Channel for this interface
	  type: str

    groups:
      description:
        - Groups this host is a member of
      type: list
      elements: str

    boot:
      description:
        - Boot info for this host
      type: dict
      contains:
        action:
	  description:
	    - The action taken during next host boot
	  type: str

        nukedisks:
	  description:
	    - True if host storage partitions should be nuked next install
	  type: bool

        nukecontroller:
	  description:
	    - True if host storage controller should be nuked next install
	  type: bool

    status:
      description:
        - Various status fields for the host
      type: dict
      contains:
        state:
	  description:
	    - Latest state of the host
	  type: str

        ssh:
	  description:
	    - State of the SSH daemon
	  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError


def main():
	# Define the arguments for this module
	argument_spec = dict(
		name=dict(type="str", required=False, default=None)
	)

	# Create our module object
	module = AnsibleModule(
		argument_spec=argument_spec,
		supports_check_mode=True
	)

	# Initialize a blank result
	result = {
		"changed": False,
		"hosts": []
	}

	# Bail if the user is just checking syntax of their playbook
	if module.check_mode:
		module.exit_json(**result)

	# Fetch our host info from Stacki
	args = []
	if module.params["name"]:
		args.append(module.params["name"])

	try:
		for host in run_stack_command("list.host", args):
			# Fetch this host's interfaces
			host["interfaces"] = []
			for interface in run_stack_command("list.host.interface", [host["host"]]):
				del interface["host"]
				host["interfaces"].append(interface)

			# Fetch the groups
			host["groups"] = run_stack_command(
				"list.host.group", [host["host"]]
			)[0]["groups"].split()

			# Now boot info
			host["boot"] = run_stack_command("list.host.boot", [host["host"]])[0]
			del host["boot"]["host"]

			# And finally the host status info
			host["status"] = run_stack_command("list.host.status", [host["host"]])[0]
			del host["status"]["host"]

			# Add it to the results
			result["hosts"].append(host)

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
