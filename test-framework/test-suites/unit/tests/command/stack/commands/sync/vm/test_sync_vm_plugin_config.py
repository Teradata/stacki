import pytest
from unittest.mock import create_autospec, patch, call, ANY
from stack.commands import DatabaseConnection
from stack.commands.sync.vm.plugin_config import Plugin, VmException
from stack.commands.sync.vm import Command
from stack.bool import str2bool

class TestSyncVmConfig:
	def mock_vm_exception(self, *args):
		raise VmException('Oh no something went wrong!')

	@pytest.fixture
	def mock_sync_config_plugin(self):
		"""
		A fixture for mocking Plugin instances
		"""

		mock_command = create_autospec(
			spec = Command,
			instance = True
		)

		mock_command.db = create_autospec(
			spec = DatabaseConnection,
			spec_set = True,
			instance = True
		)

		return Plugin(mock_command)

	# Test various successful input to the plugin
	# returns the expected output
	# 1. Single host
	# 2. Multiple hosts with different statuses
	#    and disk types
	CONFIG_ADD = [
		(
			{'foo': {
				'virtual machine': 'foo',
				'hypervisor': 'hypervisor-foo',
				'pending deletion': 'False',
				'status': 'off'
				}
			},
			{'foo': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'False'
				}]
			}
		),
		(
			{'foo': {
					'virtual machine': 'foo',
					'hypervisor': 'hypervisor-foo',
					'pending deletion': 'False',
					'status': 'off'
					},
				 'bar': {
					'virtual machine': 'bar',
					'hypervisor': 'hypervisor-bar',
					'pending deletion': 'False',
					'status': 'off'
					},
				 'baz': {
					'virtual machine': 'baz',
					'hypervisor': 'hypervisor-baz',
					'pending deletion': 'False',
					'status': 'off'
					}
			},
			{'foo': [
						{
						'Name': 'disk1',
						'Type': 'disk',
						'Image Name': 'disk_name',
						'Location': 'loc',
						'Pending Deletion': 'False'
					}
				],
			 'bar': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'False'
			 }],
			 'baz': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'False'
				}]
			})
	]

	@patch('stack.commands.sync.vm.plugin_config.Hypervisor')
	@pytest.mark.parametrize('vm_hosts, vm_disks', CONFIG_ADD)
	def test_sync_vm_config_start_domain(
		self,
		mock_hypervisor,
		mock_sync_config_plugin,
		vm_hosts,
		vm_disks
	):
		"""
		Test starting a domain on a hypervisor
		when running the plugin
		"""

		mock_sync_config_plugin.owner.call.return_value = vm_hosts.values()

		# Use the real str2bool when the
		# mock plugin calls it
		mock_sync_config_plugin.owner.str2bool.side_effect = str2bool
		hypervisor = mock_hypervisor.return_value

		# Call the plugin
		actual_output = mock_sync_config_plugin.run((vm_hosts, vm_disks, False, True, False, True))

		# Check mocked functions were called with
		# the expected args and the right amount
		# of times
		mock_sync_config_plugin.owner.delete_pending_disk.assert_not_called()
		off_hosts = [host for host, values in vm_hosts.items() if values['status'] == 'off']
		assert hypervisor.autostart.call_args_list == [call(host, True) for host in off_hosts]
		assert hypervisor.start_domain.call_args_list == [call(host) for host in off_hosts]
		assert actual_output == []

	# Input for testing removing disks/VM's
	# 1. Test removing a single VM's but not
	# 	 its disk
	# 2. Test removing multiple VM's
	#    with different combos of disks/hosts
	CONFIG_REMOVE = [
		(
			{'foo': {
				'virtual machine': 'foo',
				'hypervisor': 'hypervisor-foo',
				'pending deletion': 'True',
				'status': 'off'
				}
			},
			{'foo': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'False'
				}]
			}
		),
		(
			{'foo': {
				'virtual machine': 'foo',
				'hypervisor': 'hypervisor-foo',
				'pending deletion': 'True',
				'status': 'on'
				}
			},
			{'foo': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'True'
				}]
			}
		),
		(
			{'foo': {
					'virtual machine': 'foo',
					'hypervisor': 'hypervisor-foo',
					'pending deletion': 'True',
					'status': 'off'
					},
				 'bar': {
					'virtual machine': 'bar',
					'hypervisor': 'hypervisor-bar',
					'pending deletion': 'False',
					'status': 'off'
					},
				 'baz': {
					'virtual machine': 'baz',
					'hypervisor': 'hypervisor-baz',
					'pending deletion': 'True',
					'status': 'undefined'
					}
			},
			{'foo': [
						{
						'Name': 'disk1',
						'Type': 'disk',
						'Image Name': 'disk_name',
						'Location': 'loc',
						'Pending Deletion': 'False'
					}
				],
			 'bar': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'True'
			 }],
			 'baz': [{
					'Name': 'disk1',
					'Type': 'mountpoint',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'True'
				}]
			})
	]
	@patch('stack.commands.sync.vm.plugin_config.Hypervisor', autospec=True)
	@pytest.mark.parametrize('vm_hosts, vm_disks', CONFIG_REMOVE)
	def test_sync_vm_config_remove_domain(
		self,
		mock_hypervisor,
		mock_sync_config_plugin,
		vm_hosts,
		vm_disks
	):
		"""
		Test the plugin removes virtual machines
		from the database when marked for it
		"""

		mock_sync_config_plugin.owner.call.return_value = vm_hosts.values()

		# Use the real str2bool when the
		# mock plugin calls it
		mock_sync_config_plugin.owner.str2bool.side_effect = str2bool
		hypervisor = mock_hypervisor.return_value

		# Call the plugin
		actual_output = mock_sync_config_plugin.run((vm_hosts, vm_disks, False, True, False, True))

		# Check mocked functions were called with
		# the expected args and the right amount
		# of times
		expect_delete_disk = []
		expect_delete_vm = []
		delete_disk = mock_sync_config_plugin.owner.delete_pending_disk.call_args_list

		# Gather argument calls we expect for
		# delete_pending_disk
		for host, disks in vm_disks.items():
			for disk in disks:
				if str2bool(disk['Pending Deletion']):
					expect_delete_disk.append(call(host, disk['Name']))
		assert delete_disk == expect_delete_disk

		delete_vm = mock_sync_config_plugin.owner.delete_pending_vm.call_args_list

		# Gather argument calls we expect for
		# delete_pending_vm
		for host, values in vm_hosts.items():
			if str2bool(values['pending deletion']) and values['status'] != 'on':
				expect_delete_vm.append(call(host))
		assert delete_vm == expect_delete_vm
		assert actual_output == []

	@patch('stack.commands.sync.vm.plugin_config.Hypervisor', autospec=True)
	def test_sync_vm_config_except(self, mock_hypervisor, mock_sync_config_plugin):
		"""
		Test how the plugin handles an exception
		as we expect it to
		"""

		hypervisor = mock_hypervisor.return_value
		hypervisor.autostart.side_effect = self.mock_vm_exception
		mock_sync_config_plugin.owner.str2bool.side_effect = str2bool
		vm_disks = {}
		vm_hosts = {'foo': {
			'virtual machine': 'foo',
			'hypervisor': 'bar',
			'status': 'off',
			'pending deletion': 'True'
		}}
		mock_sync_config_plugin.owner.call.return_value = vm_hosts.values()
		except_msg = 'Could not start VM foo:\nOh no something went wrong!'
		actual_output = mock_sync_config_plugin.run((vm_hosts, vm_disks, False, True, False, True))
		hypervisor.autostart.assert_called_once_with('foo', True)
		assert actual_output == [except_msg]

	@patch('stack.commands.sync.vm.plugin_config.Hypervisor', autospec=True)
	@patch('stack.commands.sync.vm.plugin_config._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	def test_sync_vm_config_disk_exists(
		self,
		mock_completed_process,
		mock_exec,
		mock_hypervisor,
		mock_sync_config_plugin
	):
		"""
		Test that the config plugin
		keeps a disk in the database
		if it's present on the hypervisor
		and marked for deletion
		"""

		hypervisor = mock_hypervisor.return_value
		mock_sync_config_plugin.owner.str2bool.side_effect = str2bool

		# Simulate finding the disk image file
		# on the remote hypervisor using ls's
		# return code
		mock_completed_process.returncode = 0
		mock_exec.return_value = mock_completed_process
		vm_disks = {
			 'foo': [{
					'Name': 'disk1',
					'Type': 'disk',
					'Image Name': 'disk_name',
					'Location': 'loc',
					'Pending Deletion': 'True'
				}]
		}
		vm_hosts = {'foo': {
			'virtual machine': 'foo',
			'hypervisor': 'bar',
			'status': 'off',
			'pending deletion': 'True'
		}}
		mock_sync_config_plugin.owner.call.return_value = vm_hosts.values()
		actual_output = mock_sync_config_plugin.run((vm_hosts, vm_disks, False, True, False, True))

		# We expect the disk to not have been deleted
		# as the plugin will not delete it if the
		# image is still present on the hypervisor
		mock_sync_config_plugin.owner.delete_pending_disk.assert_not_called()
		assert actual_output == []
