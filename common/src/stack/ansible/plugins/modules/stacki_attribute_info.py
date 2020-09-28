# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_attribute_info
short_description: Return data about Stacki attributes
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

  attr:
    description:
      - A shell syntax glob pattern to specify attributes to return data about
    type: str
    required: false

  shadow:
    description:
      - Should shadow attributes be returned along with non-shadow attributes
    type: bool
    required: false
    default: yes
"""

EXAMPLES = """
- name: Get all global data
  stacki_attribute_info:
  register: results

- name: Get data about backend appliance
  stacki_attribute_info:
    name: backend
    scope: appliance
  register: results

- name: Get the os.version attribute for backend-0-0
  stacki_attribute_info:
    name: backend-0-0
    scope: host
    attr: os.version
  register: result
"""

RETURN = """
attributes:
  description:
    - List of attributes
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

    scope:
      description:
        - The scope source of the data
      type: str
      choices: ['global', 'appliance', 'os', 'environment', 'host']

    type:
      description:
        - The type of the attribute
      type: str
      choices: ['const', 'shadow', 'var']

    attr:
      description:
        - The attribute name
      type: str

    value:
      description:
        - The value assigned to the attribute
      type: str
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
		),
		attr=dict(type="str", required=False, default=None),
		shadow=dict(type="bool", required=False, default=True)
	)

	# Create our module object
	module = AnsibleModule(
		argument_spec=argument_spec,
		supports_check_mode=True
	)

	# Initialize a blank result
	result = {
		"changed": False,
		"attributes": []
	}

	# Bail if the user is just checking syntax of their playbook
	if module.check_mode:
		module.exit_json(**result)

	# Fetch our info from Stacki
	args = ["scope=" + module.params["scope"]]

	if module.params["name"]:
		args.append(module.params["name"])

	for field in ("attr", "shadow"):
		if module.params[field] is not None:
			args.append(f"{field}={module.params[field]}")

	try:
		for attribute in run_stack_command("list.attr", args):
			# Make sure attribute value is a string
			attribute["value"] = str(attribute["value"])

			# Add it to the results
			result["attributes"].append(attribute)

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
