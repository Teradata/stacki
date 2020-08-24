import pytest
import os
import stack.api
import hashlib
import json


# Returns hash of filename
def get_hash(filename, sles):
	# SLES15 uses sha256
	if '15sp' in sles:
		hasher = hashlib.sha256()
	else:
		hasher = hashlib.md5()

	with open(filename, 'rb') as f:
		hasher.update(f.read())

	return hasher.hexdigest()


# Verify SLES patches are installed
def test_sles_pallet_patched(host, report_output):
	total_matched = []
	base_dir = '/export/stack/pallets/SLES/'
	if not os.path.isdir(base_dir):
		pytest.skip('No SLES pallet found - skipping patch check')
	sles_flavors = os.listdir(base_dir)
	assert sles_flavors

	# Find out where is stack-sles*images*.rpm file(s)
	result = host.run('find /export/stack/pallets/stacki/ -name "*stack-sles-*.rpm"')
	RPM = result.stdout.splitlines()
	assert RPM

	# If the stack-sles*images*.rpm installed?
	result = host.run('rpm -qa | grep stack | grep images')
	assert result

	# Test every sles flavor found
	for sles_flavor in sles_flavors:
		# Make sure installed patches match what's under /opt/stack/pallet-patches
		patch_dir = '/opt/stack/pallet-patches'
		patch_dir_files = []
		found_source = False
		for (dir_path, dir_names, filenames) in os.walk(patch_dir):
			# Only want particular SLES version
			if sles_flavor in dir_path:
				file_to_check = None
				if '15sp' in sles_flavor:
					file_to_check = 'CHECKSUMS'
				else:
					file_to_check = 'content'
				patch_dir_files += [os.path.join(dir_path, file) for file in filenames if file == file_to_check]

		# We should have non-empty list here
		assert patch_dir_files

		# Find img file from patch directory in SLES pallet
		result = host.run(f'grep .img {patch_dir_files[0]}')

		# Last item is the partial image path
		part_img_file = result.stdout.split()[-1]

		# Find full path to /export/stack/pallets/SLES/?
		result = host.run(f'probepal {base_dir}')
		assert result.rc == 0
		palinfo = json.loads(result.stdout)

        	# It shouldn't be empty
		assert palinfo[base_dir]
		
		sles_pallet_root = None 
		for pallet in palinfo[base_dir]:
			# Grab the right sles sp level
			if pallet['version'] == sles_flavor:
				assert host.file(f"{pallet['pallet_root']}").is_directory
				sles_pallet_root = pallet['pallet_root']
				break

		# .img file should exist in sles pallet directory in relative path
		assert os.path.exists(sles_pallet_root + '/' + part_img_file)

		# Verify all the stack-sles-* rpm packages 
		for rpm in RPM:
			# Make sure we found pm file
			assert '.rpm' in rpm

			result = host.run(f'rpm -qp --dump {rpm}')	
			# We don't want file under /opt/stack/images to be included in this list
			patch_files = [line.split() for line in result.stdout.splitlines() if sles_flavor in line and '/images/' not in line]

			matched_list = []
			# Verify file(s) from images RPM actually exist
			for this_list in patch_files:
				file_to_check = this_list[0]
				assert os.path.exists(file_to_check) 
				hash_value = this_list[3]

				# Grab hash for this file in patch directory and SLES pallet directory and compare against hash from img file. They should match
				# Need to build the equivalent path first
				temp_path_list = file_to_check.split('add-stacki-squashfs')	
				temp_path = sles_pallet_root + temp_path_list[1]
				if get_hash(file_to_check,sles_flavor) == hash_value and get_hash(temp_path, sles_flavor) == hash_value:
					matched_list.append(file_to_check)

			# Check if we found hash match as expected. Should be 4 files.	
			if matched_list and len(matched_list) == 4: 
				found_source = True
				# trim the string
				temp_path = rpm.split('stacki/')[1]
				temp_path_list = temp_path.split('/')
				version = temp_path_list[0]
				os_type = temp_path_list[1]
				version_string = 'stacki-' + version + '-' + os_type + '-sles-x86_64'
				# Don't want duplicate entry
				if version_string not in total_matched:
					total_matched.append(version_string)

		# Didn't find stacki source for this os
		assert found_source == True

	for match in total_matched:
		report_output('SLES pallet patch source', match)
