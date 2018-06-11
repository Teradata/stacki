import pytest
import subprocess
import json
import os
from cStringIO import StringIO

"""To run this separately/manually:
cd test-suites/system/04*
./set-up.sh stacki-5.*sles12.x86_64.disk1.iso
# Wait a long time..
source ../../../bin/activate
pytest -n 5 --hosts=frontend --ssh-config=".cache/ssh-config" tests/ -vvv
"""

# GLOBALS #
# I guess we could pass these around through arguments, but this seemed easier when thinking through parallel uses.
TEST_SCENARIOS = (["tdc_multi_disk", "DEFAULT", "msdos"],
				["tdc_multi_disk", "DEFAULT", "gpt"],
				["tdc_multi_disk", "SLES_11", "msdos"],
				["tdc_multi_disk", "SLES_11", "gpt"],
				["tdc_single_disk", "DEFAULT", "msdos"],
				["tdc_single_disk", "DEFAULT", "gpt"],
				["tdc_single_disk", "SLES_11", "msdos"],
				["tdc_single_disk", "SLES_11", "gpt"],
				["xfs", "DEFAULT", "msdos"],
				["xfs", "DEFAULT", "gpt"],
				["xfs", "SLES_11", "msdos"],
				["xfs", "SLES_11", "gpt"])
RUN_NUM = 0

with open(".cache/state.json") as json_file:
	my_json = json.load(json_file)
	NAME = my_json['NAME']
	# BACKEND_TUPLE = ('backend-0-0', 'backend-0-1', 'backend-0-2', 'backend-0-3', 'backend-0-4', 'backend-0-5')
	BACKEND_TUPLE = tuple(my_json['BACKENDS'])
	print(BACKEND_TUPLE)
	TEST_SLES_11 = os.path.isfile(my_json['SLES_11_STACKI_ISO'])


# @pytest.mark.parametrize("backend", ("backend-0-0", "backend-0-1", "backend-0-2"))
# def test_frontend_ssh_to_backends(host, backend):
def frontend_ssh_to_backends(host, backend):
	"""Test that the frontend can SSH to its backends"""
	command_returns = []
	cmd = host.run("sudo -i ssh %s cat /etc/hostname".format(backend))
	assert cmd.stdout.strip() == "%s.localdomain".format(backend)
	assert (cmd.rc == 0)
	return all(command_returns)


def get_partition_scenario(backend):
	"""Need to figure out which test scenario we need to run.

	This is implemented for parallel testing, so it is variable to the number of backends"""
	backend_tuple_address = -1
	i = 0
	for each_backend in BACKEND_TUPLE:
		if backend == each_backend:
			backend_tuple_address = i
		i += 1
	assert backend_tuple_address >= 0
	test_scenario_address = len(BACKEND_TUPLE) * RUN_NUM + backend_tuple_address
	if test_scenario_address < len(TEST_SCENARIOS):
		return TEST_SCENARIOS[test_scenario_address]
	else:
		return None

# def find_available_backend:
#	 """Lock backend for our testing then return string of the name"""
#
# def get_backend():
#	 """Need to figure out which backend is available.
#
#	 This is implemented for parallel testing, so it is variable to the number of backends"""
#	 backend = None
#	 backend = find_available_backend()
#	 while backend == None:
#		 time.sleep(10)
#		 backend = find_available_backend()
#	 return backend


def setup_partitioning(host, backend, test_scenario):
	"""Create the partitioning csv for stacki loading"""
	import csv
	partition_config = []
	fieldnames = ["Name", "Device", "Mountpoint", "Size", "Type", "Options"]

	if "tdc_" in test_scenario[0]:
		partition_config = [
			{'Name': str('%s' % backend), 'Device': 'sda', 'Mountpoint': '', 'Type': '',
			 'Options': '--asprimary --partition_id=18', 'Size': '40'},
			{'Name': '', 'Device': 'sda', 'Mountpoint': '/', 'Type': 'ext3', 'Options': '--asprimary --label=ROOT-BE1',
			 'Size': '30720'},
			{'Name': '', 'Device': 'sda', 'Mountpoint': '', 'Type': 'ext3', 'Options': '--asprimary --label=ROOT-BE2',
			 'Size': '30720'},
			{'Name': '', 'Device': 'sda', 'Mountpoint': '/var', 'Type': 'ext3', 'Options': '--label=VAR-BE1',
			 'Size': '5120'},
			{'Name': '', 'Device': 'sda', 'Mountpoint': '', 'Type': 'ext3', 'Options': '--label=VAR-BE2',
			 'Size': '5120'},
			{'Name': '', 'Device': 'sda', 'Mountpoint': '/var/opt/teradata', 'Type': 'ext3',
			 'Options': '--label=TERADATA', 'Size': '0'}]
	if test_scenario[0] == "tdc_multi_disk":
		partition_config.append({'Name': '', 'Device': 'sdb', 'Mountpoint': '/var/opt/teradata/data1', 'Type': 'xfs',
								 'Options': '--label=data1', 'Size': '64'})
		partition_config.append({'Name': '', 'Device': 'sdb', 'Mountpoint': '/var/opt/teradata/data1/sub_d1',
								 'Type': 'xfs', 'Options': '--label=sub_d1', 'Size': '0'})
	elif test_scenario[0] == "xfs":
		# This is to test the defaults work as well, if we make tdc the default we need to write a real csv for this
		pass

	fake_file = StringIO()
	writer = csv.DictWriter(fake_file, fieldnames=fieldnames)
	writer.writeheader()
	for each in partition_config:
		writer.writerow(each)
	# with open("%s_partition.csv".format(backend), 'w+') as csvfile:
	#		 writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	#		 writer.writeheader()
	#		 for each in partition_config:
	#			 writer.writerow(each)

	# Loading the CSV is super hacky. I couldn't do a with open on the remote host/frontend
	# So I am echoing the string into a file.
	my_string = ""
	for each in fake_file.getvalue().splitlines():
		my_string += "\\n" + each
	cmd = host.run('sudo -i echo -e "%s"' % my_string + " > /home/vagrant/%s_partition.csv" % backend)
	assert cmd.rc == 0
	cmd = host.run("sudo -i stack remove host storage partition %s" % backend)
	assert cmd.rc == 0
	cmd = host.run("sudo -i stack load storage partition file=/home/vagrant/%s_partition.csv" % backend)
	if test_scenario[0] != "xfs":
		assert cmd.rc == 0
	cmd = host.run(str("sudo -i stack set host attr %s attr=disklabel value=" % backend) + test_scenario[2])
	assert cmd.rc == 0
	return partition_config


def setup_os(host, backend, test_scenario, nukedisk=True, no_attr=False):
	"""Setup the os for installing by applying the box and proper installaction"""
	if test_scenario[1] == "SLES_11":
		cmd = host.run("sudo -i stack set host box %s box=sles11" % backend)
		assert cmd.rc == 0
		cmd = host.run("sudo -i stack set host installaction %s action='install sles 11.3'" % backend)
		assert cmd.rc == 0
	elif test_scenario[1] == "DEFAULT":
		cmd = host.run("sudo -i stack set host box %s box=default" % backend)
		assert cmd.rc == 0
		cmd = host.run("sudo -i stack set host installaction %s action='default'" % backend)
		assert cmd.rc == 0
	cmd = host.run(str("sudo -i stack set host boot %s action=install nukedisks=" % backend) + str(nukedisk))
	assert cmd.rc == 0
	if no_attr and not nukedisk:
		cmd = host.run("sudo -i stack remove host attr %s attr=nukedisks" % backend)
		assert cmd.rc == 0


def touch_touchy(host, backend, test_file):
	"""touch some files to later make sure they are erased (or not) on reinstall"""
	cmd = host.run("sudo -i ssh %s touch %s" % (backend, test_file))
	assert cmd.rc == 0


def check_ls(host, backend, test_file, should_exist=True):
	"""Make sure the files are either gone or still there depending on should_exist"""
	cmd = host.run("sudo -i ssh %s ls %s" % (backend, test_file))
	print(cmd.stdout)
	if should_exist:
		assert cmd.rc == 0
	else:
		# Depending on the OS, it may have quotes around the file...
		if cmd.stderr.strip() == "ls: cannot access %s: No such file or directory" % test_file:
			assert cmd.stderr.strip() == "ls: cannot access %s: No such file or directory" % test_file
		else:
			assert cmd.stderr.strip() == "ls: cannot access '%s': No such file or directory" % test_file
		assert cmd.rc == 2


def check_fstab_and_blkid(fstab, details, blkid):
	"""Makes sure that label was utilized or that a UUID was used."""
	label = None
	fs_check = []
	# print("fstab: %s" % fstab)
	# print("mountpoint: %s" % details['Mountpoint'])
	# print("options: %s" % details['Options'])
	# print("blkid: %s" % blkid)
	for arg in details['Options'].split():
		if '--label=' in arg:
			label = arg.split('=')[1]
	if label and '/' in details['Mountpoint']:
		for line in fstab.splitlines():
			fs_check.append(label in line and details['Mountpoint'] in line)
	elif label is None and '/' in details['Mountpoint']:
		for line in fstab.splitlines():
			fs_check.append("UUID" in line and details['Mountpoint'] in line)
	else:
		fs_check.append(True)
	if details['Type'] is None or details['Type'] == '':
		blk_check = True
	elif label is None:
		blk_check = "UUID" in blkid
	else:
		blk_check = label in blkid
	# print fs_check
	# print blk_check
	return all([any(fs_check), blk_check])


def get_block_id(host, backend, each, partition_num):
	"""Grab the blkid output for the given partition"""
	current_partition = each['Device'] + str(partition_num)
	cmd = host.run("sudo -i ssh %s blkid /dev/%s" % (backend, current_partition))
	return cmd.stdout


def partition_incrementor(i, new_extended_partition, current_partition, test_scenario, partitions):
	""" Need to have extra partition number added if new extended partition detected"""
	# print("partition_incrementor")
	# print("i: %s" % i)
	# print("new_extended_partition: %s" % new_extended_partition)
	# print("current_partition: %s" % current_partition)
	# print("test_scenario: %s" % test_scenario)

	# Need to check if there is not asprimary declared, so that all are primary, and we can break early.
	# Requires the knowledge of other partition configs, so we need the entire partitions data
	primary_partitions_only = []
	for each in partitions:
		# print("each['Device']: %s" % each['Device'])
		# print("current_partition['Device']: %s" % current_partition['Device'])
		if each['Device'] == current_partition['Device']:
			primary_partitions_only.append("--asprimary" not in each['Options'])

	# print("primary_partitions_only: %s" % primary_partitions_only)
	if all(primary_partitions_only):
		return i, new_extended_partition
	if test_scenario[2] == "msdos":
		if not new_extended_partition and "--asprimary" not in current_partition['Options']:
			new_extended_partition = True
			i += 1
		elif new_extended_partition and "--asprimary" in current_partition['Options']:
			# Reset the detection so we increment again on a new extended partition
			new_extended_partition = True
	# print("i: %s" % i)
	# print("test_scenario: %s" % test_scenario)
	return i, new_extended_partition


def dev_incrementor(i, current_dev, new_extended_partition, current_partition):
	"""Count partition numbers reset when new sd<x> found"""
	if current_dev != current_partition['Device']:
		i = 1
		new_extended_partition = False
		current_dev = current_partition['Device']
	return i, current_dev, new_extended_partition


def check_if_backend_stuck(host, backend):
	"""There are a few UI related prompts that will make the install get stuck. Add additional checks to list."""
	error_list = ['YOKButton']
	for bad_string in error_list:
		cmd = host.run("sudo -i ssh -p 2200 %s 'tail /var/log/YaST2/y2log' | grep -c %s" % (backend, bad_string))
		assert cmd.stdout.strip() == "0"


def wait_for_install(host, backend):
	"""Reboot and wait for the reinstall"""
	i = 0
	cmd = host.run("sudo -i stack list host boot %s" % backend)
	assert cmd.rc == 0
	print(cmd.stdout)
	# assert nukedisk is True
	host.run("sudo -i ssh %s sync" % backend)
	while "install" in cmd.stdout:
		host.run("sudo -i stack list host %s" % backend)
		if "installing packages" not in cmd.stdout.lower():
			subprocess.call(str("VBoxManage controlvm %s_%s reset" % (NAME, backend)).split())
			host.run("sudo -i ssh %s init 6" % backend)
			host.run("sleep 30")
			cmd = host.run("sudo -i ssh % s cat /proc/uptime | awk '{print $1}'" % backend)
			print(cmd.stdout)
		host.run("i=0;while sleep 60; do sudo -i ssh %s 'exit 0' && break; i=$((i+1)); "
				 "if [[ $i -gt 20 ]]; then exit 1; fi; done" % backend)
		i += 1
		if i > 2:
			host.run("sudo -i systemctl restart dhcpd")
			i = 0
		cmd = host.run("sudo -i stack list host boot %s" % backend)
		check_if_backend_stuck(host, backend)
	# Too many post ssh issues, better to wait a minute...
	host.run("sleep 60")
	cmd = host.run("date")
	print(cmd.stdout)
	# If we ssh keys aren't all synced up yet, wait a minute:
	# host.run("ssh-keygen -R %s -f /root/.ssh/known_hosts" % backend)
	cmd = host.run("sudo -i ssh %s 'exit 0'" % backend)
	i = 0
	while "REMOTE HOST IDENTIFICATION HAS CHANGED" in cmd.stderr:
		host.run("sleep 60")
		host.run("sudo -i ssh-keygen -R %s -f /root/.ssh/known_hosts" % backend)
		cmd = host.run("sudo -i ssh %s 'exit 0'" % backend)
		i += 1
		assert i < 5

	cmd = host.run("date")
	print(cmd.stdout)


def powered_on(backend):
	"""Check if host is powered on or not"""
	is_powered_on = True
	state = subprocess.Popen(str("VBoxManage showvminfo %s_%s" % (NAME, backend)).split(), stdout=subprocess.PIPE)
	for line in state.communicate()[0].splitlines():
		if "state:" in line.lower():
			is_powered_on = "powered off" not in line.lower()
			# print(line)
	return is_powered_on


def check_backend_reinstall(host, backend, nukedisk=True, first_install=True, no_attr=False):
	"""Test different scenarios for reinstalls."""
	# This function is getting too large, should really break out a bit.
	test_scenario = get_partition_scenario(backend)
	if test_scenario is None or (test_scenario[1] == "SLES_11" and not TEST_SLES_11):
		# Get out of here if there is nothing to do
		# Including if we got a SLES 11 test while not having a SLES 11 iso to test against.
		return None
	else:
		partitions = setup_partitioning(host, backend, test_scenario)
		setup_os(host, backend, test_scenario, nukedisk, no_attr)
		# Create data files if backend is running
		if powered_on(backend) and not first_install:
			for each in partitions:
				if '/' in each['Mountpoint']:
					print("Touched: %s" % os.path.join(each['Mountpoint'], "test"))
					touch_touchy(host, backend, os.path.join(each['Mountpoint'], "test"))
					check_ls(host, backend, os.path.join(each['Mountpoint'], "test"), True)
			if not partitions:
				# need to handle the blank partitions defaults, so hardcoded:
				touch_touchy(host, backend, "/state/partition1/test")
				touch_touchy(host, backend, "/test")
				touch_touchy(host, backend, "/var/test")
		else:
			print("Didn't Touch ")
			subprocess.call(str("VBoxManage startvm %s_%s --type headless" % (NAME, backend)).split())
		print(partitions)
		# print("sudo -i stack list host boot %s" % (backend))
		# print(cmd.stdout)
		print("nukedisk: %s" % nukedisk)
		cmd = host.run("date")
		print(cmd.stdout)
		wait_for_install(host, backend)
		# Check that the partitioning and disk nuking worked as expected:
		cmd = host.run("sudo -i ssh %s cat /etc/fstab" % backend)
		assert cmd.rc == 0
		fstab = cmd.stdout
		i = 1
		current_dev = None
		new_extended_partition = False
		for each in partitions:
			i, current_dev, new_extended_partition = dev_incrementor(i, current_dev, new_extended_partition, each)
			# These should never exist after a reinstall, even if nukedisk=False
			if each['Mountpoint'] in ['/', '/var', '/boot', '/bootefi']:
				# print(each)
				check_ls(host, backend, os.path.join(each['Mountpoint'], "test"), should_exist=False)
			elif '/' in each['Mountpoint']:
				# print(each)
				check_ls(host, backend, os.path.join(each['Mountpoint'], "test"), not nukedisk)
			i, new_extended_partition = partition_incrementor(i, new_extended_partition, each, test_scenario,
															  partitions)
			blkid = get_block_id(host, backend, each, i)
			assert check_fstab_and_blkid(fstab, each, blkid) is True
			i += 1
		if not partitions:
			# need to handle the blank partitions defaults, so hardcoded:
			check_ls(host, backend, "/state/partition1/test", not nukedisk)
			check_ls(host, backend, "/test", should_exist=False)
			check_ls(host, backend, "/var/test", should_exist=False)


@pytest.mark.parametrize("backend", BACKEND_TUPLE)
def test_nukedisk_false(host, backend):
	"""Test that the frontend can reinstall its backends without nuking disks"""
	run_throughs = int((len(BACKEND_TUPLE) + len(TEST_SCENARIOS) - 1 / len(BACKEND_TUPLE)))
	global RUN_NUM
	for i in range(0, run_throughs):
		RUN_NUM = i
		# First we need to install with nukedisk=True to be sure partitioning is correct
		check_backend_reinstall(host, backend, nukedisk=True, first_install=True)
		check_backend_reinstall(host, backend, nukedisk=True, first_install=False)
		check_backend_reinstall(host, backend, nukedisk=False, first_install=False)
		check_backend_reinstall(host, backend, nukedisk=False, first_install=False, no_attr=True)


