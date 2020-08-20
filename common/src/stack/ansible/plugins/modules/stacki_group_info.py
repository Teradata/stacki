# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError

DOCUMENTATION = """
module: stacki_group_info
short_description: Return data about Stacki groups
description: List the current groups and the number of member hosts in each.
"""

EXAMPLES = """
- name: Get info on all the groups
  stacki_group_info:
  register: result
"""

RETURN = """
groups:
  description:
    - List of groups
  returned_on: success
  type: complex
  contains:
    group:
      description:
        - Name of the group
      type: str
    hosts:
      description:
        - List of hosts in the given group
       type: list
       elements: str
"""


def main():
    # Create our module object
    module = AnsibleModule(
        argument_spec=dict(),
        supports_check_mode=True
    )

    # Initialize a blank result
    result = {
        "changed": False,
        "groups": []
    }

    # Bail if the user is just checking syntax of their playbook
    if module.check_mode:
        module.exit_json(**result)

    try:
        for group in run_stack_command("list.group"):
            group["hosts"] = group["hosts"].split()

            # Add it to the results
            result["groups"].append(group)

    except StackCommandError as e:
        # Fetching the data failed
        module.fail_json(msg=e.message, **result)

    # Return our data
    module.exit_json(**result)


if __name__ == "__main__":
    main()
