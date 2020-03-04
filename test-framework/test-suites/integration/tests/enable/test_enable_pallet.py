import json
from textwrap import dedent
import pathlib
import pytest
from stack.argument_processors.pallet import PALLET_HOOK_ROOT

class TestEnablePallet:
	def test_no_args(self, host):
		result = host.run('stack enable pallet')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "pallet" argument is required
			{pallet ...} [arch=string] [box=string] [os=string] [release=string] [run_hooks=bool] [version=string]
		''')

	def test_invalid_pallet(self, host):
		result = host.run('stack enable pallet test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid pallet with parameters arch=x86_64
			{pallet ...} [arch=string] [box=string] [os=string] [release=string] [run_hooks=bool] [version=string]
		''')

	def test_invalid_box(self, host):
		result = host.run('stack enable pallet test box=test')
		assert result.rc == 255
		assert result.stderr == 'error - unknown box "test"\n'

	def test_incompatable_os(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add the pallet that is ubuntu
		result = host.run(f'stack add pallet {create_pallet_isos}/test-different-os-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Try to enable it on our default box
		result = host.run(f'stack enable pallet test-different-os')
		assert result.rc == 255
		assert result.stderr == 'error - incompatible pallet "test-different-os" with OS "ubuntu"\n'

	def test_wrong_version(self, host, create_pallet_isos, revert_export_stack_pallets):
		# Add our test pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/test-different-version-test_foo-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Try to enable it with the version parameter being wrong
		result = host.run(f'stack enable pallet test-different-version version=1.0')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test-different-version" argument is not a valid pallet with parameters version=1.0, arch=x86_64
			{pallet ...} [arch=string] [box=string] [os=string] [release=string] [run_hooks=bool] [version=string]
		''')

	def test_default_box(self, host, host_os, create_pallet_isos, revert_etc, revert_export_stack_pallets):
		# Add our test pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/test_1-{host_os}-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Add the pallet to the default box
		result = host.run(f'stack enable pallet test_1-{host_os}')
		assert result.rc == 0

		# Confirm it is in the box now
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'default',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

	def test_with_box(self, host, host_os, create_pallet_isos, revert_etc, revert_export_stack_pallets):
		# Add our test box
		result = host.run('stack add box test')
		assert result.rc == 0

		# Add our test pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/test_1-{host_os}-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Add the pallet to the test box
		result = host.run(f'stack enable pallet test_1-{host_os} box=test')
		assert result.rc == 0

		# Confirm it is in the box now
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'test',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

	def test_already_enabled(self, host, host_os, create_pallet_isos, revert_etc, revert_export_stack_pallets):
		# Add our test pallet
		result = host.run(f'stack add pallet {create_pallet_isos}/test_1-{host_os}-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		# Add the pallet to the default box
		result = host.run(f'stack enable pallet test_1-{host_os}')
		assert result.rc == 0

		# Confirm it is in the box now
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'default',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

		# Now enable it again, nothing should change in the db
		result = host.run(f'stack enable pallet test_1-{host_os}')
		assert result.rc == 0

		# Confirm everything is the same
		result = host.run(f'stack list pallet test_1-{host_os} output-format=json')
		assert result.rc == 0
		assert json.loads(result.stdout) == [
			{
				'arch': 'x86_64',
				'boxes': 'default',
				'name': f'test_1-{host_os}',
				'os': host_os,
				'release': 'prod',
				'version': '1.0'
			}
		]

	def test_stacki_enable_hooks_sles12(
		self,
		host,
		host_os,
		revert_etc,
		revert_export_stack_pallets,
		revert_pallet_patches,
		revert_pallet_hooks,
		revert_opt_stack_images,
	):
		"""Test the stacki hooks for sles12 work as expected."""
		if host_os != "sles":
			pytest.skip("This only tests hooks for SLES")

		# remove the stacki-sles-sles12-images RPM
		result = host.run("zypper --non-interactive remove stack-sles-sles12-images")
		assert result.rc == 0

		# remove the sles pallet
		result = host.run("stack remove pallet SLES")
		assert result.rc == 0

		# clean up /tftboot/pxelinux, /opt/stack/pallet-patches, and /opt/stack/pallet_hooks
		result = host.run("rm -f /tftpboot/pxelinux/vmlinuz-sles*")
		assert result.rc == 0
		result = host.run("rm -f /tftpboot/pxelinux/initrd-sles*")
		assert result.rc == 0
		result = host.run("rm -rf /opt/stack/pallet-patches/*")
		assert result.rc == 0
		result = host.run(f"rm -rf {PALLET_HOOK_ROOT}/*")
		assert result.rc == 0

		# Re-add the stacki pallet to re-copy the patches and hooks
		result = host.run(f"stack add pallet /export/isos/stacki*sles12*.iso")
		assert result.rc == 0

		# Add the SLES pallet back.
		result = host.run("stack add pallet /export/isos/SLE-12-SP3-Server-DVD-x86_64-GM-DVD1.iso")
		assert result.rc == 0
		# Get the sha256sum for the original content and boot/x86_64/config files (unpatched)
		original_content_shasum = host.file("/export/stack/pallets/SLES/12sp3/sles12/sles/x86_64/content").sha256sum
		original_config_shasum = host.file("/export/stack/pallets/SLES/12sp3/sles12/sles/x86_64/boot/x86_64/config").sha256sum

		# Now re-enable the stacki pallet to patch the SLES pallet.
		result = host.run("stack enable pallet stacki")
		assert result.rc == 0

		# Now get the sha256sum for the patched files.
		new_content_shasum = host.file("/export/stack/pallets/SLES/12sp3/sles12/sles/x86_64/content").sha256sum
		new_config_shasum = host.file("/export/stack/pallets/SLES/12sp3/sles12/sles/x86_64/boot/x86_64/config").sha256sum
		# Make sure they do not match
		assert original_content_shasum != new_content_shasum
		assert original_config_shasum != new_config_shasum
		# They should match the files in the pallet-patches location
		source_content_shasum = host.file("/opt/stack/pallet-patches/SLES-12sp3-sles12-sles-x86_64/add-stacki-squashfs/content").sha256sum
		assert new_content_shasum == source_content_shasum
		source_config_shasum = host.file("/opt/stack/pallet-patches/SLES-12sp3-sles12-sles-x86_64/add-stacki-squashfs/boot/x86_64/config").sha256sum
		assert new_config_shasum == source_config_shasum

		# Make sure the vmlinuz and initrds were laid down.
		assert host.file("/tftpboot/pxelinux/initrd-sles-sles11-11sp3-x86_64").exists
		assert host.file("/tftpboot/pxelinux/initrd-sles-sles12-12sp2-x86_64").exists
		assert host.file("/tftpboot/pxelinux/initrd-sles-sles12-12sp3-x86_64").exists
		assert host.file("/tftpboot/pxelinux/vmlinuz-sles-sles11-11sp3-x86_64").exists
		assert host.file("/tftpboot/pxelinux/vmlinuz-sles-sles12-12sp2-x86_64").exists
		assert host.file("/tftpboot/pxelinux/vmlinuz-sles-sles12-12sp3-x86_64").exists

	def test_stacki_enable_hooks_redhat7(
			self,
			host,
			host_os,
			revert_etc,
			revert_export_stack_pallets,
			revert_pallet_patches,
			revert_pallet_hooks,
			revert_opt_stack_images,
		):
			"""Test the stacki hooks for redhat7 work as expected."""
			if host_os != "redhat":
				pytest.skip("This only tests hooks for RedHat")

			# remove the stacki-sles-sles12-images RPM
			result = host.run("yum --assumeyes remove stack-images")
			assert result.rc == 0

			# clean up /tftboot/pxelinux and /opt/stack/pallet_hooks
			result = host.run("rm -f /tftpboot/pxelinux/initrd.img*redhat7-x86_64")
			assert result.rc == 0
			result = host.run("rm -f /tftpboot/pxelinux/vmlinuz*redhat7-x86_64")
			assert result.rc == 0
			result = host.run(f"rm -rf {PALLET_HOOK_ROOT}/*")
			assert result.rc == 0

			# Re-add the stacki pallet to re-copy the patches and hooks
			result = host.run(f"stack add pallet /export/isos/stacki*redhat7*.iso")
			assert result.rc == 0

			# Now re-enable the stacki pallet to lay down the vmlinuz and initrd.
			result = host.run("stack enable pallet stacki")
			assert result.rc == 0

			# Make sure the vmlinuz and initrds were laid down. Have to do globbing
			# as the version number (potentially a git hash) is baked into the filename.
			assert len(list(pathlib.Path("/tftpboot/pxelinux").glob("initrd.img*redhat7-x86_64"))) == 1
			assert len(list(pathlib.Path("/tftpboot/pxelinux").glob("vmlinuz*redhat7-x86_64"))) == 1
