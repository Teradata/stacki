import pytest
import libvirt
import jinja2
import tarfile
from pathlib import Path
from libvirt import libvirtError, virConnect, virDomain, virStoragePool, virStorageVol
from stack.kvm import Hypervisor, VmException
from unittest.mock import create_autospec, patch, call
from subprocess import CompletedProcess

class TestPylibKvm:

	def mock_libvirt_exception(self, *args, **kwargs):
		"""
		Mock raising a libvirt exception
		"""

		raise libvirtError('Something went wrong!')

	class TestPylibKvmUnderTest(Hypervisor):
		"""
		Inherited class to mock the init function
		"""

		def __init__(self, host = 'hypervisor-foo'):
			self.hypervisor = host
			self.kvm = create_autospec(spec = virConnect, instance = True)
			self.kvm_pool = """
				<pool type="dir">
				<name>{{ name }}</name>
				<target>
				<path>{{ dir }}</path>
				</target>
				</pool>
			"""
			self.kvm_volume = """
				<volume>
				<name>{{ volname }}</name>
				<allocation>0</allocation>
				<capacity unit="G">{{ size }}</capacity>
				<target>
				<path>{{ pooldir }}/{{ volname }}</path>
				<format type="qcow2"/>
				</target>
				</volume>
			"""

	@patch(target = 'stack.kvm.Hypervisor.connect', autospec = True)
	def test_kvm_init(self, mock_kvm_connect):
		mock_kvm_connect.return_value = 'bar'
		test_hypervisor = Hypervisor(host = 'hypervisor-foo')
		mock_kvm_connect.assert_called_once()
		assert hasattr(test_hypervisor, 'hypervisor')

	@patch('libvirt.open', autospec=True)
	def test_kvm_connect(self, mock_libvirt_open):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_libvirt_open.return_value = 'bar'

		# Assert we got back the libvirt
		# connection object
		libvirt_obj = mock_hypervisor.connect()
		mock_libvirt_open.assert_called_once()
		assert libvirt_obj == 'bar'

	@patch('libvirt.open', autospec=True)
	def test_kvm_connect_exception(self, mock_libvirt_open):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_libvirt_open.side_effect = self.mock_libvirt_exception
		expect_exception = 'Failed to connect to hypervisor hypervisor-foo:\nSomething went wrong!'

		# Make sure a VmException was raised
		# with the correct message when a
		# a libvirt exception occurs
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.connect()
			mock_libvirt_open.assert_called_once()

	def test_kvm_close(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.close()
		mock_hypervisor.kvm.close.assert_called_once()

	def test_kvm_close_exception(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.close.side_effect = self.mock_libvirt_exception
		expect_exception = 'Failed to close hypervisor connection to hypervisor-foo:\nSomething went wrong!'
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.close()
			mock_libvirt.close.assert_called_once()

	# Test three cases:
	# 1. No guests found
	# 2. Guests with different status (on/off)
	# 3. Single Guest
	GUEST_INPUT = [
	( {},
	  {}
	),
	(	{'foo' : True, 'bar': False, 'baz': False},
		{'foo' : 'on', 'bar': 'off', 'baz': 'off'}
	),
	(	{'foo' : True},
		{'foo' : 'on'}
	)
	]
	@pytest.mark.parametrize('status, guests', GUEST_INPUT)
	@patch('libvirt.virDomain', autospec=True)
	def test_kvm_guests(self, mock_virDomain, status, guests):
		mock_hypervisor = self.TestPylibKvmUnderTest()

		# Patch the virDomain object that listAllDomains
		# will return a list of when called
		# These are the only two functions of virDomain we
		# care about
		mock_virDomain.isActive.side_effect = status.values()
		mock_virDomain.name.side_effect = status.keys()

		# Make the return value of listAllDomains the same
		# length as the amount of vm's on our simulated hypervisor object
		mock_hypervisor.kvm.listAllDomains.return_value = [mock_virDomain] * len(status)
		actual_guests = mock_hypervisor.guests()
		mock_hypervisor.kvm.listAllDomains.assert_called_once()

		# Check several conditions are met:
		# 1. Output of the function matches
		#	 what we expected
		# 2. The isActive function is called the
		#	 same amount of times as the number of guests
		# 3. Ditto for the domain name function
		assert all([
			actual_guests == guests,
			mock_virDomain.isActive.call_count == len(guests),
			mock_virDomain.name.call_count == len(guests)
		])

	def test_kvm_guests_exception(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.listAllDomains.side_effect = self.mock_libvirt_exception
		expect_exception = 'Failed to get list of VM domains on hypervisor-foo:\nSomething went wrong!'
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.guests()
			mock_hypervisor.kvm.listAllDomains.assert_called_once()

	def test_kvm_add_domain(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.add_domain('foo')

		# defineXML is the libvirt func when creating a domain
		mock_hypervisor.kvm.defineXML.assert_called_once_with('foo')

	def test_kvm_add_domain_exception(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.defineXML.side_effect = self.mock_libvirt_exception
		expect_exception = 'Failed to define guest on hypervisor hypervisor-foo:\nSomething went wrong!'
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.add_domain('foo')
			mock_hypervisor.kvm.defineXML.assert_called_once_with('foo')

	def test_kvm_add_domain_exception_domain_already_exists(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		exception = 'domain already exists with uuid'

		# If a VM is already defined, add_domain
		# should ignore the error
		mock_hypervisor.kvm.defineXML.side_effect = libvirtError(exception)
		mock_hypervisor.add_domain('foo')
		mock_hypervisor.kvm.defineXML.assert_called_once_with('foo')

	@patch('libvirt.virDomain', autospec=True)
	def test_kvm_start_domain(self, mock_virDomain):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.lookupByName.return_value = mock_virDomain
		mock_hypervisor.start_domain('foo')
		mock_hypervisor.kvm.lookupByName.assert_called_once_with('foo')

		# create is the libvirt func for starting a domain
		mock_virDomain.create.assert_called_once()

	def test_kvm_start_domain_exception(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.lookupByName.side_effect = self.mock_libvirt_exception
		expect_exception = 'Failed to start VM foo on hypervisor hypervisor-foo:\nSomething went wrong!'
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.start_domain('foo')
			mock_hypervisor.kvm.lookupByName.assert_called_once_with('foo')

	@patch('libvirt.virDomain', autospec=True)
	def test_kvm_stop_domain(self, mock_virDomain):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.lookupByName.return_value = mock_virDomain
		mock_hypervisor.stop_domain('foo')
		mock_hypervisor.kvm.lookupByName.assert_called_once_with('foo')

		# destroy is the libvirt func for stopping a domain
		mock_virDomain.destroy.assert_called_once()

	def test_kvm_stop_domain_exception(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.lookupByName.side_effect = self.mock_libvirt_exception
		expect_exception = 'Failed to stop VM foo on hypervisor hypervisor-foo:\nSomething went wrong!'
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.stop_domain('foo')
			mock_hypervisor.kvm.lookupByName.assert_called_once_with('foo')

	@patch('libvirt.virStoragePool', autospec=True)
	@patch('stack.util._exec', autospec=True)
	@pytest.mark.parametrize('pool_exists, output', [(True, None), (False, 'foo')])
	def test_kvm_add_pool(self, mock_exec, mock_storage_pool, pool_exists, output):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_storage_pool.create.return_value = None

		# Create our own jinja template to
		# compare later to the one called in
		# add_pool
		mock_pool_vars = {'name': 'foo', 'dir': 'bar'}
		mock_pool_xml = jinja2.Template(mock_hypervisor.kvm_pool).render(mock_pool_vars)

		if pool_exists:
			mock_hypervisor.kvm.storagePoolLookupByName.return_value = mock_storage_pool
		else:
			mock_hypervisor.kvm.storagePoolLookupByName.side_effect = self.mock_libvirt_exception

		mock_hypervisor.kvm.storagePoolDefineXML.return_value = mock_storage_pool
		pool_name = mock_hypervisor.add_pool('foo', 'bar')
		mock_hypervisor.kvm.storagePoolLookupByName.assert_called_once_with('foo')

		# add_pool should return here if the
		# pool exists, otherwise create it
		if pool_exists:
			mock_hypervisor.kvm.storagePoolDefineXML.assert_not_called()
			mock_storage_pool.create.assert_not_called()
			mock_storage_pool.setAutostart.assert_not_called()
		else:
			mock_hypervisor.kvm.storagePoolDefineXML.assert_called_once_with(mock_pool_xml, 0)
			mock_storage_pool.create.assert_called_once()
			mock_storage_pool.setAutostart.assert_called_once_with(1)

		assert pool_name == output

	def test_kvm_add_pool_error(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.storagePoolLookupByName.side_effect = self.mock_libvirt_exception
		mock_hypervisor.kvm.storagePoolDefineXML.side_effect = self.mock_libvirt_exception
		expect_exception = 'Failed to create storage pool bar:\nSomething went wrong!'
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.add_pool('foo', 'bar')
			mock_hypervisor.kvm.storagePoolLookupByName.assert_called_once_with('foo')

	@patch('libvirt.virStoragePool', autospec=True)
	def test_kvm_remove_pool(self, mock_storage_pool):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_storage_pool.undefine.return_value = None
		mock_hypervisor.kvm.storagePoolLookupByName.return_value = mock_storage_pool
		pool_name = mock_hypervisor.remove_pool('foo')
		mock_hypervisor.kvm.storagePoolLookupByName.assert_called_once_with('foo')
		mock_storage_pool.undefine.assert_called_once()

	def test_kvm_remove_pool_exception(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.storagePoolLookupByName.side_effect = self.mock_libvirt_exception
		expect_exception = 'Failed to delete pool foo on hypervisor hypervisor-foo:\nSomething went wrong!'
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.remove_pool('foo')
			mock_hypervisor.kvm.storagePoolLookupByName.assert_called_once_with('foo')

	@patch('libvirt.virStoragePool', autospec=True)
	@patch('libvirt.virStorageVol', autospec=True)
	@pytest.mark.parametrize('vol_exists', [True, False])
	def test_kvm_add_volume(self, mock_storage_vol, mock_storage_pool, vol_exists):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_storage_pool.createXML.return_value = None

		if vol_exists:
			mock_storage_pool.storageVolLookupByName.return_value = mock_storage_vol
		else:
			mock_storage_pool.storageVolLookupByName.side_effect = self.mock_libvirt_exception

		mock_hypervisor.kvm.storagePoolLookupByName.return_value = mock_storage_pool
		pool_name = mock_hypervisor.add_volume('foo', 'bar', 'baz', '100')
		mock_hypervisor.kvm.storagePoolLookupByName.assert_called_once_with('baz')
		mock_storage_pool.storageVolLookupByName.assert_called_once_with('foo')

		if vol_exists:
			mock_storage_pool.createXML.assert_not_called()
		else:

			# similar to add_pool's test, create a jinja template
			# to compare the rendered output to the func args
			vol_template = jinja2.Template(mock_hypervisor.kvm_volume)
			vol_xml = vol_template.render({'volname': 'foo', 'size': 100, 'dir': 'bar'})
			mock_storage_pool.createXML.assert_called_once_with(vol_xml, 0)

	def test_kvm_add_volume_no_pool(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.storagePoolLookupByName.side_effect = self.mock_libvirt_exception

		# If no pool is found for a given storage
		# volume an error is raised
		expect_exception = 'Failed to create volume foo on hypervisor hypervisor-foo:\nSomething went wrong!'
		with pytest.raises(VmException, match=expect_exception):
			pool_name = mock_hypervisor.add_volume('foo', 'bar', 'baz', '100')
			mock_hypervisor.kvm.storagePoolLookupByName.assert_called_once_with('baz')

	@patch('libvirt.virStoragePool', autospec=True)
	@patch('libvirt.virStorageVol', autospec=True)
	def test_kvm_add_volume_error(self, mock_storage_vol, mock_storage_pool):
		"""
		Simulate an exception being rasied when
		trying to create the volume
		"""

		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_storage_pool.storageVolLookupByName.side_effect = self.mock_libvirt_exception

		# This creates the storage volume
		mock_storage_pool.createXML.side_effect = self.mock_libvirt_exception
		mock_hypervisor.kvm.storagePoolLookupByName.return_value = mock_storage_pool

		# Compare the exception raised and make sure the
		# text is the same
		expect_exception = 'Failed to create volume foo on hypervisor hypervisor-foo:\nSomething went wrong!'
		vol_template = jinja2.Template(mock_hypervisor.kvm_volume)
		vol_xml = vol_template.render({'volname': 'foo', 'size': 100, 'dir': 'bar'})
		with pytest.raises(VmException, match=expect_exception):
			pool_name = mock_hypervisor.add_volume('foo', 'bar', 'baz', '100')
			mock_hypervisor.kvm.storagePoolLookupByName.assert_called_once_with('baz')
			mock_storage_pool.storageVolLookupByName.assert_called_once_with('foo')
			mock_storage_pool.createXML.assert_called_once_with(vol_xml, 0)

	@patch('libvirt.virStoragePool', autospec=True)
	@patch('libvirt.virStorageVol', autospec=True)
	def test_kvm_remove_vol(self, mock_storage_vol, mock_storage_pool):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.storagePoolLookupByName.return_value = mock_storage_pool
		mock_storage_pool.storageVolLookupByName.return_value = mock_storage_vol

		# Call remove_volume and make sure
		# the correct func are called
		mock_hypervisor.remove_volume('foo', 'bar')
		mock_hypervisor.kvm.storagePoolLookupByName.assert_called_once_with('foo')
		mock_storage_pool.storageVolLookupByName.assert_called_once_with('bar')
		mock_storage_vol.delete.assert_called_once()

	@patch('libvirt.virStoragePool', autospec=True)
	def test_kvm_remove_vol_exception(self, mock_storage_pool):
		"""
		Simulate finding the correct pool, but no volume
		existing in that pool with the given name
		when trying to remove it
		"""

		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_storage_pool.storageVolLookupByName.side_effect = self.mock_libvirt_exception
		mock_hypervisor.kvm.storagePoolLookupByName.return_value = mock_storage_pool
		expect_exception = 'Failed to delete volume bar on hypervisor hypervisor-foo:\nSomething went wrong!'

		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.remove_volume('foo', 'bar')
			mock_hypervisor.kvm.storagePoolLookupByName.assert_called_once_with('foo')
			mock_storage_pool.storageVol.LookupByName.assert_called_once_with('bar')

	@patch('libvirt.virDomain', autospec=True)
	@pytest.mark.parametrize('is_autostart', [True, False])
	def test_kvm_autostart(self, mock_virDomain, is_autostart):
		"""
		Test setting/un-setting a VM to autostart
		upon host boot-up
		"""

		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.lookupByName.return_value = mock_virDomain
		mock_hypervisor.autostart('foo', is_autostart)

		mock_hypervisor.kvm.lookupByName.assert_called_once_with('foo')
		if is_autostart:
			mock_virDomain.setAutostart.assert_called_once_with(1)
		else:
			mock_virDomain.setAutostart.assert_called_once_with(0)

	@patch('libvirt.virDomain', autospec=True)
	def test_kvm_remove_autostart_exception(self, mock_virDomain):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_virDomain.setAutostart.side_effect = self.mock_libvirt_exception
		mock_hypervisor.kvm.lookupByName.return_value = mock_virDomain
		expect_exception = 'Could not autostart foo on hypervisor-foo:\nSomething went wrong!'

		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.autostart('foo', True)
			mock_hypervisor.kvm.lookupByName.assert_called_once_with('foo')
			mock_virDomain.setAutostart.assert_called_once_with(1)
