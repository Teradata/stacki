# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_storage_partition_info
short_description: Return data about Stacki storage partitions
description:
  - If name is supplied, and scope is not global, returns data about a single scoped item
  - If name is supplied, and scope is global, then an error is returned
  - If name is not supplied, and scope is not global, then all data in that scope is returned
  - If name is not supplied, and scope is global, then all global data is returned

options:
  name:
    description:
      - The name of the scoped item to return data about
    type: str
    required: false

  scope:
    description:
      - The scope to return data about
    type: str
    required: false
    choices: ['global', 'appliance', 'os', 'environment', 'host']
    default: global
"""

EXAMPLES = """
- name: Get all global data
  stacki_storage_partition_info:
  register: results

- name: Get data about backend appliance
  stacki_storage_partition_info:
    name: backend
    scope: appliance
  register: results

- name: Get data about all hosts
  stacki_storage_partition_info:
    scope: host
  register: results
"""

RETURN = """
partitions:
  description:
    - List of storage partitions
  returned: on success
  type: complex
  contains:
    appliance:
      description:
        - Name of the appliance for this data
      type: str
      returned: scope is appliance

    os:
      description:
        - Name of the os for this data
      type: str
      returned: scope is os

    environment:
      description:
        - Name of the environment for this data
      type: str
      returned: scope is environment

    host:
      description:
        - Name of the host for this data
      type: str
      returned: scope is host

    device:
      description:
        - Disk device of the partition
      type: str

    partid:
      description:
        - Partition ID or None
      type: int

    mountpoint:
      description:
        - Mount point of the partition
      type: str

    size:
      description:
        - Size of the partition in megabytes as a string, or possibly 'recommended' or 'hibernation' if mountpoint is 'swap'
      type: str

    fstype:
      description:
        - File system type of the partition
      type: str

    options:
      description:
        - Partition options
      type: str

    source:
      description:
        - The scope source of the data
      type: str
      choices: ['G', 'A', 'O', 'E', 'H']
      returned: scope is host
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError


def main():
	# Define the arguments for this module
	argument_spec = dict(
		name=dict(type="str", required=False, default=None),
		scope=dict(
			type="str", required=False, default="global",
			choices=["global", "appliance", "os", "environment", "host"]
		)
	)

	# Create our module object
	module = AnsibleModule(
		argument_spec=argument_spec,
		supports_check_mode=True
	)

	# Initialize a blank result
	result = {
		"changed": False,
		"partitions": []
	}

	# Bail if the user is just checking syntax of their playbook
	if module.check_mode:
		module.exit_json(**result)

	# Fetch our info from Stacki
	args = ["scope=" + module.params["scope"]]

	if module.params["name"]:
		args.append(module.params["name"])

	try:
		for partition in run_stack_command("list.storage.partition", args):
			# Make sure size is a string
			partition["size"] = str(partition["size"])

			# Add it to the results
			result["partitions"].append(partition)

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
