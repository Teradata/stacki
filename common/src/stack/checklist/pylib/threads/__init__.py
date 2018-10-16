# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
from datetime import datetime
import copy
import json
import logging
import paramiko
import re
import socket
import shlex
import stack.bool
from stack.checklist import State, StateMessage, StateSequence
import stack.mq.processors
import time
import threading
import queue

class LogParser(threading.Thread):
	"""
	Parses log messages and appends those relevant to system
	installation to the shared queue.
	"""

	IP_REGEX   = re.compile("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
	MAC_REGEX  = re.compile("(?:[0-9a-fA-F]:?){12}")
	DHCP_REGEX = re.compile("DHCP\w*")
	URL_REGEX  = re.compile("GET (.*?) HTTP")

	SSL_ACCESS_LOG_MAP = {
		'/install/sbin/profile.cgi?' : State.Profile_XML_Sent,
		'/install/sbin/public/setPxeboot.cgi?' : State.Set_Bootaction_OS,
		'/install/sbin/public/setDbPartitions.cgi' : State.Set_DB_Partitions
	}

	ACCESS_LOG_MAP = {
		'config' : State.Config_Sent,
		'common' : State.Common_Sent,
		'root'   : State.Root_Sent,
		'cracklib-dict-full.rpm' : State.Cracklib_Dict_Sent,
		'bind' : State.Bind_Sent,
		'sles-stacki.img' : State.SLES_Img_Sent
	}

	HTTP_SUCCESS = '200'

	def __init__(self, path, queue):
		super(self.__class__, self).__init__()
		self.path = path
		self.globalQ = queue
		self.parseFunc = self.parseAccessLog

		if '/var/log/messages' in path:
			self.parseFunc = self.parseVarlog
		elif 'ssl_access_log' in path:
			self.parseFunc = self.parseSSLAccessLog

		# Indicates if thread should be terminated
		self.shutdownFlag = threading.Event()

		parentLog = logging.getLogger("checklist")
		self.log = parentLog.getChild("logParser")

	# Process DHCP messages and add to shared queue
	def processDhcp(self, line):
		dhcp = re.findall(LogParser.DHCP_REGEX, line)
		ip   = re.findall(LogParser.IP_REGEX, line)
		mac  = re.findall(LogParser.MAC_REGEX, line)

		if not dhcp or not mac:
			return

		errorFlag = False
		msg = ''
		if dhcp[0] in ['DHCPDECLINE', 'DHCPNAK']:
			errorFlag = True
			msg = line

		# DHCPDISCOVER message does nt have IP address
		if not ip:
			msg = mac[0]
		else:
			ip = ip[0]

		sm = StateMessage(ip, State[dhcp[0]], \
			errorFlag, time.time(), msg)
		self.localQ.put(sm)

	# Process TFTP messages and add to shared queue
	def processTftp(self, line):
		lineArr = line.split()
		ip = re.findall(LogParser.IP_REGEX, line)
		pxeFile = lineArr[-1]

		if not ip or \
			'filename' not in line or \
			pxeFile == 'pxelinux.0':
			return
		
		self.log.debug(line)
		sm = StateMessage(ip[0], State.TFTP_RRQ, False, time.time(), pxeFile)
		self.localQ.put(sm)

	# Parse Apache ssl_access_log and add relevant messages to shared queue
	def parseSSLAccessLog(self, line):
		lineArr  = shlex.split(line)
		status   = lineArr[-2]
		ip       = lineArr[0]
		errFlag = False
		msg = ''
		
		if status != LogParser.HTTP_SUCCESS:
			errFlag = True
			msg = line

		# Check if line in log file is relevant to backend install
		for key, val in LogParser.SSL_ACCESS_LOG_MAP.items():
			if key in line:
				sm = StateMessage(ip, val, errFlag, \
					time.time(), msg)
				self.localQ.put(sm)
				return

	# Parse access_log and add relevant messages to shared Queue.
	def parseAccessLog(self, line):
		lineArr = shlex.split(line)
		status  = lineArr[-4]
		ip      = lineArr[0]
		errFlag = False
		msg = ''

		if status != LogParser.HTTP_SUCCESS:
			errFlag = True
			msg = line

		for key, val in LogParser.ACCESS_LOG_MAP.items():
			url = re.findall(LogParser.URL_REGEX, line)
			if url and url[0].split('/')[-1] == key:
				sm = StateMessage(ip, val, errFlag, \
					time.time(), msg)
				self.localQ.put(sm)
				return

	#
	# Invoke appropriate parse function based on daemon name
	# in /var/log/messages
	#
	def parseVarlog(self, line):
		if 'dhcpd' in line:
			self.processDhcp(line)
		elif 'tftpd' in line:
			self.processTftp(line)

	# Main method - Keep reading file for newline
	def run(self):
		self.localQ = queue.Queue()
		qAdder = GlobalQueueAdder(self.localQ, self.globalQ)
		qAdder.setDaemon(True)
		qAdder.start()

		try:
			with open(self.path, "r") as file:
				file.seek(0, 2)

				while not self.shutdownFlag.is_set():
					where = file.tell()
					line  = file.readline()

					if not line:
						time.sleep(1)
						file.seek(where)
					else:
						self.parseFunc(line)

				qAdder.shutdownFlag.set()
				file.close()
		except Exception as e:
			self.log.error(e, exc_info=True)

class GlobalQueueAdder(threading.Thread):
	"""
	Get StateMessage object from local Queue and
	add it to global Queue. This helps prevent Queue
	contention issues if we are doing multiple
	backend installation checks at the same time.
	"""
	def __init__(self, localQ, globalQ):
		super(self.__class__, self).__init__()
		self.globalQ = globalQ
		self.localQ  = localQ
		self.shutdownFlag = threading.Event()

	def run(self):
		while not self.shutdownFlag.is_set():
			sm = self.localQ.get()
			self.globalQ.put(sm)

class CheckTimeouts(threading.Thread):
	"""
	Fires a timeout message if the installation does nt
	progress to the next stage
	"""
	def __init__(self, ipBackendMap, queue, lock):
		super(self.__class__, self).__init__()
		self.queue = queue
		self.ipBackendMap = ipBackendMap
		self.shutdownFlag = threading.Event()
		self.lock = lock
		parentLog = logging.getLogger("checklist")
		self.log = parentLog.getChild("CheckTimeout")

	def run(self):
		import redis
		self.r = None

		try:
			self.r = redis.StrictRedis(host='localhost')
		except:
			self.log.error(self, 'cannot connect to redis')
			self.shutdownFlag.set()

		while not self.shutdownFlag.is_set():
			#
			# Make a deepcopy of the internal state so this
			# thread is not holding the lock for too long.
			#
			with self.lock:
				l = list(self.ipBackendMap.values())
				backendList = copy.deepcopy(l)

			for b in backendList:
				ip = b.ipList[0]
				currState = b.lastSuccessfulState()

				if not currState or currState.isError or \
					not currState.state or \
					currState.state == State.Install_Wait or \
					currState.state == State.Installation_Stalled:
					continue

				redisKey = ip + '-' + currState.state.name

				#
				# If current State is not in redis then fire a timeout
				# message since install has not progressed to the next
				# state.
				#
				if self.r and self.r.get(redisKey):
					continue

				os = b.os
				osver = b.osversion
				nextState = StateSequence.nextExpectedState(currState.state, os, osver)

				if nextState and b.stateArr:
					msg = '%s Installation Stage Timeout' % nextState.name
					sm = StateMessage(ip, nextState, True, time.time(), msg)
					self.log.debug(sm)
					self.queue.put(sm)

class BackendExec(threading.Thread):
	"""
	Runs scripts / tests on a Backend via SSH and appends
	State messages to the queue about the installation
	progress.
	"""

	SSH_PORT    = 2200
	MAX_RETRIES = 50

	def __init__(self, ip, queue, scriptPath, ignoreError=True):
		super(self.__class__, self).__init__()
		self.ip = ip
		self.queue = queue
		self.ignoreError = ignoreError
		self.scriptPath = scriptPath
		parentLog = logging.getLogger("checklist")
		self.log = parentLog.getChild("BackendExec-%s" % ip)

		# Flag that checks if termination is needed
		self.shutdownFlag = threading.Event()

	def connect(self, client):
		num_tries = 0

		# Retry connecting to backend till it succeeds
		while num_tries <= BackendExec.MAX_RETRIES and \
			not self.shutdownFlag.is_set():
			try:
				num_tries = num_tries + 1
				client.connect(self.ip, port=BackendExec.SSH_PORT)
				return True
			except (paramiko.BadHostKeyException, paramiko.AuthenticationException,
				paramiko.SSHException, socket.error) as e:
				time.sleep(2)
				pass
		return False

	def run(self):
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self.log.debug('Initialized Backend Exec...')

		if not self.connect(client):
			client.close()

			if not self.shutdownFlag.is_set() and self.ignoreError:
				msg = 'Error - Unable to connect to %s via port %d' % \
					(self.ip, BackendExec.SSH_PORT)
				self.log.warn(msg)
				sm = StateMessage(self.ip, State.SSH_Open, True, \
					time.time(), msg)
				self.queue.put(sm)
			return

		msg = 'Connected to backend %s via port 2200' % self.ip
		self.log.debug(msg)
		sm = StateMessage(self.ip, State.SSH_Open, False, \
			time.time(), msg)
		self.queue.put(sm)

		# Run tests if Backend test script is provided
		if self.scriptPath:
			sftp = client.open_sftp()
			sftp.put(self.scriptPath, '/tmp/BackendTest.py')
			sftp.close()

			stdin, stdout, stderr = client.exec_command(
				'export LD_LIBRARY_PATH=/opt/stack/lib;' 	\
				'unset PYTHONPATH;' 				\
				'/opt/stack/bin/python3 /tmp/BackendTest.py')

			for line in stderr:
				self.log.error(line.strip())

		client.close()

class MQProcessor(stack.mq.processors.ProcessorBase):
	"""
	Listens for messages about Backend installation and
	appends State Messages to message queue
	"""

	def isActive(self):
		return True

	def channel(self):
		return 'health'

	def __init__(self, context, sock, gQueue):
		stack.mq.processors.ProcessorBase.__init__(self, context, sock)
		self.globalQ = gQueue

		parentLog = logging.getLogger("checklist")
		self.log = parentLog.getChild("mqprocessor")

		self.localQ = queue.Queue()
		qAdder = GlobalQueueAdder(self.localQ, self.globalQ)
		qAdder.setDaemon(True)
		qAdder.start()

	def process(self, message):
		msgTime = message.getTime()
		source  = message.getSource()
		payload = message.getPayload()
		self.log.debug('MQ Paylod = %s ' % str(payload))

		try:
			o = json.loads(payload)
			timeFormat = "%a %b %d %H:%M:%S %Y"
			d = datetime.strptime(msgTime, timeFormat)

			if "systest" in o:
				sm = StateMessage(source, State[o['systest']], \
					stack.bool.str2bool(o['flag']), 	\
					time.mktime(d.timetuple()), o['msg'])
				self.localQ.put(sm)
			elif "ssh" in o and source:
				errFlag = True
				if o['ssh'] == 'up' and o['state'] == 'online':
					errFlag = False

				sm = StateMessage(source, State.Reboot_Okay,
					errFlag, time.mktime(d.timetuple()))
				self.localQ.put(sm)
		except Exception as e:
			self.log.debug('Error %s parsing string - %s' % (str(e), payload))
