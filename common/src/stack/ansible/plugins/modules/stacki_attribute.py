# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

DOCUMENTATION = """
module: stacki_attribute
short_description: Manage Stacki attributes
description:
  - Add, modify, and remove Stacki attributes

options:
  name:
    description:
      - The name of the scoped item to manage
    type: str
    required: false

  scope:
    description:
      - The scope of the attribute to manage
    type: str
    required: false
    choices: ['global', 'appliance', 'os', 'environment', 'host']
    default: global

  attr:
    description:
      - The name of the attribute to manage, in the given scope
    required: true
    type: str

  value:
    description:
      - The value to assign to the attribute
    required: When state is present
    type: str

  shadow:
    description:
      - Is the attribute in the shadow database (only readable by root and apache)
    type: bool
    required: false
    default: no

  state:
    description:
      - If present, then an attribute will be added (if needed) and value set to match
      - If absent, then the attribute will be removed
    type: str
    choices: [ absent, present ]
    default: present
"""

EXAMPLES = """
- name: Add a global attribute
  stacki_attribute:
    attr: global_attr
    value: test

- name: Update the global attribute
  stacki_attribute:
    attr: global_attr
    value: foo

- name: Add a shadow host attribute
  stacki_attribute:
    name: backend-0-0
    scope: host
    attr: my_secret
    value: foo
    shadow: yes

- name: Remove a shadow host attribute
  stacki_attribute:
    name: backend-0-0
    scope: host
    attr: my_secret
    shadow: yes
    state: absent
"""

RETURN = """ # """

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
		attr=dict(type="str", required=True),
		value=dict(type="str", required=False, default=None),
		shadow=dict(type="bool", required=False, default=False),
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

	# Make sure we have a name if scope isn't global
	if not module.params["name"] and module.params["scope"] != "global":
		module.fail_json(msg="error - name is required for non-global scope", **result)

	# Make sure value is provided if state isn't absent
	if not module.params["value"] and module.params["state"] != "absent":
		module.fail_json(msg="error - value is required", **result)

	# Bail if the user is just checking syntax of their playbook
	if module.check_mode:
		module.exit_json(**result)

	# Fetch our attribute info from Stacki
	args = []
	if module.params["name"]:
		args.append(module.params["name"])

	for field in ("scope", "attr"):
		args.append(f"{field}={module.params[field]}")

	attributes = run_stack_command("list.attr", args)

	if len(attributes) > 1:
		# No more than one attribute should match
		module.fail_json(msg="error - more than one attribute matches attr", **result)

	# Make sure the shadow state matches a returned attr
	attribute = None
	if len(attributes):
		# The returned attribute type has to match the shadow flag
		if module.params["shadow"] and attributes[0]["type"] == "shadow":
			attribute = attributes[0]
		elif not module.params["shadow"] and attributes[0]["type"] == "var":
			attribute = attributes[0]

	try:
		# Are we adding or removing?
		if module.params["state"] == "present":
			# Do we need to add or modify the attribute?
			if attribute is None or attribute["value"] != module.params["value"]:
				# Append the args missing to the existing list
				for field in ("value", "shadow"):
					args.append(f"{field}={module.params[field]}")

				# Create or update the attribute
				run_stack_command("set.attr", args)
				result["changed"] = True
		else:
			# Do we have an attribute to remove?
			if attribute:
				# Append the shadow arg to our existing list
				args.append(f'shadow={module.params["shadow"]}')

				# Remove the attribute
				run_stack_command("remove.attr", args)
				result["changed"] = True

	except StackCommandError as e:
		# Fetching the data failed
		module.fail_json(msg=e.message, **result)

	# Return our data
	module.exit_json(**result)


if __name__ == "__main__":
	main()
