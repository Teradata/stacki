# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.stacki import run_stack_command, StackCommandError

DOCUMENTATION = """
module: stacki_host_info
short_description: Return the groups that hosts are in 
description:
    - If host is supplied, returns information about the single host
    - If group(s) is supplied, returns information about all the hosts in the group(s)
options:
    host:
        description:
            - The name of the host
        required: false
    group:
        description:
            - The name(s) of the groups 
        required: false
"""

EXAMPLES = """
"""

RETURN = """
"""


def run_module():
    argument_spec = dict(
        host=dict(type="str", required=False, default=None),
        group=dict(type="str", required=False, default=None)
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    results = {
        "changed": False,
        "hostgroups": list()
    }

    if module.check_mode:
        module.exit_json(**results)

    args = list()

    if module.params["host"]:
        args.append(module.params["host"])
    if module.params["group"]:
        groups = module.params["group"].split(',')
        args.append(module.params["group"])

    print(args)

    try:
        for host_group in run_stack_command("list.host.group", args):
            host_group["groups"] = host_group["groups"].split()

            results["hostgroups"].append(host_group)

    except StackCommandError as e:
        module.fail_json(msg=e.message, **results)

    module.exit_json(**results)


if __name__ == "__main__":
    run_module()
