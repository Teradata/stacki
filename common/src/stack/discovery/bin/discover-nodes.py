#! /opt/stack/bin/python3

# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import argparse
import snack
import subprocess

# Parse our commandline arguments
parser = argparse.ArgumentParser()

arguments = (
	("--appliance", "appliance used to configure nodes"),
	("--basename", "base name for the nodes"),
	("--rack", "rack number to use"),
	("--rank", "rank number to start from"),
	("--box", "box used to configure nodes"),
	("--installaction", "install action used to configure nodes")
)

for argument in arguments:
	parser.add_argument(argument[0], help=argument[1])

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
screen = snack.SnackScreen()
screen.pushHelpLine(" ")

if result.returncode == 0:
	# Create our display form
	form = snack.GridForm(screen, "Discovered Hosts", 1, 4)
	textbox = snack.Textbox(60, 10, "", scroll=1)
	
	form.add(snack.Textbox(60, 1, "MAC Address   Hostname   Kickstarted"), 0, 0)
	form.add(textbox, 0, 1)
	form.add(snack.Textbox(0, 2, ""), 0, 2)
	form.add(snack.Button("Quit"), 0, 3)
	
	form.runOnce()
else:
	# There was an error running the enable discovery command, show it to the user
	form = snack.GridForm(screen, "Error", 1, 3)

	error_message = result.stderr.strip()
	if error_message.startswith("error - "):
		error_message = error_message[8:]
	
	textbox = snack.TextboxReflowed(40, error_message)
	form.add(textbox, 0, 0)
	form.add(snack.Textbox(0, 2, ""), 0, 1)
	form.add(snack.Button("Quit"), 0, 2)
	
	form.runOnce()

# We are done
subprocess.run(
	["/opt/stack/bin/stack", "disable", "discovery"],
	stdout=subprocess.PIPE,
	stderr=subprocess.PIPE,
	encoding="utf-8"
)

screen.finish()
