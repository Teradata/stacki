# @copyright@
# @copyright@
#!/opt/stack/bin/python3
from collections import deque
import os
import re
import subprocess
import threading
import time

#
# Global function that invokes command to
# post messages to the 'health channel
#
def outputState(state, flag, msg=''):
	pyenv = os.environ.copy()
	pyenv["LD_LIBRARY_PATH"] = "/opt/stack/lib/"

	if 'PYTHONPATH' in pyenv:
		del pyenv['PYTHONPATH']

	cmd = ['/opt/stack/bin/smq-publish', 
		'-chealth', 
		'-t300',
		'{"systest":"%s","flag":"%s","msg":"%s"}' % (state, str(flag), msg)]

	subprocess.run(cmd, env=pyenv)

	# Send status update if install is stalled
	if state.lower() in ['stalled', 'wait']:
		cmd = ['/opt/stack/bin/smq-publish', '-chealth', \
			'{"state":"%s"}' % flag.lower()]
		subprocess.run(cmd, env=pyenv)

class YastLogReader(threading.Thread):
	"""
	Read y2log to see if installation has stalled
	"""
	YAST_LOG = '/var/log/YaST2/y2log'
	SLEEP_TIME = 2

	def run(self):
		# Wait until log file is available
		while True:
			if not os.path.isfile(YastLogReader.YAST_LOG):
				time.sleep(YastLogReader.SLEEP_TIME)
			else:
				break

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

							outputState('Installation_Stalled', \
								True, "\\n".join(msg))

							# Clear elements in q
							q.clear()
				else:
					q.append(line)

class CheckWait(threading.Thread):
	"""
	Check for WAIT status through the install
	"""
	WAIT_FILE = '/tmp/wait'
	SLEEP_TIME = 15

	def run(self):
		while True:
			if os.path.isfile(CheckWait.WAIT_FILE):
				time.sleep(CheckWait.SLEEP_TIME)
				outputState('Install_Wait', False, 'Install Paused')

class BackendTest:
	"""
	Sequence of tests that indicate the progress of installation
	"""
	PARTITION_XML = '/tmp/partition.xml'
	LUDICROUS_LOG = '/var/log/ludicrous-client-debug.log'
	NUM_RETRIES   = 10
	SLEEP_TIME    = 10

	def isEmptyFile(self, filepath):
		return os.stat(filepath).st_size == 0

	def checkAutoyastFiles(self):
		autoyastFile = '/tmp/profile/autoinst.xml'
		#
		# Once SSH is available, the autoyast, stacki chapets should have
		# already been created
		#
		if self.isEmptyFile(autoyastFile):
			msg = 'Backend - %s profile file - Empty' % autoyastFile
			outputState("AUTOINST_Present", True, msg)
		else:
			msg = 'Backend - %s - Present' % autoyastFile
			outputState("AUTOINST_Present", False, msg)

	def checkFileExists(self, path):
		i = 0

		while i < BackendTest.NUM_RETRIES: 
			if os.path.isfile(path):
				return True

			time.sleep(BackendTest.SLEEP_TIME)
			i = i + 1

		return False

	def checkPkgInstall(self):
		count = 0

		while count < BackendTest.NUM_RETRIES:
			if not self.isEmptyFile(BackendTest.LUDICROUS_LOG):
				msg = 'Backend - %s log file - Populated with' \
					' installed packages' % BackendTest.LUDICROUS_LOG
				outputState("Ludicrous_Populated", False, msg)
				return

			time.sleep(BackendTest.SLEEP_TIME)
			count = count + 1

		msg = 'Backend - %s log file is empty - Check if Ludicrous is okay' \
			% BackendTest.LUDICROUS_LOG
		outputState("Ludicrous_Populated", True, msg)

	def checkLudicrousStarted(self):
		if self.checkFileExists(BackendTest.LUDICROUS_LOG):
			msg = 'Backend - Ludicrous Service - Started'
			outputState("Ludicrous_Started", False, msg)
		else:
			msg = 'Backend - Ludicrous Service - May not have' \
				' been started' % BackendTest.LUDICROUS_LOG
			outputState("Ludicrous_Started", True, msg)

	def checkPartition(self):
		if self.checkFileExists(BackendTest.PARTITION_XML):
			msg = 'Backend - %s - Present' % BackendTest.PARTITION_XML
			outputState("Partition_XML_Present", False, msg)
		else:
			msg = 'Backend - %s - Not Present' % BackendTest.PARTITION_XML
			outputState("Partition_XML_Present", True, msg)

	def run(self):
		test_list = [self.checkAutoyastFiles, self.checkLudicrousStarted,  \
				self.checkPartition, self.checkPkgInstall]

		# Check for WAIT status through the install
		chkWait = CheckWait()
		chkWait.setDaemon(True)
		chkWait.start()

		yastLogReader = YastLogReader()
		yastLogReader.setDaemon(True)
		yastLogReader.start()

		for test in test_list:
			test()

		chkWait.join()

if __name__ == "__main__":
	b = BackendTest()
	b.run()
