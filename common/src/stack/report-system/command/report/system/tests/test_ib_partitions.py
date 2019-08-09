import pytest
from stack import api
from collections import defaultdict


class TestIbPartitions:
	"""
	Test if the ib partitions and their members are
	in the Stacki database are the same as what
	the ib switch says it has
	"""
	ib_switches = []
	for switch in api.Call('list host attr a:switch'):
		if switch['attr'] == 'switch_type' and switch['value'] == 'infiniband':
			ib_switches.append(switch['host'])

	@pytest.mark.parametrize('switch', ib_switches)
	def test_ib_partitions(self, switch):
		"""
		Test IB partitions have the same value
		in the database and switch.
		"""

		part_errors = []
		errors = []
		cmd = 'list switch partition'
		stacki_ib_part = {}
		actual_ib_part = {}

		for part in api.Call(f'{cmd} {switch}'):
			# Filter out values used for keys
			part_val = {k: v for k, v in part.items() if v != part['partition']}
			stacki_ib_part[part['partition']] = part_val

		# Same as above but for values actually on the ib switch
		for part in api.Call(f'{cmd} {switch}', args = ['expanded=true']):
			part_val = {k: v for k, v in part.items() if v != part['partition']}
			actual_ib_part[part['partition']] = part_val

		# Make lists of partitions the same order
		part_diff = [part for part in actual_ib_part if part not in stacki_ib_part]
		if part_diff:
			errors.append(f'Infiniband switch {switch} found with partitions not defined in Stacki: {",".join(part_diff)}')
			assert not errors, errors

		# Check each partitiion and then check each value of
		# each partition is the same
		for stacki_part, values in stacki_ib_part.items():

			# The database reports blank when ipoib is false so fill
			# it in to maintain parity with what the switch reports
			if values['options'] == '':
				values['options'] = 'ipoib=False'

			# Check partition is actually on the switch
			try:
				actual_part = actual_ib_part[stacki_part]

			except KeyError:
				part_errors.append(f'Could not find partition for host {stacki_part} on switch {switch}')
				continue

			# Check partition values
			for stacki_key in values:
				if stacki_key not in actual_part:
					part_errors.append(f'Could not find value {stacki_key} on switch {switch}')
				elif actual_part[stacki_key] != values[stacki_key]:
					msg = f'Host {values["host"]} found with {stacki_key} value {actual_part[stacki_key]} but should be {values[stacki_key]}'
					part_errors.append(msg)
		if part_errors:
			errors.append(f'Infiniband switch {switch} found with partition info different from Stacki:')
			errors.append('\n'.join(part_errors))

		assert not errors, errors

	@pytest.mark.parametrize('switch', ib_switches)
	def test_ib_partition_members(self, switch):
		"""
		Test IB partition members have the same value
		in the database and switch.
		"""

		member_errors = []
		errors = []
		cmd = 'list switch partition member'
		stacki_ib_mem = defaultdict(dict)
		actual_ib_mem = defaultdict(dict)

		for mem in api.Call(f'{cmd} {switch}', args = ['expanded=true']):

			# Filter out the values we are using for keys
			mem_val = {k: v for k, v in mem.items() if v != mem['host'] or v != mem['device']}

			# Assign per ib interface values as a host might have more than one
			# ib interface on a switch
			stacki_ib_mem[mem['host']][mem['device']] = mem_val

		for mem in api.Call(f'{cmd} {switch}', args = ['expanded=true', 'source=switch']):

			# Same but for the values being reported by the switch itself
			mem_val = {k: v for k, v in mem.items() if v != mem['host'] or v != mem['device']}
			actual_ib_mem[mem['host']][mem['device']] = mem_val

		member_diff = [mem for mem in actual_ib_mem if mem not in stacki_ib_mem]
		if member_diff:
			errors.append(f'Infiniband switch {switch} found with ib members not defined in Stacki: {",".join(member_diff)}')
			assert not errors, errors

		# Check every host member of each partition
		for stacki_member, mem_devices in stacki_ib_mem.items():
			if stacki_member not in actual_ib_mem:
				member_errors.append(f'Could not find partition member for host {stacki_member} on switch {switch}')
				continue
			actual_member = actual_ib_mem[stacki_member]

			# Check every device of the host
			for device, mem_val in mem_devices.items():

				# The command gets it's host info by matching the guid from the switch to
				# the database, therefore the host name would be blank if it didn't match
				# so we don't need to check it here, instead it would be caught above as
				# a member not in the database
				actual_member.pop('guid', None)
				mem_val.pop('guid', None)

				# Check if the key is present on the switch and in the database
				if device not in actual_member:
					member_errors.append(f'Interface {device} not found on switch {switch} for host {stacki_member}')
					continue

				# Check each devices member attributes
				for stacki_key, stacki_value in mem_val.items():

					# Check the value exists on the switch
					if stacki_key not in actual_member[device]:
						msg = [
							f'Could not find member value {stacki_key} ',
							f'for host {stacki_member} on switch {switch}'
						]
						member_errors.append(''.join(msg))
						continue

					# Check the values are the same
					actual_value = actual_member[device][stacki_key]
					if stacki_value != actual_value:
						msg = [
							f'Host {stacki_member} found with {stacki_key} value ',
							f'{actual_value} but should be {stacki_value}'
						]
						member_errors.append(''.join(msg))
		if member_errors:
			errors.append(f'Infiniband switch {switch} found with partition members info different from Stacki:')
			errors.append('\n'.join(member_errors))
		assert not errors, errors
