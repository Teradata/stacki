#!/opt/stack/bin/python3
import argparse
import asyncio
from collections import defaultdict
import sys
import time


STATUSES = defaultdict(str)

async def monitor_install(backend):
	with open("/var/log/checklist.log", 'r') as log:
		# First step is to detect that the backend actually starts to
		# boot, by checking for the first entry for it to show up in the
		# checklist.log file. It gets 5 minutes to make that happen.
		start = time.time()

		while time.time() - start < 300:
			line = log.readline()
			if line:
				if backend in line:
					# Our backend has started booting
					break
			else:
				await asyncio.sleep(10)
		else:
			# Backend didn't boot within 5 minutes
			raise asyncio.TimeoutError

		# Go to the beginning of our checklist log file...
		log.seek(0)

		# ...and start parsing the latest status and look for hard failures
		while True:
			# Run through the latest log lines, looking for a fresh status
			for line in log:
				if f"Installation Status Messages for {backend}" in line:
					STATUSES[backend] = line
				elif backend in line:
					STATUSES[backend] += line

			# If fetching the profile XML returns a 500 error several times and
			# never a success, then it probably is a node XML error
			failures = 0
			for line in STATUSES[backend].splitlines():
				if "State.Profile_XML_Sent" in line:
					if "Success = True" in line:
						break
					else:
						failures += 1
			else:
				if failures > 5:
					raise asyncio.TimeoutError

			# If the installer stalled it is probably a missing package
			if "State.Installation_Stalled" in STATUSES[backend]:
				raise asyncio.TimeoutError

			# If we got to Reboot_Okay, this backend is done
			if "State.Reboot_Okay" in STATUSES[backend]:
				break

			# Not done yet, take a nap
			await asyncio.sleep(10)

async def main(timeout):
	# Create our monitoring tasks...
	tasks = asyncio.gather(
		monitor_install("192.168.0.1"),
		monitor_install("192.168.0.3"),
		return_exceptions=True
	)

	# ...and run them with a timeout
	try:
		results = await asyncio.wait_for(tasks, timeout=timeout)
	except asyncio.TimeoutError:
		# We ran out of time, make sure the tasks are cancelled
		try:
			results = await tasks
		except asyncio.CancelledError:
			return False
	finally:
		# Pause 10 seconds before output, so we don't corrupt the
		# vagrant output for the backends
		await asyncio.sleep(10)

		print()
		print("*** Last status for backend-0-0 ***")
		print(STATUSES["192.168.0.1"])
		print()

		print("*** Last status for backend-0-1 ***")
		print(STATUSES["192.168.0.3"])
		print()

	# Return if our tasks finished successfully or not
	return not any(isinstance(result, Exception) for result in results)

if __name__ == "__main__":
	# Parse some command line args
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"--timeout", type=int, default=60,
		help="timeout in minutes for the backends to install)"
	)
	args = parser.parse_args()

	# Run our async tasks
	success = asyncio.run(main(args.timeout*60))
	if not success:
		sys.exit("Error: one or more backends failed to install")
