# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError

DOCUMENTATION = """
module: stacki_network_info
short_description: 
"""

EXAMPLES = """
"""

RETURN = """
"""


def run_module():
    argument_spec = dict(
        name=dict(type="str", required=False, default=None)
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    results = {
        "changed": False,
        "networks": list()
    }

    if module.check_mode:
        module.exit_json(**results)

    args = list()

    if module.params["name"]:
        args.append(module.params["name"])

    try:
        for network in run_stack_command("list.network", args):
            for key, value in network.items():
                network[key] = str(value).split()

            results["networks"].append(network)

    except StackCommandError as e:
        module.fail_json(msg=e.message, **results)

    module.exit_json(**results)


def main():
    run_module()


if __name__ == "__main__":
    main()
