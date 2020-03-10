import pytest
import shlex
from unittest.mock import create_autospec, patch, call, ANY, PropertyMock
from stack.commands import DatabaseConnection
from stack.commands.sync.vm.plugin_storage import Plugin, VmException
from stack.commands.sync.vm import Command
from stack.bool import str2bool
from pathlib import Path

class TestSyncVmStorage:
	def mock_vm_exception(self, *args, **kwargs):
		raise VmException('Oh no something went wrong!')

	@pytest.fixture
	def mock_sync_storage_plugin(self):
		"""
		A fixture for mocking Plugin instances
		"""

		mock_command = create_autospec(
			spec=Command,
			instance=True
		)

		mock_command.db = create_autospec(
			spec=DatabaseConnection,
			spec_set=True,
			instance=True
		)

		return Plugin(mock_command)

	# Test various vm storage types are added:
	# 1. A VM with a single disk
	# 2. A VM with an image from a compressed
	#	 archive
	# 3. A VM with a pre-made image
	ADD_DISK_ARGS = [
		(
			'foo',
			'hypervisor-foo',
			{
				'Name': 'disk1',
				'Type': 'disk',
				'Image Name': 'disk_name',
				'Location': 'loc',
				'Pending Deletion': 'False',
				'Size': 100
			},
			True
		),
		(
			'baz',
			'hypervisor-baz',
			{
				'Name': 'disk1',
				'Type': 'image',
				'Image Name': 'disk.qcow2',
				'Location': 'loc',
				'Pending Deletion': 'False'
			},
			True
		)
	]
	@patch.object(Plugin, 'pack_ssh_key', autospec=True)
	@patch.object(Plugin, 'copy_remote_file', autospec=True)
	@patch('stack.commands.sync.vm.plugin_storage.Hypervisor', autospec=True)
	@pytest.mark.parametrize('host, hypervisor_name, disk, sync_ssh', ADD_DISK_ARGS)
	def test_sync_storage_plugin_add_disk(
		self,
		mock_hypervisor,
		mock_copy_file,
		mock_pack_ssh,
		mock_sync_storage_plugin,
		host,
		hypervisor_name,
		disk,
		sync_ssh
	):
		hypervisor = mock_hypervisor.return_value.__enter__.return_value
		hypervisor.add_pool.return_value = True
		mock_pack_ssh.return_value = []
		mock_copy_file.return_value = None

		# Setup values
		disk_location = Path(disk['Location'])
		image_name = Path(disk['Image Name']).name

		output = mock_sync_storage_plugin.add_disk(
			host,
			hypervisor_name,
			disk,
			sync_ssh,
			True
		)

		# Check different methods were called based
		# on the disk type
		if disk['Type'] == 'disk':
			hypervisor.add_pool.assert_called_once_with(
				disk_location.name,
				disk_location
			)
			hypervisor.add_volume.assert_called_once_with(
				disk['Image Name'],
				disk_location,
				disk_location.name,
				disk['Size']
			)
			mock_pack_ssh.assert_not_called()

		elif disk['Type'] == 'image':
			copy_file = disk['Image Name']

			mock_copy_file.assert_called_once_with(
				ANY,
				copy_file,
				disk_location,
				hypervisor_name
			)
			if sync_ssh:
				mock_pack_ssh.assert_called_once_with(ANY, host, hypervisor_name, disk)

		assert output == []

	@patch('stack.commands.sync.vm.plugin_storage.Hypervisor', autospec=True)
	def test_sync_storage_plugin_add_disk_vm_except(
		self,
		mock_hypervisor,
		mock_sync_storage_plugin
	):
		"""
		Test the add_disk method returns an error
		when a VmException is raised
		"""

		hypervisor = mock_hypervisor.return_value.__enter__.return_value
		hypervisor.add_pool.side_effect = self.mock_vm_exception
		disk = {
				'Name': 'disk1',
				'Type': 'disk',
				'Image Name': 'disk_name',
				'Location': 'loc',
				'Pending Deletion': 'False',
				'Size': 100
		}
		output = mock_sync_storage_plugin.add_disk(
			'foo',
			'hypervisor-foo',
			disk,
			True,
			True
		)
		assert output == ['Oh no something went wrong!']

	@patch.object(Plugin, 'pack_ssh_key', autospec=True)
	@patch.object(Plugin, 'copy_remote_file', autospec=True)
	def test_sync_storage_plugin_add_disk_copy_file_except(
		self,
		mock_copy_remote_file,
		mock_pack_ssh_key,
		mock_sync_storage_plugin
	):
		"""
		Test the add_disk method returns an error
		when an OSError is raised while copying
		files over to a hypervisor
		"""

		mock_copy_remote_file.return_value = 'Error while copying file'
		mock_pack_ssh_key.return_value = 'Key could not be copied'
		disk = {
				'Name': 'disk1',
				'Type': 'image',
				'Image Name': 'disk.qcow2',
				'Location': 'loc',
				'Pending Deletion': 'False',
				'Size': ''
		}
		output = mock_sync_storage_plugin.add_disk(
			'foo',
			'hypervisor-foo',
			disk,
			True,
			True
		)

		# Check the output matches the
		# error message we expect
		assert output == [
				'Error while copying file',
				'Failed to pack frontend ssh key: Key could not be copied'
		]

	def exec_return(self, mock_completed_process, mock_calls, *args, **kwargs):
		"""
		Helper function for giving different
		return codes for _exec based on the input args
		"""

		mock_completed_process.returncode = 1

		# Return a successful return code if the input
		# dict specifies it for the call to _exec
		for arg_text, success in mock_calls.items():
			if arg_text in args[0]:
				if success:
					mock_completed_process.returncode = 0
		return mock_completed_process

	# Test different disk types are removed:
	# 1. A disk volume in a managed hypervisor pool
	# 2. A pre-made disk image
	REMOVE_DISK_ARGS = [
		(
			'hypervisor-foo',
			{
				'Name': 'disk1',
				'Type': 'disk',
				'Image Name': 'disk_name',
				'Location': 'loc',
				'Pending Deletion': 'True',
				'Size': 100
			}
		),
		(
			'hypervisor-baz',
			{
				'Name': 'disk1',
				'Type': 'image',
				'Image Name': 'disk.qcow2',
				'Location': 'loc',
				'Pending Deletion': 'True'
			}
		)
	]
	@patch('stack.commands.sync.vm.plugin_storage.Hypervisor', autospec=True)
	@patch.object(Plugin, 'remove_remote_file', autospec=True)
	@pytest.mark.parametrize('hypervisor_name, disk', REMOVE_DISK_ARGS)
	def test_sync_storage_plugin_remove_disk(
		self,
		mock_remove_remote_file,
		mock_hypervisor,
		mock_sync_storage_plugin,
		hypervisor_name,
		disk
	):
		hypervisor = mock_hypervisor.return_value.__enter__.return_value
		mock_remove_remote_file.return_value = None
		output = mock_sync_storage_plugin.remove_disk(hypervisor_name, disk, True)

		# Check different methods were called
		# based on the disk type
		if disk['Type'] == 'disk':
			hypervisor.remove_volume.assert_called_once_with(disk['Location'], disk['Image Name'])
		elif disk['Type'] == 'image':
			file_loc = f'{disk["Location"]}/{disk["Image Name"]}'
			mock_remove_remote_file.assert_called_once_with(ANY, file_loc, hypervisor_name)
		assert output == []

	@patch('stack.commands.sync.vm.plugin_storage.Hypervisor', autospec=True)
	@patch.object(Plugin, 'remove_remote_file', autospec=True)
	def test_sync_storage_plugin_remove_disk_vm_except(
		self,
		mock_remove_remote_file,
		mock_hypervisor,
		mock_sync_storage_plugin
	):
		"""
		Test the remove_disk method returns an error
		when a VmException is raised
		"""

		hypervisor = mock_hypervisor.return_value.__enter__.return_value
		hypervisor.remove_volume.side_effect = self.mock_vm_exception
		disk = {
				'Name': 'disk1',
				'Type': 'disk',
				'Image Name': 'disk_name',
				'Location': 'loc',
				'Pending Deletion': 'False',
				'Size': 100
		}
		output = mock_sync_storage_plugin.remove_disk('hypervisor-foo', disk, True)
		assert output == ['Oh no something went wrong!']

	@patch.object(Plugin, 'remove_remote_file', autospec=True)
	def test_sync_storage_plugin_remove_disk_remove_file_except(
		self,
		mock_remove_remote_file,
		mock_sync_storage_plugin
	):
		"""
		Test the remove_disk method returns an error
		when its supposed to
		"""

		mock_remove_remote_file.return_value = 'Remove file error'
		disk = {
				'Name': 'disk1',
				'Type': 'image',
				'Image Name': 'disk.qcow2',
				'Location': 'loc',
				'Pending Deletion': 'False',
				'Size': ''
		}
		output = mock_sync_storage_plugin.remove_disk('hypervisor-foo', disk, True)
		assert output == ['Remove file error']

	# Test different hosts to the run method
	# 1. Single host with one disk
	# 2. Multiple hosts with varying amounts
	#    of disks
	RUN_ARGS = [
		(
			{
				'foo': {
					'hypervisor': 'hypervisor-foo'
				}
			},
			{
				'foo': [
					{
						'Name': 'disk1',
						'Type': 'disk',
						'Image Name': 'disk_name',
						'Location': 'loc',
						'Pending Deletion': 'True',
						'Size': 100
					}
				]
			},
			'hypervisor-foo'
		),
		(
			{
				'foo': {
					'hypervisor': 'hypervisor-foo'
				},
				'bar': {
					'hypervisor': 'hypervisor-bar'
				},
				'baz': {
					'hypervisor': 'hypervisor-baz'
				},
			},
			{
				'foo': [
					{
						'Name': 'disk1',
						'Type': 'disk',
						'Image Name': 'disk_name',
						'Location': 'loc',
						'Pending Deletion': 'True',
						'Size': 100
					}
				],
				'bar': [
					{
						'Name': 'disk1',
						'Type': 'image',
						'Image Name': 'disk_name.qcow2',
						'Location': 'loc',
						'Pending Deletion': 'False',
						'Size': ''
					}
				],
			},
			'hypervisor-foo'
		)
	]
	@patch.object(Plugin, 'add_disk', autospec=True)
	@patch.object(Plugin, 'remove_disk', autospec=True)
	@patch.object(Plugin, 'remove_pool', autospec=True)
	@patch.object(Plugin, 'remove_storage_dir', autospec=True)
	@pytest.mark.parametrize('hosts, host_disks, hypervisor', RUN_ARGS)
	def test_sync_storage_plugin_run(
		self,
		mock_remove_host_storage_dir,
		mock_remove_host_pool,
		mock_remove_disk,
		mock_add_disk,
		mock_sync_storage_plugin,
		hosts,
		host_disks,
		hypervisor
	):
		add_disks = {}
		delete_disks = {}

		# Also test any error messages returned by add_disk
		# and remove_disk are output
		mock_remove_disk.return_value = ['remove_disk errors!']
		mock_add_disk.return_value = ['add_disk errors!']
		expect_output = []

		# Create a dict of what disks
		# should be deleted and which
		# ones should be added
		for host, disks in host_disks.items():
			for disk in disks:
				host_hypervisor = hosts[host]['hypervisor']
				if str2bool(disk['Pending Deletion']):
					delete_disks[host_hypervisor] = disk
				else:
					add_disks[host] = (host_hypervisor, disk)
		mock_sync_storage_plugin.owner.str2bool.side_effect = str2bool

		# Run the plugin
		output = mock_sync_storage_plugin.run((hosts, host_disks, True, True, False, hypervisor))

		# Check disks marked for deletion are fed into
		# remove_disk and the return value contains the values
		# we expect
		for hypervisor_name, disk in delete_disks.items():
			mock_remove_disk.assert_any_call(ANY, hypervisor_name, disk,True)
			expect_output.append('remove_disk errors!')

		# Same for added disks
		for host, info in add_disks.items():
			mock_add_disk.assert_any_call(ANY, host, info[0], info[1], sync_ssh = True, debug = True)
			expect_output.append('add_disk errors!')
		assert sorted(output) == sorted(expect_output)

	@patch('subprocess.CompletedProcess', autospec=True)
	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	def test_sync_storage_plugin_pack_ssh_key(
		self,
		mock_exec,
		mock_completed_process,
		mock_sync_storage_plugin
	):
		"""
		Test the pack ssh key method
		makes the correct calls to _exec
		"""

		# Always have 0 be the return code value
		# to simulate all commands executing successfully
		mock_completed_process.returncode = 0
		mock_exec.return_value = mock_completed_process
		key_dir = '/tmp/foo_keys'

		disk = {
			'Name': 'disk1',
			'Type': 'disk',
			'Image Name': 'disk_name',
			'Location': 'loc',
			'Pending Deletion': 'True',
			'Size': 100
		}

		output = mock_sync_storage_plugin.pack_ssh_key('foo', 'hypervisor-foo', disk)

		# Make sure all commands executed
		# on the hypervisor are the correct
		# values
		expect_calls = [
			call(f'ssh hypervisor-foo "mkdir -p {key_dir}"', shlexsplit=True),
			call(f'scp /root/.ssh/id_rsa.pub hypervisor-foo:{key_dir}/frontend_key', shlexsplit=True),
			call(f'ssh hypervisor-foo "virt-copy-out -a loc/disk_name /root/.ssh/authorized_keys {key_dir}"',
				shlexsplit=True
			),
			call(f'ssh hypervisor-foo "cat {key_dir}/frontend_key >> {key_dir}/authorized_keys"',
				shlexsplit=True
			),
			call(f'ssh hypervisor-foo "virt-copy-in -a loc/disk_name {key_dir}/authorized_keys /root/.ssh/"',
				shlexsplit=True
			),
			call(shlex.split(f'ssh hypervisor-foo "rm -r {key_dir}"'))
		]
		assert output is None and mock_exec.call_args_list == expect_calls

	@patch('subprocess.CompletedProcess', autospec=True)
	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	def test_sync_storage_plugin_pack_ssh_key_error(
		self,
		mock_exec,
		mock_completed_process,
		mock_sync_storage_plugin
	):
		"""
		Test the pack ssh key method
		returns the stderr of commands
		executed on a hypervisor
		"""

		mock_completed_process.returncode = 1
		mock_completed_process.stderr = 'Error!'
		mock_exec.return_value = mock_completed_process

		disk = {
			'Name': 'disk1',
			'Type': 'disk',
			'Image Name': 'disk_name',
			'Location': 'loc',
			'Pending Deletion': 'True',
			'Size': 100
		}
		output = mock_sync_storage_plugin.pack_ssh_key('foo', 'hypervisor-foo', disk)

		# Check our mock stderr message
		# was returned
		assert output == 'Error!'

	@patch('pathlib.Path.is_file', autospec=True)
	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	def test_copy_remote_file(
		self,
		mock_completed_process,
		mock_exec,
		mock_is_file,
		mock_sync_storage_plugin,
	):

		exec_args = {
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/foo"': False,
			'scp foo baz:bar': True
		}
		mock_completed_process.stderr = 'Error!'

		# Call a helper function to assign the desired
		# return code values for each arg to _exec
		mock_exec.side_effect = lambda *args, **kwargs: self.exec_return(mock_completed_process, exec_args, *args, **kwargs)
		output = mock_sync_storage_plugin.copy_remote_file('foo', 'bar', 'baz')
		mock_is_file.assert_called_once_with(Path('foo'))

		assert mock_exec.call_args_list == [
			call('ssh baz "mkdir -p bar"', shlexsplit=True),
			call('ssh baz "ls bar/foo"', shlexsplit=True),
			call('scp foo baz:bar', shlexsplit=True)
		]

		assert not output

	@patch('pathlib.Path.is_file', autospec=True)
	def test_copy_remote_file_no_file(
		self,
		mock_is_file,
		mock_sync_storage_plugin
	):
		"""
		Test copy_remote_file returns an error
		when a given file doesn't exist
		"""

		mock_is_file.return_value = False
		error = mock_sync_storage_plugin.copy_remote_file('foo', 'bar', 'baz')
		mock_is_file.assert_called_once_with(Path('foo'))
		assert error == 'File foo not found to transfer'

	@patch('pathlib.Path.is_file', autospec=True)
	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	def test_copy_remote_file_no_directory(
		self,
		mock_completed_process,
		mock_exec,
		mock_is_file,
		mock_sync_storage_plugin
	):
		mock_completed_process.stderr = 'Error!'
		exec_args = {
			'ssh baz "mkdir -p bar"': False
		}
		mock_exec.side_effect = lambda *args, **kwargs: self.exec_return(mock_completed_process, exec_args, *args, **kwargs)
		error = mock_sync_storage_plugin.copy_remote_file('foo', 'bar', 'baz')
		mock_is_file.assert_called_once_with(Path('foo'))
		mock_exec.call_args_list == [
			call('ssh baz "mkdir -p bar"', shlexsplit=True)
		]
		assert error == 'Could not create file folder bar on baz:\nError!'

	@patch('pathlib.Path.is_file', autospec=True)
	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	def test_copy_remote_file_no_copy(
		self,
		mock_completed_process,
		mock_exec,
		mock_is_file,
		mock_sync_storage_plugin
	):
		exec_args = {
			'ssh baz "mkdir -p bar"': True,
			'ssh baz "ls bar/foo"': False,
			'scp foo baz:bar': False
		}
		mock_completed_process.stderr = 'Error!'
		mock_exec.side_effect = lambda *args, **kwargs: self.exec_return(mock_completed_process, exec_args, *args, **kwargs)
		error = mock_sync_storage_plugin.copy_remote_file('foo', 'bar', 'baz')
		mock_is_file.assert_called_once_with(Path('foo'))
		mock_exec.call_args == [
			call('ssh baz "mkdir -p bar"', shlexsplit=True),
			call('ssh baz "ls bar/foo"', shlexsplit=True),
			call('scp foo baz:bar', shlexsplit=True)
		]
		assert error == 'Failed to transfer file foo to baz at bar/foo:\nError!'

	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	def test_remove_remote_file(
		self,
		mock_completed_process,
		mock_exec,
		mock_sync_storage_plugin
	):
		mock_completed_process.returncode = 0
		mock_exec.return_value = mock_completed_process
		mock_sync_storage_plugin.remove_remote_file('foo', 'bar')

		expected_calls = [
			call('ssh bar "ls foo"', shlexsplit=True),
			call('ssh bar "rm foo"', shlexsplit=True)
		]

		# Check all the calls to _exec match
		assert expected_calls == mock_exec.call_args_list

	# Test exceptions are raised for removing remote files when:
	# 1. The file doesn't exist on the remote host
	# 2. Removing the file fails
	REMOVE_FILE_EXCEPT_INPUT = [
		(
			{
				'ssh bar "ls foo"': False,
			},
			'Could not find file foo on bar'
		),
		(
			{
				'ssh bar "ls foo"': True,
				'ssh bar "rm foo"': False
			},
			'Failed to remove file foo:Error!'
		)
	]
	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	@patch('subprocess.CompletedProcess', autospec=True)
	@pytest.mark.parametrize('exec_args, except_msg', REMOVE_FILE_EXCEPT_INPUT)
	def test_remove_file_exeception(
		self,
		mock_completed_process,
		mock_exec,
		mock_sync_storage_plugin,
		exec_args,
		except_msg
	):
		mock_completed_process.stderr = 'Error!'

		# Call a helper function to assign the desired
		# return code values for each arg to _exec
		mock_exec.side_effect = lambda *args, **kwargs: self.exec_return(mock_completed_process, exec_args, *args, **kwargs)
		output = mock_sync_storage_plugin.remove_remote_file('foo', 'bar')

		# The calls should match what we expect
		expected_calls = [call(c, shlexsplit=True) for c in exec_args.keys()]
		assert expected_calls == mock_exec.call_args_list
		assert output == except_msg

	@patch('subprocess.CompletedProcess', autospec=True)
	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	def test_remove_empty_dir(
		self,
		mock_exec,
		mock_completed_process,
		mock_sync_storage_plugin
	):

		"""
		Test remove_empty_dir removes an empty
		directory on a remote host
		"""

		# Always have 0 be the return code value
		# to simulate all commands executing successfully
		mock_completed_process.returncode = 0
		mock_completed_process.stdout = ''
		mock_exec.return_value = mock_completed_process

		output = mock_sync_storage_plugin.remove_empty_dir('foo', 'bar')

		# Make sure all commands executed
		# on the hypervisor are the correct
		# values
		expect_calls = [
			call(f'ssh foo "ls bar"', shlexsplit=True),
			call(f'ssh foo "rm -r bar"',
				shlexsplit=True
			)
		]
		assert output is None and mock_exec.call_args_list == expect_calls

	@patch('subprocess.CompletedProcess', autospec=True)
	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	def test_remove_empty_dir_without_empty_dir(
		self,
		mock_exec,
		mock_completed_process,
		mock_sync_storage_plugin
	):

		"""
		Test when content is found in a directory
		that it is not deleted by remove_empty_dir
		"""

		# Always have 0 be the return code value
		# to simulate all commands executing successfully
		mock_completed_process.returncode = 0
		mock_completed_process.stdout = 'file contents'
		mock_exec.return_value = mock_completed_process

		expect_output = 'Found files present in bar on foo'
		output = mock_sync_storage_plugin.remove_empty_dir('foo', 'bar')

		# Check remote bash calls are correct
		expect_calls = [
			call(f'ssh foo "ls bar"', shlexsplit=True)
		]
		assert output == expect_output and mock_exec.call_args_list == expect_calls

	EMPTY_DIR_ERRORS = [
		([1, 0], 'Failed to find bar on foo'),
		([0, 1], 'Failed to remove directory bar on foo:\nError!')
	]
	@patch('subprocess.CompletedProcess', autospec=True)
	@patch('stack.commands.sync.vm.plugin_storage._exec', autospec=True)
	@pytest.mark.parametrize('return_codes, message', EMPTY_DIR_ERRORS)
	def test_remove_empty_dir_errors(
		self,
		mock_exec,
		mock_completed_process,
		mock_sync_storage_plugin,
		return_codes,
		message
	):
		"""
		Test remove_empty_dir
		outputs the correct error messages
		"""

		mock_completed_process.stderr = 'Error!'
		mock_completed_process.stdout = ''

		# Change the returncode attribute based on what
		# command we want to fail
		type(mock_completed_process).returncode = PropertyMock(side_effect=return_codes)
		mock_exec.return_value = mock_completed_process

		output = mock_sync_storage_plugin.remove_empty_dir('foo', 'bar')

		assert output == message

	@patch('stack.commands.sync.vm.plugin_storage.Hypervisor', autospec=True)
	def test_remove_pool(
		self,
		mock_hypervisor,
		mock_sync_storage_plugin
	):
		"""
		Test storage pools are removed correctly
		"""

		mock_conn = mock_hypervisor.return_value.__enter__.return_value
		errors = mock_sync_storage_plugin.remove_pool('pool', 'foo', False)
		mock_conn.remove_pool.assert_called_once_with('pool')
		assert errors == []

	@patch('stack.commands.sync.vm.plugin_storage.Hypervisor', autospec=True)
	def test_remove_pool_exception(
		self,
		mock_hypervisor,
		mock_sync_storage_plugin
	):
		"""
		Test remove_pool outputs errors
		when VmExceptions are raised
		"""

		mock_conn = mock_hypervisor.return_value.__enter__.return_value
		mock_conn.remove_pool.side_effect = self.mock_vm_exception
		errors = mock_sync_storage_plugin.remove_pool('pool', 'foo', False)
		mock_conn.remove_pool.assert_called_once_with('pool')
		assert errors == ['Oh no something went wrong!']

	@patch.object(Plugin, 'remove_empty_dir', autospec=True)
	def test_remove_storage_dir(
		self,
		mock_remove_empty_dir,
		mock_sync_storage_plugin
	):
		"""
		Test remove_storage_dir removes Vm storage directories
		when they are empty and outputs errors
		"""

		mock_remove_empty_dir.return_value = 'Error!'
		disks = [
			{
			'Name': 'foo_disk1',
			'Type': 'disk',
			'Image Name': 'disk_name',
			'Location': 'foo',
			'Pending Deletion': 'False',
			'Size': 100
			},
			{
			'Name': 'baz_disk2',
			'Type': 'image',
			'Image Name': 'disk_name2',
			'Location': 'foo',
			'Pending Deletion': 'False',
			'Size': 100
			}
		]
		errors = mock_sync_storage_plugin.remove_storage_dir('foo', 'bar', disks, False)
		empty_dir_calls = mock_remove_empty_dir.call_args_list

		# Make sure we only called remove_empty dir once
		# so the same directory isn't trying to be removed twice
		assert empty_dir_calls == [call(ANY, 'bar', 'foo')]
		assert errors == ['Error!']
