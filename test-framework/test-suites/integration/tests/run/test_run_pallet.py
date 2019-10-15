import json
from textwrap import dedent


class TestRunPallet:
	def test_invalid_pallet(self, host):
		result = host.run('stack run pallet test')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "test" argument is not a valid pallet
			{pallet ...} [arch=string] [os=string] [release=string] [version=string]
		''')

	def test_no_args(self, host):
		result = host.run('stack run pallet')
		assert result.rc == 255
		assert result.stderr == dedent('''\
			error - "pallet" argument is required
			{pallet ...} [arch=string] [os=string] [release=string] [version=string]
		''')

	def test_not_enabled(self, host, host_os, create_pallet_isos, revert_export_stack_pallets):
		# Add our test pallet
		result = host.run(
			f'stack add pallet {create_pallet_isos}/minimal-1.0-sles12.x86_64.disk1.iso'
		)
		assert result.rc == 0

		# Make sure we get an error that the pallet isn't enabled
		result = host.run(f'stack run pallet minimal')
		assert result.rc == 255
		assert result.stderr == 'error - minimal is not in box frontend\n'

	def test_one_arg(self, host, revert_export_stack_carts):
		# Make sure the top of the output matches what we expect
		result = host.run('script -qfec "stack run pallet stacki" - | tr -d "\r" | head -n 1')
		assert result.rc == 0
		assert result.stdout == '#! /bin/bash\n'

		# Note: The code has a test for isatty so we have to trick the
		# run pallet command to think it has a tty

		# Run it through "bash -n" to do a syntax sanity check
		result = host.run('script -qfec "stack run pallet stacki" - | tr -d "\r" | bash -n')
		assert result.rc == 0
		assert result.stdout == ''

	def test_multiple_args(self, host, host_os, create_pallet_isos, revert_etc, revert_export_stack_pallets, revert_export_stack_carts):
		# Add our test pallet
		result = host.run(
			f'stack add pallet {create_pallet_isos}/test_1-{host_os}-1.0-prod.x86_64.disk1.iso'
		)
		assert result.rc == 0

		# Add the pallet to the default box
		result = host.run(f'stack enable pallet test_1-{host_os}')
		assert result.rc == 0

		# Note: The code has a test for isatty so we have to trick the
		# run pallet command to think it has a tty

		# Make sure the top of the output matches what we expect
		result = host.run(f'script -qfec "stack run pallet stacki test_1-{host_os}" - | tr -d "\r" | head -n 1')
		assert result.rc == 0
		assert result.stdout == '#! /bin/bash\n'

		# Run it through "bash -n" to do a syntax sanity check
		result = host.run(f'script -qfec "stack run pallet stacki test_1-{host_os}" - | tr -d "\r" | bash -n')
		assert result.rc == 0
		assert result.stdout == ''

	def test_database_false(self, host, host_os, create_pallet_isos, revert_etc, revert_export_stack_pallets, revert_export_stack_carts):
		# Add our test pallet
		result = host.run(
			f'stack add pallet {create_pallet_isos}/test_1-{host_os}-1.0-prod.x86_64.disk1.iso'
		)
		assert result.rc == 0

		# Add the pallet to the default box
		result = host.run(f'stack enable pallet test_1-{host_os}')
		assert result.rc == 0

		# Note: The code has a test for isatty so we have to trick the
		# run pallet command to think it has a tty

		# Make sure the top of the output matches what we expect
		result = host.run(f'script -qfec "stack run pallet stacki test_1-{host_os} database=false" - | tr -d "\r" | head -n 1')
		assert result.rc == 0
		assert result.stdout == '#! /bin/bash\n'

		# Run it through "bash -n" to do a syntax sanity check
		result = host.run(f'script -qfec "stack run pallet stacki test_1-{host_os} database=false" - | tr -d "\r" | bash -n')
		assert result.rc == 0
		assert result.stdout == ''

	def test_no_tty_xml_error(self, host, host_os):
		# Run the command, passing false for database to skip the pallet
		# check and feed it bad XML
		result = host.run('echo "test" | stack run pallet database=false')
		assert result.rc == 0
		assert result.stderr == 'error - OS name not specified in profile\n'
