# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_host
short_description: Manage Stacki hosts
description:
  - Add, modify, and remove Stacki hosts

options:
  name:
    description:
      - The name of the host to manage
    required: true
    type: str

  appliance:
    description:
      - The appliance used for the host
    required: Only for new hosts
    type: str

  box:
    description:
      - The box used for the host
    required: false
    type: str
    default: default

  comment:
    description:
      - Freeform text to attach to the host
    required: false
    type: str

  environment:
    description:
      - Environment to assign the host
    required: false
    type: str
    default: None

  groups:
    description:
      - Groups to add or remove the host from
    required: false
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - The name of the group
        required: true
        type: str

      state:
        description:
          - If present, then a host will be added to this group
          - If absent, then the host will be removed from this group
        type: str
        choices: [ absent, present ]
        default: present

  installaction:
    description:
      - The install boot action for the host
    required: false
    type: str
    default: default

  interfaces:
    description:
      - List of network interfaces for the host
    type: list
    elements: dict
    suboptions:
      channel:
        description:
          - Channel for this interface
        type: str

      default:
        description:
          - Is the interface is the default for the host
        type: bool
        default: false

      interface:
        description:
          - Device for this interface
        type: str

      ip:
        description:
          - IP address for this interface
        type: str

      name:
        description:
          - Logical name for this interface
        type: str

      network:
        description:
          - Network attached to this interface
        type: str

      mac:
        description:
          - Hardware MAC address for this interface
        type: str

      module:
        description:
          - Device module for this interface
        type: str

      options:
        description:
          - Module options for this interface
        type: str

      vlan:
        description:
          - The VLAN ID for this interface
        type: str

      state:
        description:
          - If present, then an interface will be added to the host, if needed, and options updates.
          - If absent, then the interface will be removed from the host.
	  - If update_mac, then the interface device is used to update the mac.
	  - If update_interface, then the mac is used to update the interface device.
	  - Note: The interface device and mac are both used to match for updating an existing interface.
        type: str
        choices: [ absent, present ]
        default: present

  osaction:
    description:
      - The os boot action for the host
    required: false
    type: str
    default: default

  rack:
    description:
      - By convention, the number of the rack where the host is located
    required: Only for new hosts
    type: str

  rank:
    description:
      - By convention, the position of the host in the rack
    required: Only for new hosts
    type: str

  state:
    description:
      - If present, then a host will be added (if needed) and options are set to match
      - If absent, then the host will be removed
    type: str
    choices: [ absent, present ]
    default: present
"""

EXAMPLES = """
- name: Add a host
  stacki_host:
    name: test-backend
    appliance: backend
    box: default
    comment: "test host"
    groups:
      - name: test
    installaction: console
    interfaces:
      - default: true
        interface: eth0
        ip: "10.10.10.10"
        mac: "00:11:22:33:44:55"
    rack: "10"
    rank: "4"

- name: Remove a host
  stacki_host:
    name: test-backend
    state: absent
"""

RETURN = """ # """

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError


def _add_host(module):
	args = [module.params["name"]]
	for field in (
		"appliance", "box", "environment",
		"installaction", "osaction", "rack", "rank"
	):
		if module.params[field]:
			args.append(f"{field}={module.params[field]}")

	run_stack_command("add.host", args)

	# Add the host comment, if needed
	if module.params["comment"]:
		run_stack_command("set.host.comment",  [
			module.params["name"],
			f'comment={module.params["comment"]}'
		])

	# Process the groups
	if module.params["groups"]:
		for group in module.params["groups"]:
			if group["state"] == "present":
				run_stack_command("add.host.group",  [
					module.params["name"],
					f'group={group["name"]}'
				])

	# Process the interfaces
	if module.params["interfaces"]:
		for interface in module.params["interfaces"]:
			if interface["state"] == "present":
				args = [module.params["name"]]
				for field in (
					"interface", "channel", "default", "ip", "mac",
					"module", "name", "network", "options", "vlan"
				):
					if interface[field]:
						args.append(f"{field}={interface[field]}")

				run_stack_command("add.host.interface", args)


def _update_host(host, module):
	changed = False

	for field in (
		"appliance", "box", "comment", "environment",
		"installaction", "osaction", "rack", "rank"
	):
		# Did the playbook specify a value for the field?
		if module.params[field] is not None:
			# Do we need to modify the field?
			if module.params[field] != host[field]:
				if field in ("installaction", "osaction"):
					run_stack_command(f"set.host.bootaction", [
						module.params["name"],
						f"type={field[:-6]}",
						f"action={module.params[field]}"
					])
				else:
					run_stack_command(f"set.host.{field}", [
						module.params["name"],
						f"{field}={module.params[field]}"
					])

				changed = True

	# Process the groups
	if module.params["groups"]:
		# Get the existing host groups
		existing_groups = set(run_stack_command(
			"list.host.group", [module.params["name"]]
		)[0]["groups"].split())

		# Process the requested changes
		for group in module.params["groups"]:
			if group["state"] == "present" and group["name"] not in existing_groups:
				# Add the new host group
				run_stack_command("add.host.group",  [
					module.params["name"],
					f'group={group["name"]}'
				])
				changed = True

			elif group["state"] == "absent" and group["name"] in existing_groups:
				# Remove an existing host group
				run_stack_command("remove.host.group",  [
					module.params["name"],
					f'group={group["name"]}'
				])
				changed = True

	# Updating existing interfaces in Stacki
	if module.params["interfaces"]:
		if _update_interfaces(module):
			changed = True

	return changed


def _update_interfaces(module):
	changed = False

	# Create two lookup tables of existing interfaces
	lookup_dev = {}
	lookup_mac = {}

	for row in run_stack_command(
		"list.host.interface", [module.params["name"]]
	):
		if row["interface"]:
			lookup_dev[row["interface"]] = row

		if row["mac"]:
			lookup_mac[row["mac"]] = row

	# Process the requested changes
	for interface in module.params["interfaces"]:
		# Try to find a matching existing interface
		existing = None
		if interface["state"] == "update_mac":
			if interface["interface"] in lookup_dev:
				existing = lookup_dev[interface["interface"]]
		elif interface["state"] == "update_interface":
			if interface["mac"] in lookup_mac:
				existing = lookup_mac[interface["mac"]]
		else:
			if interface["interface"] in lookup_dev:
				existing = lookup_dev[interface["interface"]]
			elif interface["mac"] in lookup_mac:
				existing = lookup_mac[interface["mac"]]

		# All the commands will need these base args
		args = [module.params["name"]]
		for field in ("interface", "mac"):
			if interface[field]:
				args.append(f"{field}={interface[field]}")

		# Now lets handle our different states
		if interface["state"] == "present":
			if existing:
				# If the interface already exists, we update it
				for field in (
					"channel", "default", "ip", "module", "name",
					"network", "options","vlan"
				):
					if interface[field] is not None and interface[field] != existing[field]:
						run_stack_command(
							f"set.host.interface.{field}",
							args + [f"{field}={interface[field]}"]
						)
						changed = True
			else:
				# None existing, so we add a new one
				for field in (
					"interface", "channel", "default", "ip", "mac",
					"module", "name", "network", "options", "vlan"
				):
					if interface[field]:
						args.append(f"{field}={interface[field]}")

				run_stack_command("add.host.interface", args)
				changed = True

		elif interface["state"] == "absent":
			if existing:
				run_stack_command("remove.host.interface", args)
				changed = True

		elif interface["state"] == "update_mac":
			if existing and existing["mac"] != interface["mac"]:
				run_stack_command("set.host.interface.mac", args)
				changed = True

		elif interface["state"] == "update_interface":
			if existing and existing["interface"] != interface["interface"]:
				run_stack_command("set.host.interface.interface", args)
				changed = True

	return changed


def main():
	# Define the arguments for this module
	argument_spec = dict(
		name=dict(type="str", required=True),
		appliance=dict(type="str", required=False),
		box=dict(type="str", required=False),
		comment=dict(type="str", required=False),
		environment=dict(type="str", required=False),
		groups=dict(type="list", required=False, elements="dict", options=dict(
			name=dict(type="str", required=True),
			state=dict(type="str", default="present", choices=["absent", "present"])
		)),
		installaction=dict(type="str", required=False),
		interfaces=dict(type="list", required=False, elements="dict", options=dict(
			channel=dict(type="str", required=False),
			default=dict(type="bool", required=False),
			interface=dict(type="str", required=True),
			ip=dict(type="str", required=False),
			mac=dict(type="str", required=False),
			module=dict(type="str", required=False),
			name=dict(type="str", required=False),
			network=dict(type="str", required=False),
			options=dict(type="str", required=False),
			vlan=dict(type="str", required=False),
			state=dict(type="str", default="present", choices=[
				"absent", "present", "update_mac", "update_interface"
			])
		)),
		osaction=dict(type="str", required=False),
		rack=dict(type="str", required=False),
		rank=dict(type="str", required=False),
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

	# Fetch our host info from Stacki
	try:
		hosts = run_stack_command("list.host", [module.params["name"]])
	except StackCommandError as e:
		# If the host doesn't exist, it will raise an error
		hosts = []

	if len(hosts) > 1:
		# No more than one host should match
		module.fail_json(msg="error - more than one host matches name", **result)

	try:
		# Are we adding or removing?
		if module.params["state"] == "present":
			if len(hosts) == 0:
				_add_host(module)
				result["changed"] = True

			else:
				result["changed"] = _update_host(hosts[0], module)
		else:
			# Only remove a host that actually exists
			if len(hosts):
				run_stack_command("remove.host", [module.params["name"]])
				result["changed"] = True

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
