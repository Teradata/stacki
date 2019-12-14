import pytest
from collections import namedtuple
from stack.kvm import Hypervisor, VmException
from unittest.mock import create_autospec, patch
from stack.commands import DatabaseConnection
from stack.argument_processors.vm import VmArgumentProcessor
from stack.commands.set.host.power.imp_kvm import Implementation
from stack.commands.set.host.power import Command

class TestKVMImp:
	mock_tuple = namedtuple('output', 'out debug success')

	def mock_vm_exception(self, *args):
		raise VmException('Oh no something went wrong!')

	@pytest.fixture
	def kvm_imp(self):
		"""
		A fixture for mocking the Implementation instance
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

		return Implementation(mock_command)

	@patch.object(target = Implementation, attribute = 'get_hypervisor_by_name', autospec = True)
	def test_no_kvm_host(self, mock_get_hypervisor_name, kvm_imp):
		mock_get_hypervisor_name.return_value = None
		output = kvm_imp.run(args = ['foo', 'on', self.mock_tuple])
		assert output == self.mock_tuple('', 'No KVM host specified for virtual machine "foo"', False)

	@patch('stack.kvm.Hypervisor', autospec = True)
	def test_kvm_imp_on(self, mock_hypervisor, kvm_imp):
		hypervisor = mock_hypervisor.return_value
		hypervisor.start_domain.return_value = None

		output = kvm_imp.run(args = ['foo', 'on', self.mock_tuple])

		hypervisor.start_domain.assert_called_once_with('foo')

		assert output == self.mock_tuple('', '', True)

	@patch('stack.kvm.Hypervisor', autospec = True)
	def test_kvm_imp_off(self, mock_hypervisor, kvm_imp):
		hypervisor = mock_hypervisor.return_value
		hypervisor.stop_domain.return_value = None

		output = kvm_imp.run(args = ['foo', 'off', self.mock_tuple])

		hypervisor.stop_domain.assert_called_once_with('foo')

		assert output == self.mock_tuple('', '', True)

	@patch('stack.kvm.Hypervisor', autospec = True)
	def test_kvm_imp_reset(self, mock_hypervisor, kvm_imp):
		hypervisor = mock_hypervisor.return_value
		hypervisor.start_domain.return_value = None
		hypervisor.stop_domain.return_value = None

		output = kvm_imp.run(args = ['foo', 'reset', self.mock_tuple])

		hypervisor.stop_domain.assert_called_once_with('foo')
		hypervisor.start_domain.assert_called_once_with('foo')

		assert output == self.mock_tuple('', '', True)

	VM_STATUS_DEFINED = [
	([{'status': 'on'}], mock_tuple('Chassis Power is on', '', True)),
	([{'status': 'off'}], mock_tuple('Chassis Power is off', '', True)),
	([{'status': 'undefined'}], mock_tuple('', f'Cannot find host foo defined on hypervisor', False)),
	([{'status': 'Connection failed'}], mock_tuple('', f'Cannot find host foo defined on hypervisor', False))
	]
	@patch('stack.kvm.Hypervisor', autospec = True)
	@pytest.mark.parametrize('return_status, output', VM_STATUS_DEFINED)
	def test_kvm_imp_status(self, mock_hypervisor, kvm_imp, return_status, output):
		kvm_imp.owner.call.return_value = return_status
		run_output = kvm_imp.run(args = ['foo', 'status', self.mock_tuple])
		kvm_imp.owner.call.assert_called_once()
		assert all([
			output.out in run_output.out,
			output.debug in run_output.debug,
			output.success == run_output.success
		])

	@patch('stack.kvm.Hypervisor', autospec = True)
	def test_kvm_imp_vm_exception(self, mock_hypervisor, kvm_imp):
		hypervisor = mock_hypervisor.return_value
		hypervisor.start_domain.side_effect = self.mock_vm_exception
		output = kvm_imp.run(args = ['foo', 'on', self.mock_tuple])

		hypervisor.start_domain.assert_called_once_with('foo')

		assert output == self.mock_tuple('', 'Oh no something went wrong!', False)
