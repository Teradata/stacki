import stack.firmware

def test_sync_only_needed_files(host, add_host_with_net, fake_local_firmware_file, inject_code, test_file, revert_firmware):
	"""Test that sync host firmware only tries to sync firmware it needs, not all in the database.

	This adds multiple firmware versions for the same make + model combo on purpose to exercise clustered syncing of
	firmware files. This also requires passing the force flag to `sync host firmware`.
	"""
	# Add multiple piecies of firmware for mellanox, and associate it with the host we are going to sync.
	result = host.run(f"stack add firmware 1.2.3 make=mellanox model=m7800 source={fake_local_firmware_file} hosts=backend-0-0")
	assert result.rc == 0
	result = host.run(f"stack add firmware 2.3.4 make=mellanox model=m7800 source={fake_local_firmware_file} hosts=backend-0-0")
	assert result.rc == 0
	# Add multiple firmwares for dell, and associate it with the host we are going to sync.
	result = host.run(f"stack add firmware 1.2.3.4 make=dell model=x1052-software source={fake_local_firmware_file} hosts=backend-0-0")
	assert result.rc == 0
	result = host.run(f"stack add firmware 2.3.4.5 make=dell model=x1052-software source={fake_local_firmware_file} hosts=backend-0-0")
	assert result.rc == 0
	result = host.run(f"stack add firmware 1.2.3.4 make=dell model=x1052-boot source={fake_local_firmware_file} hosts=backend-0-0")
	assert result.rc == 0
	result = host.run(f"stack add firmware 2.3.4.5 make=dell model=x1052-boot source={fake_local_firmware_file} hosts=backend-0-0")
	assert result.rc == 0
	# Add a piece of firmware we don't care about. Don't associate it with any hosts.
	result = host.run(f"stack add firmware 1.2.3 make=mellanox model=m6036 source={fake_local_firmware_file}")
	assert result.rc == 0
	# Now find the files on disk and nuke em. The files are given random UUID4 names,
	# so we have to glob for the file.
	firmware_files_on_disk = [
		firmware_file for firmware_file in stack.firmware.BASE_PATH.glob(f"**/*")
		if firmware_file.is_file()
	]
	assert len(firmware_files_on_disk) == 7
	for firmware_file in firmware_files_on_disk:
		firmware_file.unlink()
		assert not firmware_file.exists()

	# Now sync the firmware to the host. We need to mock out the running of plugins so it doesn't
	# actually try to sync to hardware that doesn't exist.
	with inject_code(test_file("sync/mock_firmware_run_plugins.py")):
		result = host.run("stack sync host firmware force=true")
		assert result.rc == 0

	# Now it should have added back only the firmware for the switch-0-0 host that was to be synced.
	firmware_files_on_disk = [
		firmware_file for firmware_file in stack.firmware.BASE_PATH.glob(f"**/*")
		if firmware_file.is_file()
	]
	assert len(firmware_files_on_disk) == 6
	for firmware_file in firmware_files_on_disk:
		assert firmware_file.exists()
