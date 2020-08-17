# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_box
short_description: Manage Stacki boxes
description:
  - Add, edit, and remove Stacki boxes
  - The OS of the box can be modified only if no hosts are assigned to the box.
  - Changing the OS of the box involves removing the existing box and re-adding it with the new OS. All enabled pallets, carts, and repos will need to be re-enabled.

options:
  name:
    description:
      - The name of the box to manage
    required: true
    type: str

  os:
    description:
      - The OS of the box to create
    required: false
    type: str
    default: OS of frontend

  state:
    description:
      - If present, then a box will be added if it doesn't exist
      - If present and the box exists but the OS is different, the box will be removed and re-added with the updated OS.
      - If absent, then the box will be removed
    type: str
    choices: [ absent, present ]
    default: present
"""

EXAMPLES = """
- name: Add a box default
  stacki_box:
    name: foo

- name: Remove a box
  stacki_box:
    name: foo
    state: absent
"""

RETURN = """ # """

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError


def main():
	# Define the arguments for this module
	argument_spec = dict(
		name=dict(type="str", required=True),
		os=dict(type="str", required=False),
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

	# Fetch our box info from Stacki
	try:
		boxes = run_stack_command("list.box", [module.params["name"]])
	except StackCommandError as e:
		# If box doesn't exist, it will raise an error
		boxes = []

	if len(boxes) > 1:
		# No more than one box should match
		module.fail_json(msg="error - more than one box matches name", **result)

	try:
		# Are we adding or removing?
		if module.params["state"] == "present":
			args = [module.params["name"]]
			if module.params["os"]:
				args.append("os="+module.params["os"])

			if len(boxes) == 0:
				# Add a new box
				args = [module.params["name"]]
				if module.params["os"]:
					args.append("os="+module.params["os"])

				run_stack_command("add.box", args)
				result["changed"] = True

			elif module.params["os"] and module.params["os"] != boxes[0]["os"]:
				# Try to make the OS match. Might throw an error if the box has hosts attached.
				run_stack_command("remove.box", [module.params["name"]])
				run_stack_command("add.box", args)
				result["changed"] = True

		else:
			# Only remove a box that actually exists
			if len(boxes):
				run_stack_command("remove.box", [module.params["name"]])
				result["changed"] = True

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
