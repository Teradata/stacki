# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError

DOCUMENTATION = """
module: stacki_network_info
short_description: Return data about networks in Stacki
description:
    - If name is supplied, returns information about the single network
    - If name is not supplied, returns information about all the networks in the system
options:
    name:
        description:
            - The name of the network 
        required: false
"""

EXAMPLES = """
- name: Get info on all the networks
  stacki_network_info:
  register: result

- name: Get the primary netwrok info
  stacki_network_info:
    name: primary
  register: result
"""

RETURN = """
networks:
    description:
        - List of networks
    returned: on success
    type: complex
    contains:
        network:
            description:
                - Name of the network
            type: str

        address:
            description:
                - Address of the network
            type: str

        mask:
            description:
                - Mask of the network
            type: str

        gateway:
            description:
                - Gateway of the network
            type: str

        mtu:
            description:
                - MTU of the network
            type: int

        zone:
            description:
                - Zone of the network
            type: str

        dns:
            description:
                - Is DNS enabled on the network
            type: boolean

        pxe:
            description:
                - Is PXE enabled on the network
            type: boolean
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
        "networks": []
    }

    if module.check_mode:
        module.exit_json(**results)

    args = []
    if module.params["name"]:
        args.append(module.params["name"])

    try:
        results["networks"] = run_stack_command("list.network", args)

    except StackCommandError as e:
        module.fail_json(msg=e.message, **results)

    module.exit_json(**results)


if __name__ == "__main__":
    main()