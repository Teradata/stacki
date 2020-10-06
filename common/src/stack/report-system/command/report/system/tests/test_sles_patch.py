import pytest
import os
import stack.api
import hashlib
import json
import pathlib
import pprint
import collections 

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

def nested_dict():
	return collections.defaultdict(nested_dict)

# Verify SLES patches are installed
def test_sles_pallet_patched(host, report_output):
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
	assert result.rc == 0

	overall_dict = nested_dict()

	# Test every sles flavor found
	for sles_flavor in sles_flavors:
		# Make sure installed patches match what's under /opt/stack/pallet-patches
		patch_dir = '/opt/stack/pallet-patches'
		patch_dir_files = []
		not_matched_list = []
		for (dir_path, dir_names, filenames) in os.walk(patch_dir):
			# Only want particular SLES version
			if sles_flavor in dir_path:
				if '15sp' in sles_flavor:
					pattern = f'SLES-{sles_flavor}-*/**/CHECKSUMS'
				else:
					pattern = f'SLES-{sles_flavor}-*/**/content'

				# SLES-12sp3-sles12-sles-x86_64	
				patch_dir_files = list(pathlib.Path(patch_dir).glob(pattern))

		# We should have 1 file here
		assert len(patch_dir_files) == 1

		# Last item is the partial image path
		part_img_file = [
			line for line in patch_dir_files[0].read_text().splitlines()
			if line.endswith('.img')
		][-1].split()[-1]

		# Find full path to /export/stack/pallets/SLES/?
		result = host.run(f'probepal {base_dir}')
		assert result.rc == 0
		palinfo = json.loads(result.stdout)

        	# It shouldn't be empty
		assert palinfo[base_dir]
		
		#sles_pallet_root = None
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
			result = host.run(f'rpm -qp --dump {rpm}')	
			# We don't want file under /opt/stack/images to be included in this list
			patch_files = [
				line.split() for line in result.stdout.splitlines()
				if sles_flavor in line 
				if '/add-stacki-squashfs/' in line
			]

			matched_list = []
			not_matched_list = []
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
				else:
					not_matched_list.append(file_to_check)

			# Add info we have into nested dictionary 
			good_dict = {rpm: []}
			bad_dict = {rpm: []}
			# Check if we found all the hash matches 	
			if matched_list and len(matched_list) == len(patch_files): 
				# this indicates if hash match was found for a sles flavor or not
				good_dict[rpm].append(matched_list)
				overall_dict[sles_flavor]['good'].update({rpm: matched_list})
			elif not_matched_list:# and len(not_matched_list) == len(patch_files):
				bad_dict[rpm].append(not_matched_list)
				overall_dict[sles_flavor]['bad'].update({rpm: not_matched_list})

	# Print entire dictionary for debug
	#pp = pprint.PrettyPrinter(indent=4)
	#pp.pprint(overall_dict)

	assert overall_dict
	# over all test result
	final_status = True
	for os_, results in overall_dict.items():
		success = False 
		if 'good' in results:
			success = True
		for result, rpms in results.items():
			for rpm, filelist in rpms.items():
				if result == 'good':
					temp_path = rpm.split('stacki/')[1]
					temp_path_list = temp_path.split('/')
					version = temp_path_list[0]
					os_type = temp_path_list[1]
					version_string = 'stacki-' + version + '-' + os_type + '-sles-x86_64'
					output = version_string + '\n'
					report_output(f'SLES{os_} pallet patch source', output)
				else:
					# if we already found good case then skip all the bad cases
					if success: 
						continue;
					else:
						# overall status is bad if we find one valid bad case
						final_status = False
						output = ''
						for val in rpms.get(rpm):
							if len(output) == 0:
								output = val
							else:
								output = output + '\n' + val
						output += '\n'
						report_output(f'SLES{os_} pallet patch source NOT found', output)
	assert final_status 
