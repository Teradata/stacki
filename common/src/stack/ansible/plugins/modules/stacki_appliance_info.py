# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_appliance_info
short_description: Return data about Stacki appliances
description:
  - If name is supplied, returns data about a single appliance
  - If name is not supplied, returns data about all appliances in the system

options:
  name:
    description:
      - The name of the appliance to return data about
    required: false
"""

EXAMPLES = """
- name: Get appliance backend
  stacki_appliance_info:
    name: backend
  register: result

- name: Get all appliances
  stacki_appliance_info:
  register: result
"""

RETURN = """
appliances:
  description:
    - List of appliances
  returned: on success
  type: complex
  contains:
    name:
      description:
        - Name of the appliance
      type: str

    public:
      description:
        - True if the appliance is considered public
      type: bool
"""

from stack.bool import str2bool

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
		"appliances": []
	}

	# Bail if the user is just checking syntax of their playbook
	if module.check_mode:
		module.exit_json(**result)

	# Fetch our appliance info from Stacki
	args = []
	if module.params["name"]:
		args.append(module.params["name"])

	try:
		for appliance in run_stack_command("list.appliance", args):
			# Public needs to be a bool
			appliance["public"] = str2bool(appliance["public"])

			result["appliances"].append(appliance)

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
