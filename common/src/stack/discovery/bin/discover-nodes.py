#! /opt/stack/bin/python3

# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import argparse
from collections import OrderedDict
import json
import snack
from stack.mq import Subscriber
import subprocess
import zmq


class TUI(Subscriber):
	def __init__(self):
		super().__init__(zmq.Context())

		self._screen = snack.SnackScreen()
		self._screen.pushHelpLine(" ")

		self._callback_data = OrderedDict()

		self.subscribe("discovery")

	def error(self, message):
		form = snack.GridForm(self._screen, "Error", 1, 3)
		
		form.add(snack.TextboxReflowed(40, message), 0, 0)
		form.add(snack.Textbox(0, 2, ""), 0, 1)
		form.add(snack.Button("Quit"), 0, 2)

		form.runOnce()

	def start(self):
		# Create our discovery list
		form = snack.GridForm(self._screen, "Discovered Hosts", 1, 3)
		self._textbox = snack.Textbox(60, 10, "", scroll=1)
		label = snack.Label("MAC Address         Hostname               Kickstarted")

		form.add(label, 0, 0, anchorLeft=True, padding=(1, 0, 0, 0))
		form.add(self._textbox, 0, 1, padding=(1, 0, 0, 2))
		form.add(snack.Button("Quit"), 0, 2)

		# Call start on the base class to start the thread
		self.daemon = True
		super().start()

		# Launch the form and wait for the quit button to be pressed
		form.runOnce()
	
	def finish(self):
		self.unsubscribe("discovery")
		self._screen.finish()
	
	def callback(self, message):
		if message.message.get('type') == "add":
			ip_address = message.message.get('ip_address', "Unknown")
			mac_address = message.message.get('mac_address', "Unknown")
			hostname = message.message.get('hostname', "Unknown")

			self._callback_data[ip_address] = [mac_address, hostname, ""]
		elif message.message.get('type') == "kickstart":
			ip_address = message.message.get('ip_address', "Unknown")
			status_code = message.message.get('status_code')

			# In case we see a kickstart of a node already in the db
			if ip_address not in self._callback_data:
				self._callback_data[ip_address] = ["Unknown", "Unknown", ""]
			
			if status_code == 200:
				self._callback_data[ip_address][2] = "Success"
			else:
				self._callback_data[ip_address][2] = f"Error: {status_code}"
		
		self._textbox.setText('\n'.join([
			"{0}   {1:20}   {2}".format(*data) for data in self._callback_data.values()
		]))

		self._screen.refresh()


# Parse our commandline arguments
parser = argparse.ArgumentParser()

arguments = (
	("--appliance", "appliance used to configure nodes", "store"),
	("--basename", "base name for the nodes", "store"),
	("--rack", "rack number to use", "store"),
	("--rank", "rank number to start from", "store"),
	("--box", "box used to configure nodes", "store"),
	("--installaction", "install action used to configure nodes", "store"),
	("--no-install", "discover hosts but don't install OS", "store_true"),
	("--debug", "enable extra debugging info in the log file", "store_true")
)

for argument in arguments:
	parser.add_argument(argument[0], help=argument[1], action=argument[2])

args = parser.parse_args()

# Construct our stack enable discovery command
command = ["/opt/stack/bin/stack", "enable", "discovery"]

if args.basename:
	command.append(f"basename={args.basename}")

if args.appliance:
	command.append(f"appliance={args.appliance}")

if args.rack:
	command.append(f"rack={args.rack}")

if args.rank:
	command.append(f"rank={args.rank}")

if args.box:
	command.append(f"box={args.box}")

if args.installaction:
	command.append(f"installaction={args.installaction}")

if args.no_install:
	command.append("install=False")

if args.debug:
	command.append("debug=True")

# Stop discovery it it happens to be running, so we can restart
# it with our commandline arguments
subprocess.run(
	["/opt/stack/bin/stack", "disable", "discovery"],
	stdout=subprocess.PIPE,
	stderr=subprocess.PIPE,
	encoding="utf-8"
)

# Make sure node discovery is enabled
result = subprocess.run(
	command,
	stdout=subprocess.PIPE,
	stderr=subprocess.PIPE,
	encoding="utf-8"
)

# Set up our TUI
tui = TUI()

if result.returncode == 0:
	# Daemon should be up so show discovery
	tui.start()
else:
	# There was an error running the enable discovery command, show it to the user
	error_message = result.stderr.strip()
	if error_message.startswith("error - "):
		error_message = error_message[8:]
	
	tui.error(error_message)

# We are done
subprocess.run(
	["/opt/stack/bin/stack", "disable", "discovery"],
	stdout=subprocess.PIPE,
	stderr=subprocess.PIPE,
	encoding="utf-8"
)

tui.finish()
