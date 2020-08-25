# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_box_info
short_description: Return data about Stacki boxes
description:
  - If name is supplied, returns data about a single box
  - If name is not supplied, returns data about all boxes in the system

options:
  name:
    description:
      - The name of the box to return data about
    required: false
"""

EXAMPLES = """
- name: Get box default
  stacki_box_info:
    name: default
  register: default_box

- name: Get all boxes
  stacki_box_info:
  register: boxes
"""

RETURN = """
boxes:
  description:
    - List of boxes
  returned: on success
  type: complex
  contains:
    name:
      description:
        - Name of the box
      type: str

    os:
      description:
        - OS of the box
      type: str

    pallets:
      description:
        - Pallets in the box
      type: list
      elements: str

    carts:
      description:
        - Carts in the box
      type: list
      elements: str

    repos:
      description:
        - Repos in the box
      type: list
      elements: str
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
		"boxes": []
	}

	# Bail if the user is just checking syntax of their playbook
	if module.check_mode:
		module.exit_json(**result)

	# Fetch our box info from Stacki
	args = []
	if module.params["name"]:
		args.append(module.params["name"])

	try:
		for box in run_stack_command("list.box", args):
			# Split pallets, carts, and repos into lists
			box["pallets"] = box["pallets"].split()
			box["carts"] = box["carts"].split()
			box["repos"] = box["repos"].split()

			# Add it to the results
			result["boxes"].append(box)

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()