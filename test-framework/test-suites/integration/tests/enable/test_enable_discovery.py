import json
import os
import time

import pytest
from stack.mq import ports, Message
import zmq


class DiscoveryListener:
	def __init__(self):
		# Set up ZMQ to listen to the 'discovery' channel
		context = zmq.Context()

		self._socket = context.socket(zmq.SUB)
		self._socket.connect(f"tcp://localhost:{ports.subscribe}")
		self._socket.setsockopt_string(zmq.SUBSCRIBE, "discovery")

	def listen(self, count, timeout):
		messages = []

		for _ in range(timeout):
			try:
				# Read messages up to 'count'
				while len(messages) < count:
					channel, data = self._socket.recv_multipart(
						flags=zmq.NOBLOCK
					)

					message = Message(
						message=data.decode(),
						channel=channel.decode()
					)
					messages.append(message)
			except zmq.ZMQError:
				# No more messages, wait a second
				time.sleep(1)

		return messages


@pytest.mark.usefixtures("revert_discovery")
class TestEnableDiscovery:
	def test_daemon_not_running(self, host):
		"Test the discovery daemon is started when not running"

		# Confirm the daemon isn't running
		process_list = [
			process for process in host.process.filter(comm="stack")
			if "discovery" in process.args
		]
		assert len(process_list) == 0

		# Start the daemon
		result = host.run("stack enable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has started\n"

		# Confirm it is running now
		process_list = [
			process for process in host.process.filter(comm="stack")
			if "discovery" in process.args
		]
		assert len(process_list) == 1

		# Stop discovery to put the system back to the initial state
		result = host.run("stack disable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has stopped\n"

		# Confirm the log messages got written out
		log_file = host.file("/var/log/stack-discovery.log")
		assert log_file.exists

		lines = log_file.content_string.strip().split('\n')
		assert len(lines) == 2
		assert "INFO: discovery daemon started" in lines[0]
		assert "INFO: discovery daemon stopped" in lines[1]

	def test_daemon_already_running(self, host):
		"""
		Test the discovery daemon enable command works when the
		daemon is already running
		"""

		# Start the deamon
		result = host.run("stack enable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has started\n"

		# Confirm a single daemon is running
		process_list = [
			process for process in host.process.filter(comm="stack")
			if "discovery" in process.args
		]
		assert len(process_list) == 1
		pid = process_list[0].pid

		# Start the daemon again
		result = host.run("stack enable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has started\n"

		# Confirm it is still running and has the initial PID
		process_list = [
			process for process in host.process.filter(comm="stack")
			if "discovery" in process.args
		]
		assert len(process_list) == 1
		assert process_list[0].pid == pid

		# Stop discovery to put the system back to the initial state
		result = host.run("stack disable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has stopped\n"

		# Confirm the log messages got written out
		log_file = host.file("/var/log/stack-discovery.log")
		assert log_file.exists

		lines = log_file.content_string.strip().split('\n')
		assert len(lines) == 2
		assert "INFO: discovery daemon started" in lines[0]
		assert "INFO: discovery daemon stopped" in lines[1]

	def test_daemon_detecting_two_nodes(self, host):
		"""
		Test that the node discovery process works with two nodes,
		properly ignoring duplicate DHCP requests in the process.
		"""

		# Confirm only the frontend is in the database
		result = host.run("stack list host output-format=json")
		assert result.rc == 0

		host_data = json.loads(result.stdout)
		assert len(host_data) == 1
		assert host_data[0]['appliance'] == "frontend"

		# Start the deamon
		result = host.run("stack enable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has started\n"

		# Confirm a single daemon is running
		process_list = [
			process for process in host.process.filter(comm="stack")
			if "discovery" in process.args
		]
		assert len(process_list) == 1

		# Set up a listener to capture discovery messages
		listener = DiscoveryListener()

		# Simulate some DHCP requests
		with open("/var/log/messages", "a") as f:
			# The first node's initial DHCP request
			f.write("DHCPDISCOVER from 52:54:00:00:00:03 via eth1\n")

			# Simulate the first node sending a second DHCP request
			f.write("DHCPDISCOVER from 52:54:00:00:00:03 via eth1\n")

			# The second node's initial DHCP request
			f.write("DHCPDISCOVER from 52:54:00:00:00:04 via eth1\n")

			# Simulate the second node sending a second DHCP request
			f.write("DHCPDISCOVER from 52:54:00:00:00:04 via eth1\n")

			# A few more DHCP requests, because why not?
			f.write("DHCPDISCOVER from 52:54:00:00:00:03 via eth1\n")
			f.write("DHCPDISCOVER from 52:54:00:00:00:04 via eth1\n")

		# Listen for the add messages on the queue
		messages = listener.listen(2, 60)

		# Make sure we got 2 add messages and they are what we expect
		assert len(messages) == 2
		assert messages[0].getPayload() == {
			'type': "add",
			'interface': "eth1",
			'mac_address': "52:54:00:00:00:03",
			'ip_address': "192.168.0.1",
			'hostname': "backend-0-0"
		}
		assert messages[1].getPayload() == {
			'type': "add",
			'interface': "eth1",
			'mac_address': "52:54:00:00:00:04",
			'ip_address': "192.168.0.3",
			'hostname': "backend-0-1"
		}

		# Simulate some kickstarts
		if os.path.isfile("/var/log/httpd/ssl_access_log"):
			kickstart_log = "/var/log/httpd/ssl_access_log"
			os_type = "redhat"
		else:
			kickstart_log = "/var/log/apache2/ssl_access_log"
			os_type = "sles"

		with open(kickstart_log, "a") as f:
			for ip in ("192.168.0.1", "192.168.0.3"):
				f.write(
					'{} - - [01/Jan/2000:00:00:00 +0000] "GET '
					'/install/sbin/profile.cgi?os={}&arch=x86_64&np=1 '
					'HTTP/1.1" 200 12345\n'.format(ip, os_type)
				)

		# Listen for the kickstart messages on the queue
		messages = listener.listen(2, 60)

		# Make sure we got 2 kickstart messages and they are
		# what we expect
		assert len(messages) == 2
		assert messages[0].getPayload() == {
			'type': "kickstart",
			'ip_address': "192.168.0.1",
			'status_code': 200
		}
		assert messages[1].getPayload() == {
			'type': "kickstart",
			'ip_address': "192.168.0.3",
			'status_code': 200
		}

		# Stop discovery to put the system back to the initial state
		result = host.run("stack disable discovery")
		assert result.rc == 0
		assert result.stdout == "Discovery daemon has stopped\n"

		# Confirm the log messages got written out
		log_file = host.file("/var/log/stack-discovery.log")
		assert log_file.exists

		# Does the log file contain all the expected messages?
		lines = [
			line[20:]
			for line in log_file.content_string.strip().split('\n')
		]

		assert lines == [
			"INFO: discovery daemon started",
			"INFO: detected a dhcp request: 52:54:00:00:00:03 eth1",
			"INFO: found a new node: 52:54:00:00:00:03 eth1",
			"INFO: successfully added host backend-0-0",
			"INFO: detected a dhcp request: 52:54:00:00:00:03 eth1",
			"INFO: detected a dhcp request: 52:54:00:00:00:04 eth1",
			"INFO: found a new node: 52:54:00:00:00:04 eth1",
			"INFO: successfully added host backend-0-1",
			"INFO: detected a dhcp request: 52:54:00:00:00:04 eth1",
			"INFO: detected a dhcp request: 52:54:00:00:00:03 eth1",
			"INFO: detected a dhcp request: 52:54:00:00:00:04 eth1",
			"INFO: discovery daemon stopped"
		]

		# Check that the two backends were added correctly
		result = host.run("stack list host output-format=json")
		assert result.rc == 0

		host_data = json.loads(result.stdout)
		assert len(host_data) == 3
		assert host_data[0]['appliance'] == "frontend"

		assert host_data[1] == {
			"host": "backend-0-0",
			"rack": "0",
			"rank": "0",
			"appliance": "backend",
			"os": os_type,
			"box": "default",
			"environment": None,
			"osaction": "default",
			"installaction": "default",
			"comment": None
		}

		assert host_data[2] == {
			"host": "backend-0-1",
			"rack": "0",
			"rank": "1",
			"appliance": "backend",
			"os": os_type,
			"box": "default",
			"environment": None,
			"osaction": "default",
			"installaction": "default",
			"comment": None
		}
