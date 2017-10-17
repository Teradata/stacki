#
# @SI_Copyright@
# Copyright (c) 2006 - 2014 StackIQ Inc. All rights reserved.
# 
# This product includes software developed by StackIQ Inc., these portions
# may not be modified, copied, or redistributed without the express written
# consent of StackIQ Inc.
# @SI_Copyright@
#

import os
import sys
import json
import re
import stat
import subprocess

def __virtual__():
	return 'fio'

def _global():
	global_vars = {
		'numjobs' : 1,
		'runtime' : 10,
		'size' : '10g',
		'blocksize' : '128m',
		'ioengine' : 'sync',
		'direct' : 1,
		'buffered' : 0,
		'end_fsync' : 1,
	}
	return global_vars

def _rawdisk(filename, size = '5GB'):
	p = subprocess.Popen(['/sbin/parted', '-m', filename, '-s', 'print'],
		stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	o, e = p.communicate()
	rc = p.wait()
	if rc:
		return {}
	lines = o.split('\n')
	disk_found = False
	if lines[0] == 'BYT;':
		disk_found = True
	if not disk_found:
		return {}
	fields = lines[1].split(':')
	realsize = _get_size(fields[1])
	if realsize < _get_size(size):
		size = fields[1]

	return {
		'filename': filename,
	}

def _get_size(size):
	size_str = str(size).strip()
	size_fmt = re.compile(
		"([0-9]+(.[0-9]+)*)([kmg]?b)",
		flags=re.IGNORECASE
		)
	m = size_fmt.match(size)
	if not m:
		return 0
	unit = m.group(3).upper()
	if unit == "B":
		mul = 1
	if unit == "KB":
		mul = 1024
	if unit == "MB":
		mul = 1024 * 1024
	if unit == "GB":
		mul = 1024 * 1024 * 1024
	if unit == "TB":
		mul = 1024 * 1024 * 1024 * 1024
	size = float(m.group(1))
	return (size * mul)

def _part_info(filename, size):
	return {
		'filename': filename,
	}

def _mount_info(filename, size):
	if not os.path.exists(filename):
		dir = os.path.dirname(filename)
		if not os.path.exists(dir) or \
			not os.path.isdir(dir):
			return {}

	else:
		if os.path.isdir(filename):
			dir = filename
			filename = "%s/fio.img" % dir
		elif os.path.isfile(filename):
			dir = os.path.dirname(filename)
		else:
			return {}

	p = subprocess.Popen(['/bin/df','-P',dir],
		stdout = subprocess.PIPE,
		stderr = subprocess.PIPE)
	o, e = p.communicate()
	rc = p.wait()
	if rc:
		return {}

	line = o.split('\n')[1]
	avail = line.split()[3]
	if _get_size(size) > _get_size("%sKB" % avail):
		size = "%sKB" % avail

	return {
		'filename': filename,
	}

def run(tests):
	g_params = _global()
	global_params = ["[global]"]
	for i in g_params:
		global_params.append("%s=%s" % (i, g_params[i]))

	out = {}

	#
	# do the write tests first, then the read tests
	#
	cmd = ['/opt/rocks/bin/fio', '--output-format=json', '-']

	for testname, name, disk in tests:
		size = '10GB'

		spec_test = {}
		if testname == 'rawdisk': 
			filename = name
			spec_test = _rawdisk(filename, size)
		elif testname == 'mountpoint':
			filename = '%s/fio.img' % name
			spec_test = _mount_info(filename, size)
		else:
			continue

		if not spec_test:
			continue

		out[disk] = {}
		out[disk]['test'] = testname
		out[disk]['name'] = filename

		if testname == 'mountpoint':
			#
			# first do the write test 
			#
			p = subprocess.Popen(cmd, stdin  = subprocess.PIPE,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE)

			test_params = [ '[job]' ]
			test_params.append('readwrite=write')
			for i in spec_test:
				test_params.append("%s=%s" % (i, spec_test[i]))

			test_string = '\n'.join(global_params + test_params)
			o, e = p.communicate(test_string)
			rc = p.wait()

			if o:
				j = json.loads(o)
				job = j['jobs'][0]
				out[disk]['write_bw'] = job['write']['bw']
			else:
				out[disk]['write_bw'] = 0

			#
			# cleanup
			#
			os.unlink(filename)

		elif testname == 'rawdisk':
			out[disk]['write_bw'] = None

	#
	# now the read test 
	#
	file = open('/tmp/fio.debug', 'w+')
	for testname, name, disk in tests:
		size = '10GB'

		#
		# the read test will always read from the raw disk device
		#
		filename = '/dev/%s' % disk
		spec_test = _rawdisk(filename, size)

		file.write('filename: %s\n' % filename)
		file.write('spec_test: %s\n' % spec_test)

		if not spec_test:
			continue

		p = subprocess.Popen(cmd, stdin  = subprocess.PIPE,
			stdout = subprocess.PIPE, stderr = subprocess.PIPE)

		test_params = [ '[job]' ]
		test_params.append('readwrite=read')
		for i in spec_test:
			test_params.append("%s=%s" % (i, spec_test[i]))

		test_string = '\n'.join(global_params + test_params)
		o, e = p.communicate(test_string)
		rc = p.wait()

		# file.write('test_params: %s\n' % test_params)
		# file.write('o: %s\n' % o)

		if o:
			j = json.loads(o)
			job = j['jobs'][0]
			out[disk]['read_bw'] = job['read']['bw']
		else:
			out[disk]['read_bw'] = 0

	file.close()
	return out

