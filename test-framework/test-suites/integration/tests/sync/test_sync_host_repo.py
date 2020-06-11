import json
from pathlib import Path

class TestSyncHostRepo:
	def test_sync_host_repo_no_backends(self, host, host_os, host_repo_file, revert_etc, add_box):
		''' with no args and no backends, sync host repo should do nothing '''

		# get the original
		repo_fi_handle = Path(host_repo_file)
		og_repo_text = repo_fi_handle.read_text()

		# overwrite with garbage
		repo_fi_handle.write_text('potato')

		results = host.run('stack sync host repo')
		assert results.rc == 0
		# validate no change
		assert repo_fi_handle.read_text() == 'potato'

		# when called against localhost, the FE repo file should be re-written

		results = host.run('stack sync host repo localhost')
		assert results.rc == 0
		# verify it changed
		assert repo_fi_handle.read_text() == og_repo_text


	def test_repo_file_synced(self, host, host_os, host_repo_file, revert_etc, add_box, add_cart, add_repo, create_pallet_isos, revert_export_stack_pallets, revert_pallet_hooks, revert_export_stack_carts):
		''' verify that the frontend's repo file is re-written for certain commands '''

		# get the original
		repo_fi_handle = Path(host_repo_file)
		og_repo_text = repo_fi_handle.read_text()

		# we need the to test this against the frontend's box
		results = host.run(f'stack set host box localhost box=test')
		assert results.rc == 0
		# 'set host box' alone should NOT force a repo-sync.
		assert og_repo_text == repo_fi_handle.read_text()
		
		results = host.run(f'stack list host localhost output-format=json')
		assert results.rc == 0
		assert json.loads(results.stdout)[0]['box'] == 'test'

		results = host.run(f'stack sync host repo localhost')
		assert results.rc == 0

		test_repo_text = repo_fi_handle.read_text()
		assert test_repo_text != og_repo_text
		assert test_repo_text == ''

		result = host.run(f'stack add pallet {create_pallet_isos}/test_1-{host_os}-1.0-prod.x86_64.disk1.iso')
		assert result.rc == 0

		repo_objects = [
			('cart', 'test'),
			('pallet', f'test_1-{host_os}'),
			('repo', 'test'),
		]

		for obj, name in repo_objects:
			# try to enable, then disable, then re-enable, then remove
			# EXPECTED: each of these actions should trigger repo_file being re-written

			# overwrite repo file with garbage
			repo_fi_handle.write_text(f'enable {name} {obj}')
			results = host.run(f'stack enable {obj} {name} box=test')
			assert results.rc == 0
			# verify it changed
			assert repo_fi_handle.read_text() != test_repo_text
			assert repo_fi_handle.read_text() != f'enable {name} {obj}'

			# overwrite repo file with garbage
			repo_fi_handle.write_text(f'disable {name} {obj}')
			results = host.run(f'stack disable {obj} {name} box=test')
			assert results.rc == 0
			# verify it changed
			assert repo_fi_handle.read_text() == test_repo_text

			# overwrite repo file with garbage
			repo_fi_handle.write_text(f'enable {name} {obj}')
			results = host.run(f'stack enable {obj} {name} box=test')
			assert results.rc == 0
			# verify it changed
			assert repo_fi_handle.read_text() != test_repo_text
			assert repo_fi_handle.read_text() != f'enable {name} {obj}'

			repo_fi_handle.write_text(f'remove {name} {obj}')
			results = host.run(f'stack remove {obj} {name}')
			assert results.rc == 0
			# verify it changed
			assert repo_fi_handle.read_text() == test_repo_text
