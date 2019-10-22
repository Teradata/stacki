import stack.firmware

def test_sync_firmware_resync(host, fake_local_firmware_file, revert_firmware):
	"""Add some firmware, nuke the firmware dir, and then sync firmware and make sure it shows back up."""
	# Add a fake piece of firmware.
	result = host.run(f"stack add firmware 1.2.3 make=mellanox model=m7800 source={fake_local_firmware_file}")
	assert result.rc == 0

	# Now find the file on disk and nuke it. The files are given random UUID4 names,
	# so we have to glob for the file.
	firmware_file_on_disk = [
		firmware_file for firmware_file in stack.firmware.BASE_PATH.glob(f"**/*")
		if firmware_file.is_file()
	]
	assert len(firmware_file_on_disk) == 1
	firmware_file_on_disk = firmware_file_on_disk[0]
	firmware_file_on_disk.unlink()
	assert not firmware_file_on_disk.exists()

	# Now run the sync command.
	result = host.run("stack sync firmware")
	assert result.rc == 0

	# Make sure the file exists again.
	firmware_file_on_disk = [
		firmware_file for firmware_file in stack.firmware.BASE_PATH.glob(f"**/*")
		if firmware_file.is_file()
	]
	assert len(firmware_file_on_disk) == 1
	assert firmware_file_on_disk[0].exists()

def test_sync_firmware_selective_resync(host, fake_local_firmware_file, revert_firmware):
	"""Add two firmware files, nuke em both, selectively sync one and ensure that's the only one that shows back up."""
	result = host.run(f"stack add firmware 1.2.3 make=mellanox model=m7800 source={fake_local_firmware_file}")
	assert result.rc == 0
	result = host.run(f"stack add firmware 2.3.4 make=mellanox model=m7800 source={fake_local_firmware_file}")
	assert result.rc == 0

	# Now find the files on disk and nuke em. The files are given random UUID4 names,
	# so we have to glob for the file.
	firmware_files_on_disk = [
		firmware_file for firmware_file in stack.firmware.BASE_PATH.glob(f"**/*")
		if firmware_file.is_file()
	]
	assert len(firmware_files_on_disk) == 2
	for firmware_file in firmware_files_on_disk:
		firmware_file.unlink()
		assert not firmware_file.exists()

	# Now run the sync command.
	result = host.run(f"stack sync firmware 2.3.4 make=mellanox model=m7800")
	assert result.rc == 0

	# Make sure only one file exists
	firmware_files_on_disk = [
		firmware_file for firmware_file in stack.firmware.BASE_PATH.glob(f"**/*")
		if firmware_file.is_file()
	]
	assert len(firmware_files_on_disk) == 1
	assert firmware_files_on_disk[0].exists()
