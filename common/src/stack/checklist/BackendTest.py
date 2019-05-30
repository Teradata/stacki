#!/opt/stack/bin/python3

from collections import deque
import os
from functools import partial
import re
import socket
import subprocess
import sys
import time

"""
Global function that invokes smq-publish script to
post messages to the 'health' channel
"""
def sendStateToMsgQ(state, isErr, msg=''):
	pyenv = os.environ.copy()
	pyenv["LD_LIBRARY_PATH"] = "/opt/stack/lib/"

	if 'PYTHONPATH' in pyenv:
		del pyenv['PYTHONPATH']

	cmd = ['/opt/stack/bin/smq-publish', 
		'-chealth', 
		'-t300',
		'{"systest":"%s","flag":"%s","msg":"%s"}' \
		% (state, str(isErr), msg)]
	subprocess.run(cmd, env=pyenv)

	#
	# Send status update to health channel if installation is stalled or in
	# wait mode, so it can be processed by MQ health processor
	#
	if state.lower() in ['stalled', 'wait']:
		cmd = ['/opt/stack/bin/smq-publish', '-chealth',
			'{"state":"%s %s"}' % (state, msg)]
		subprocess.run(cmd, env=pyenv)

class YastLogReader:
	"""
	Reads y2log file to see if installation has stalled
	"""
	YAST_LOG = '/var/log/YaST2/y2log'
	SLEEP_TIME = 2

	def run(self):
		# Wait until log file is available
		while not os.path.isfile(YastLogReader.YAST_LOG):
			time.sleep(YastLogReader.SLEEP_TIME)

		# Create 3 element queue to store last 3 lines from log file
		q = deque( maxlen=3 )
		with open(YastLogReader.YAST_LOG, "r", errors='replace') as file:
			file.seek(0, 2)

			while True:
				where = file.tell()
				line  = file.readline()

				if not line:
					time.sleep(1)
					file.seek(where)
	
					if q and 'YPushButton.cc' in q[-1]:
						modifiedTime = os.path.getmtime(YastLogReader.YAST_LOG)
						currentTime  = time.time()
						#
						# If log has not been updated in the past 2 minutes,
						# the installation maybe stalled
						#
						if int(currentTime - modifiedTime) > 120:
							msg = []
							for elem in q:
								msg.append(elem.replace('"', '').strip())

							sendStateToMsgQ('Installation_Stalled', \
								True, "\\n".join(msg))

							# Clear elements in q
							q.clear()
				else:
					q.append(line)

class CheckWait:
	"""
	Checks for the presence of /tmp/wait file through the install
	and generate an Install_Wait message if the file exists.
	"""
	WAIT_FILE = '/tmp/wait'
	SLEEP_TIME = 15

	def run(self):
		while True:
			if os.path.isfile(CheckWait.WAIT_FILE):
				sendStateToMsgQ('Install_Wait', False, 'Install Paused')

			time.sleep(CheckWait.SLEEP_TIME)

class BackendTest:
	"""
	Main class that runs a sequence of tests that indicate the progress
	of installation
	"""
	PARTITION_FILE_SLES   = '/tmp/partition.xml'
	PARTITION_FILE_REDHAT = '/tmp/partition-info'
	LUDICROUS_LOG         = '/var/log/ludicrous-client-debug.log'
	NUM_RETRIES           = 100
	SLEEP_TIME            = 10

	"""
	Checks if a file size is 0
	"""
	def isEmptyFile(self, filepath):
		return os.stat(filepath).st_size == 0

	"""
	Checks for the presence of autoinst.xml file
	"""
	def checkAutoyastFiles(self):
		autoyastFile = '/tmp/profile/autoinst.xml'
		#
		# Once SSH is available, the autoyast, stacki chapets should have
		# already been created
		#
		if self.isEmptyFile(autoyastFile):
			msg = 'Backend - %s profile file - Empty' % autoyastFile
			sendStateToMsgQ("AUTOINST_Present", True, msg)
		else:
			msg = 'Backend - %s - Present' % autoyastFile
			sendStateToMsgQ("AUTOINST_Present", False, msg)

	"""
	Checks if a file exists. If it does nt exist, keep retrying for
	specific number of times.
	"""
	def checkFileExists(self, path):
		i = 0

		while i < BackendTest.NUM_RETRIES: 
			if os.path.isfile(path):
				return True

			time.sleep(BackendTest.SLEEP_TIME)
			i = i + 1

		return False

	"""
	Checks if ludicrous client log file is populated with messages
	"""
	def checkPkgInstall(self):
		count = 0

		while count < BackendTest.NUM_RETRIES:
			if not self.isEmptyFile(BackendTest.LUDICROUS_LOG):
				msg = 'Backend - %s log file - Populated with' \
					' installed packages' % BackendTest.LUDICROUS_LOG
				sendStateToMsgQ("Ludicrous_Populated", False, msg)
				return

			time.sleep(BackendTest.SLEEP_TIME * 3)
			count = count + 1

		msg = 'Backend - %s log file is empty - Check if Ludicrous is okay' \
			% BackendTest.LUDICROUS_LOG
		sendStateToMsgQ("Ludicrous_Populated", True, msg)

	"""
	Checks if ludicrous-client-debug.log file exists. This indicates whether
	the ludicrous client service has started successfully.
	"""
	def checkLudicrousStarted(self):
		if self.checkFileExists(BackendTest.LUDICROUS_LOG):
			msg = 'Backend - Ludicrous Service - Started'
			sendStateToMsgQ("Ludicrous_Started", False, msg)
		else:
			msg = 'Backend - Ludicrous Service - May not have' \
				' been started' % BackendTest.LUDICROUS_LOG
			sendStateToMsgQ("Ludicrous_Started", True, msg)

	"""
	Checks if partition file is present
	"""
	def checkPartitionFile(self, partitionFileName):
		if self.checkFileExists(partitionFileName):
			msg = 'Backend - %s - Present' % partitionFileName
			sendStateToMsgQ("Partition_File_Present", False, msg)
		else:
			msg = 'Backend - %s - Not Present' % partitionFileName
			sendStateToMsgQ("Partition_File_Present", True, msg)

	"""
	Checks if SSH port 2200 is open
	"""
	def checkSSHOpen(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		count = 1
		result = -1
		msg = ''

		while count <= BackendTest.NUM_RETRIES:
			result = sock.connect_ex(('127.0.0.1', 2200))
			if result == 0:
				sendStateToMsgQ("SSH_Open", False, msg)
				break

			count = count + 1
			time.sleep(BackendTest.SLEEP_TIME)

		if result != 0:
			msg = 'Error - SSH Port 2200 is not yet open'
			sendStateToMsgQ("SSH_Open", True, msg)

		sock.close()

	"""
	Main function that runs a series of tests which validates various
	states of a backend installation.
	"""
	def run_sles(self):
		#
		# Sequence of tests (in the same order) that need to be run on
		# the installing node
		#
		test_list = [self.checkSSHOpen, self.checkAutoyastFiles,
				self.checkLudicrousStarted,
				partial(self.checkPartitionFile, BackendTest.PARTITION_FILE_SLES),
				self.checkPkgInstall]

		#
		# Parent process creates 2 child processes
		# Child 1 - Checks for /tmp/wait file to detect INSTALL_WAIT state
		# Child 2 - Reads y2log file to detect INSTALLATION_STALLED state
		# Child 3 - Runs all the tests defined in test_list list.
		#
		child1pid = os.fork()
		if child1pid == 0:
			chkWait = CheckWait()
			chkWait.run()
			os._exit(os.EX_OK)

		child2pid = os.fork()
		if child2pid == 0:
			yastLogReader = YastLogReader()
			yastLogReader.run()
			os._exit(os.EX_OK)

		#
		# Spawn child process to handle other tests so parent does nt
		# block the install
		#
		child3pid = os.fork()
		if child3pid == 0:
			for test in test_list:
				test()
			os._exit(os.EX_OK)

	def run_redhat(self):
		test_list = [self.checkSSHOpen, self.checkLudicrousStarted,
			partial(self.checkPartitionFile, BackendTest.PARTITION_FILE_REDHAT),
			self.checkPkgInstall]

		child3pid = os.fork()
		if child3pid == 0:
			for test in test_list:
				test()
			os._exit(os.EX_OK)

if __name__ == "__main__":
	b = BackendTest()

	sys.path.append('/tmp')
	from stack_site import attributes

	if attributes['os'] == 'sles':
		b.run_sles()
	elif attributes['os'] == 'redhat':
		b.run_redhat()
