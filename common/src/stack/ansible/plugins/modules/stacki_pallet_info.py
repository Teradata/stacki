# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError

DOCUMENTATION = """
module: stacki_pallet_info
short_description: Return data about pallets in Stacki
description:
    - If name is supplied, returns information about the single pallet
    - If name is not supplied, returns information about all the pallets in the system
options:
    name:
        description:
            - The name of the pallet 
        required: false
"""

EXAMPLES = """
- name: Get info on all the pallets
      stacki_pallet_info:
      register: result

- name: Get the stacki pallet info
  stacki_pallet_info:
    name: stacki
  register: result
"""

RETURN = """
pallets:
    description:
        - List of pallets on the frontend
    returned: on success
    type: complex
    contains:
        name:
            description:
                - Name of the pallet
            type: str
        
        version:
            description:
                - Version of the pallet
            type: str
        
        release:
            description:
                - Release of the pallet
            type: str
            
        arch: 
            description:
                - Architecture of the pallet
            type: str
            
        os:
            description:
                - OS the pallet works with
            type: str
        
        boxes:
            description:
                - Boxes the pallet is in
            type: list
            elements: str
"""


def main():
    argument_spec = dict(
        name=dict(type="str", required=False, default=None)
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    results = {
        "changed": False,
        "pallets": []
    }

    if module.check_mode:
        module.exit_json(**results)

    args = []
    if module.params["name"]:
        args.append(module.params["name"])

    try:
        for pallet in run_stack_command("list.pallet", args):
            pallet["boxes"] = pallet["boxes"].split()

            results["pallets"].append(pallet)

    except StackCommandError as e:
        module.fail_json(msg=e.message, **results)

    module.exit_json(**results)


if __name__ == "__main__":
    main()
