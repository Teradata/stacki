# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_appliance
short_description: Manage Stacki appliances
description:
  - Add, modify, and remove Stacki appliances

options:
  name:
    description:
      - The name of the appliance to manage
    required: true
    type: str

  node:
    description:
      - The name of the root XML node for the appliance
    required: false
    type: str

  state:
    description:
      - If present, then an appliance will be added (if needed) and node updated (if provided)
      - If absent, then the appliance will be removed
    type: str
    choices: [ absent, present ]
    default: present
"""

EXAMPLES = """
- name: Add an appliance
  stacki_appliance:
    name: test
    node: backend

- name: Remove an appliance
  stacki_appliance:
    name: test
    state: absent
"""

RETURN = """ # """

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError


def main():
	# Define the arguments for this module
	argument_spec = dict(
		name=dict(type="str", required=True),
		node=dict(type="str", required=False),
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

	# Fetch our appliance info from Stacki
	try:
		appliances = run_stack_command("list.appliance", [module.params["name"]])
	except StackCommandError as e:
		# If appliance doesn't exist, it will raise an error
		appliances = []

	if len(appliances) > 1:
		# No more than one appliance should match
		module.fail_json(msg="error - more than one appliance matches name", **result)

	try:
		# Are we adding or removing?
		if module.params["state"] == "present":
			if len(appliances) == 0:
				# Adding a new appliance
				args = [module.params["name"]]
				if module.params["node"]:
					args.append("node="+module.params['node'])

				run_stack_command("add.appliance", args)
				result["changed"] = True

			else:
				# We are modifying an existing appliance
				if module.params["node"]:
					# Fetch the existing node attr
					attrs = run_stack_command(
						"list.appliance.attr", [module.params["name"], "attr=node"]
					)
					if len(attrs):
						existing_value = attrs[0]["value"]
					else:
						existing_value = None

					# Change the attr if needed
					if module.params["node"] != existing_value:
						run_stack_command(f"set.appliance.attr", [
							module.params["name"], "attr=node", "value="+module.params["node"]
						])
						result["changed"] = True

		else:
			# Only remove an appliance that actually exists
			if len(appliances):
				run_stack_command("remove.appliance", [module.params["name"]])
				result["changed"] = True

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
