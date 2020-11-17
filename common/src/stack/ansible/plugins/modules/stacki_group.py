# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_group
short_description: Manage Stacki groups
description:
  - Add and remove Stacki groups

options:
  name:
    description:
      - The name of the group to manage
    required: true
    type: str

  state:
    description:
      - If present, then an group will be added (if needed)
      - If absent, then the group will be removed
    type: str
    choices: [ absent, present ]
    default: present
"""

EXAMPLES = """
- name: Add a group
  stacki_group:
    name: test

- name: Remove a group
  stacki_group:
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

	# Fetch our group info from Stacki
	try:
		groups = run_stack_command("list.group", [module.params["name"]])
	except StackCommandError as e:
		# If the group doesn't exist, it will raise an error
		groups = []

	if len(groups) > 1:
		# No more than one group should match
		module.fail_json(msg="error - more than one group matches name", **result)

	try:
		# Are we adding or removing?
		if module.params["state"] == "present":
			if len(groups) == 0:
				# Adding a new group
				run_stack_command("add.group", [module.params["name"]])
				result["changed"] = True
		else:
			# Only remove an group that actually exists
			if len(groups):
				run_stack_command("remove.group", [module.params["name"]])
				result["changed"] = True

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
