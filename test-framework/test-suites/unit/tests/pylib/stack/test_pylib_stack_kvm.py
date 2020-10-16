import pytest
import libvirt
import jinja2
import tarfile
from pathlib import Path
from libvirt import libvirtError, virConnect, virDomain, virStoragePool, virStorageVol
from stack.kvm import Hypervisor, VmException
from unittest.mock import create_autospec, patch, call, Mock
from subprocess import CompletedProcess

class TestPylibKvm:

	def mock_libvirt_exception(self, *args, **kwargs):
		"""
		Mock raising a libvirt exception
		"""

		raise libvirtError('Something went wrong!')

	def mock_kvm_exception(self, *args, **kwargs):
		"""
		Mock raising a VmException
		"""

		raise VmException('Something went wrong!')

	class TestPylibKvmUnderTest(Hypervisor):
		"""
		Inherited class to mock the init function
		"""

		def __init__(self, host = 'hypervisor-foo'):
			self.hypervisor = host
			self.kvm = create_autospec(spec=virConnect, instance=True)
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

	def test_kvm_init(self):
		"""
		Test the init sets the values
		we expect
		"""

		test_hypervisor = Hypervisor(host='hypervisor-foo')
		assert test_hypervisor.hypervisor == 'hypervisor-foo'
		assert test_hypervisor.kvm is None

	@patch('stack.kvm.Hypervisor.connect', autospec=True)
	@patch('stack.kvm.Hypervisor.close', autospec=True)
	def test_kvm_context_manager(
		self,
		mock_kvm_close,
		mock_kvm_connect,
	):
		"""
		Test when calling the Hypervisor class as a context manager
		the connect and close functions are called on context manager
		enter and exit
		"""

		with Hypervisor('hypervisor-foo') as conn:
			pass
		mock_kvm_connect.assert_called_once()
		mock_kvm_close.assert_called_once()

		# Make sure we are returning the
		# Hypervisor object upon contextmanager enter
		assert conn is not None

	@patch('stack.kvm.Hypervisor.connect', autospec=True)
	@patch('stack.kvm.Hypervisor.close', autospec=True)
	def test_kvm_context_manager_exception_open(
		self,
		mock_kvm_close,
		mock_kvm_connect,
	):
		"""
		Test when entering the context manager that if the an exception
		is raised it will be output
		"""

		expect_exception = 'Something went wrong!'
		mock_kvm_connect.side_effect = self.mock_kvm_exception
		with pytest.raises(VmException, match=expect_exception), Hypervisor('hypervisor-foo') as conn:
			mock_kvm_connect.assert_called_once()
			mock_kvm_close.assert_called_once()

	@patch('stack.kvm.Hypervisor.connect', autospec=True)
	@patch('stack.kvm.Hypervisor.close', autospec=True)
	def test_kvm_context_manager_exception_close(
		self,
		mock_kvm_close,
		mock_kvm_connect,
	):
		"""
		Test when entering the context manager that if the an exception
		is raised it will be output
		"""

		expect_exception = 'Something went wrong!'
		mock_kvm_close.side_effect = self.mock_kvm_exception
		with pytest.raises(VmException, match=expect_exception), Hypervisor('hypervisor-foo') as conn:
			mock_kvm_connect.assert_called_once()
			mock_kvm_close.assert_called_once()

	@patch('libvirt.open', autospec=True)
	def test_kvm_connect(self, mock_libvirt_open):
		"""
		Test the connect method successfully returns
		a libvirt connection object
		"""

		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_libvirt_open.return_value = 'bar'

		# Assert we got back the libvirt
		# connection object
		libvirt_obj = mock_hypervisor.connect()
		mock_libvirt_open.assert_called_once()
		assert libvirt_obj == 'bar'

	@patch('libvirt.open', autospec=True)
	def test_kvm_connect_exception(self, mock_libvirt_open):
		"""
		Test the connect method throws a VmException when
		a libvirt connection object could not be made
		"""

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
		"""
		Test the close method calls the libvirt
		close connection method
		"""

		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.close()
		mock_hypervisor.kvm.close.assert_called_once()

	def test_kvm_close_exception(self):
		"""
		Test the close method throws a VmExpection
		when a connection could not be close
		"""

		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.close.side_effect = self.mock_libvirt_exception
		expect_exception = 'Failed to close hypervisor connection to hypervisor-foo:\nSomething went wrong!'
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.close()
			mock_libvirt.close.assert_called_once()

	def test_kvm_close_no_conn(self):
		"""
		Test the close method catches the case
		when a hypervisor connection is no longer available
		"""

		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm = None
		expect_exception = 'Cannot find hypervisor connection to hypervisor-foo'
		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.close()

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
	def test_kvm_guests(self, status, guests):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		domain_status = []
		mock_virDomain = create_autospec(virDomain, instance=True)

		# Patch the virDomain object that listAllDomains
		# will return a list of when called
		# These are the only two functions of virDomain we
		# care about
		for host, is_active in status.items():
			domain = Mock(return_value = mock_virDomain)
			domain.name.return_value = host
			domain.isActive.return_value = is_active
			domain_status.append(domain)

		# Make the return value of listAllDomains the same
		# length as the amount of vm's on our simulated hypervisor object
		mock_hypervisor.kvm.listAllDomains.return_value = domain_status
		actual_guests = mock_hypervisor.guests()
		mock_hypervisor.kvm.listAllDomains.assert_called_once()

		# Check for each domain object
		# that two functions we expected
		# were called
		for mock_domain in domain_status:
			mock_domain.isActive.assert_called_once()
			mock_domain.name.assert_called_once()

		assert actual_guests == guests

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
	def test_kvm_remove_domain(self, mock_virDomain):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.lookupByName.return_value = mock_virDomain

		mock_hypervisor.remove_domain('foo')
		mock_virDomain.undefine.assert_called_once()

	@patch('libvirt.virDomain', autospec=True)
	def test_kvm_remove_domain_exception(self, mock_virDomain):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.lookupByName.return_value = mock_virDomain
		mock_virDomain.undefine = self.mock_libvirt_exception
		expect_exception = 'Failed to undefine VM foo on hypervisor hypervisor-foo:\nSomething went wrong!'

		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.remove_domain('foo')
			mock_virDomain.undefine.assert_called_once()

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
		"""
		Test adding a storage volume to a
		storage pool that doesn't exist
		"""

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
		mock_hypervisor = self.TestPylibKvmUnderTest()

		# Raise an exception when finding a volume by name
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
	def test_kvm__autostart_exception(self, mock_virDomain):
		"""
		Test that autostart raises a VmException
		when we expect it to
		"""

		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_virDomain.setAutostart.side_effect = self.mock_libvirt_exception
		mock_hypervisor.kvm.lookupByName.return_value = mock_virDomain
		expect_exception = 'Could not autostart foo on hypervisor-foo:\nSomething went wrong!'

		with pytest.raises(VmException, match=expect_exception):
			mock_hypervisor.autostart('foo', True)
			mock_hypervisor.kvm.lookupByName.assert_called_once_with('foo')
			mock_virDomain.setAutostart.assert_called_once_with(1)

	POOL_INFO = [
		(
			'',
			['foo'],
			[2, 21474836480, 21474836480, 0],
			True,
			{
				'foo':
				{
					'allocated': '20.0 GB',
					'available': '0.0 GB',
					'capacity': '20.0 GB',
					'is_active': True
				}
			}
		),
		(
			'',
			['foo', 'bar', 'baz'],
			[2, 21474836480, 21474836480, 0],
			True,
			{
				'foo':
				{
					'allocated': '20.0 GB',
					'available': '0.0 GB',
					'capacity': '20.0 GB',
					'is_active': True
				},
				'bar':
				{
					'allocated': '20.0 GB',
					'available': '0.0 GB',
					'capacity': '20.0 GB',
					'is_active': True
				},
				'baz':
				{
					'allocated': '20.0 GB',
					'available': '0.0 GB',
					'capacity': '20.0 GB',
					'is_active': True
				}
			}

		),
		(
			'foo',
			['foo', 'bar', 'baz'],
			[2, 21474836480, 21474836480, 0],
			True,
			{
				'foo':
				{
					'allocated': '20.0 GB',
					'available': '0.0 GB',
					'capacity': '20.0 GB',
					'is_active': True
				}
			}

		)
	]
	@pytest.mark.parametrize('filter_pool, p_names, p_info, is_active, expect_output', POOL_INFO)
	def test_kvm_pool_info(
		self,
		filter_pool,
		p_names,
		p_info,
		is_active,
		expect_output
	):
		pool_list = []
		mock_hypervisor = self.TestPylibKvmUnderTest()

		# Create a list of mock virStoragePool
		# objects to emulate the real return value
		# of listAllStoragePools
		mock_virStoragePool = create_autospec(virStoragePool, instance=True)
		for p_name in p_names:
			mock_pool = Mock(return_value=mock_virStoragePool)
			mock_pool.name.return_value = p_name
			mock_pool.info.return_value = p_info
			mock_pool.isActive.return_value = is_active
			pool_list.append(mock_pool)
		mock_hypervisor.kvm.listAllStoragePools.return_value = pool_list
		output = mock_hypervisor.pool_info(filter_pool=filter_pool)
		assert output == expect_output

	def test_kvm_pool_info_except(self):
		mock_hypervisor = self.TestPylibKvmUnderTest()
		mock_hypervisor.kvm.listAllStoragePools.side_effect = self.mock_libvirt_exception
		except_msg = 'Failed to get pool info on hypervisor-foo:\nSomething went wrong!'

		with pytest.raises(VmException, match=except_msg):
			mock_hypervisor.pool_info()
			mock_hypervisor.kvm.listAllStoragePools.assert_called_once_with(0)
