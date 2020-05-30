# @copyright@
# Copyright (c) 2006 - 2020 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = """
    inventory: stacki
    short_description: Returns hosts, groups, and vars from Stacki
    description:
        - Reads hosts info and attributes from Stacki.
        - Returns host groups based on standard Stacki host selectors.
        - Hosts have attributes attached as vars with a `stacki_` prefix.
"""

EXAMPLES = """
# Directly target hosts
ansible backend-0-0 -m ping

# Using standard host selectors
ansible a_backend -m ping

# In Ansible playbooks, you can use the selectors in the `hosts` attribute:
- name: Ping my backends
  hosts: a_backend
  tasks:
    - ping:

# You can also use the --limit flag to `ansible-playbook`
ansible-playbook --limit b_default playbook.yml

# The following types of groups are created, with the UPPERCASE replaced
# with the Stacki primitive:
- a_APPLIANCE
- e_ENVIRONMENT
- o_OS
- b_BOX
- g_GROUP
- r_RACK

# All the attributes for a host are available as Ansible host vars, with
# a `stacki_` prefix:
- name: Ping managed hosts
  hosts: all
  tasks:
    - ping:
      when: stacki_managed

# To list all the inventory hosts, groups, and vars run:
ansible-inventory --list
"""

from collections import defaultdict

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.inventory import BaseInventoryPlugin
import stack.api


class InventoryModule(BaseInventoryPlugin):
	NAME = "stacki"

	def verify_file(self, path):
		return path.endswith("@stacki")

	def parse(self, inventory, loader, path, cache=True):
		super(InventoryModule, self).parse(inventory, loader, "@stacki")

		# Carve up the host info
		appliances = defaultdict(list)
		oses = defaultdict(list)
		boxes = defaultdict(list)
		racks = defaultdict(list)
		environments = defaultdict(list)
		groups = defaultdict(list)

		for row in stack.api.Call("list host"):
			# Add the host
			self.inventory.add_host(row["host"])

			# Record the groups it will belong to
			appliances[row["appliance"]].append(row["host"])
			oses[row["os"]].append(row["host"])
			boxes[row["box"]].append(row["host"])
			racks[row["rack"]].append(row["host"])

			if row["environment"]:
				environments[row["environment"]].append(row["host"])

		# Get the host groups
		for row in stack.api.Call("list host group"):
			for group in row["groups"].split():
				groups[group].append(row["host"])

		# Add the 'colon' selector groups
		selectors = (
			('a', appliances),
			('o', oses),
			('b', boxes),
			('r', racks),
			('e', environments),
			('g', groups)
		)

		for selector, hash_table in selectors:
			for key in hash_table:
				group = "%s_%s" % (selector, key)
				self.inventory.add_group(group)

				for host in hash_table[key]:
					self.inventory.add_child(group, host)

		# Add the host attrs
		for row in stack.api.Call("list host attr"):
			value = row["value"]

			# Convert boolean-like strings to Python booleans
			try:
				if value.lower() in ("true", "on"):
					value = True
				elif value.lower() in ("false", "off"):
					value = False
			except AttributeError:
				# Value wasn't string-like
				pass

			self.inventory.set_variable(row["host"], "stacki_%s" % row["attr"], value)

		# Add VM values for virtual machine hosts
		for row in stack.api.Call("list vm"):
			name = row["virtual machine"]

			self.inventory.set_variable(name, "stacki_vm_cpu", row["cpu"])
			self.inventory.set_variable(name, "stacki_vm_memory", row["memory"])
			self.inventory.set_variable(name, "stacki_vm_hypervisor", row["hypervisor"])

		# Add VM storage info
		for row in stack.api.Call("list vm storage"):
			host = row["Virtual Machine"]
			name = row["Name"]

			self.inventory.set_variable(host, f"stacki_vm_disk_{name}_name", row["Name"])
			self.inventory.set_variable(host, f"stacki_vm_disk_{name}_type", row["Type"])
			self.inventory.set_variable(host, f"stacki_vm_disk_{name}_location", row["Location"])
			self.inventory.set_variable(host, f"stacki_vm_disk_{name}_size", row["Size"])
			self.inventory.set_variable(host, f"stacki_vm_disk_{name}_image", row["Image Name"])
			self.inventory.set_variable(host, f"stacki_vm_disk_{name}_mountpoint", row["Mountpoint"])
