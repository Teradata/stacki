import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
import multiprocessing
import signal
import time

from django.core.servers import basehttp
from django.core.wsgi import get_wsgi_application
import pytest


@pytest.fixture
def run_django_server(exclusive_lock):
	# Run a Django server in a process
	def runner():
		try:
			os.environ['DJANGO_SETTINGS_MODULE'] = 'stack.restapi.settings'
			basehttp.run('127.0.0.1', 8000, get_wsgi_application())
		except KeyboardInterrupt:
			# The signal to exit
			pass

	process = multiprocessing.Process(target=runner)
	process.daemon = True
	process.start()

	# Give the server a few seconds to get ready
	time.sleep(2)

	yield

	# Tell the server it is time to clean up
	os.kill(process.pid, signal.SIGINT)
	process.join()

@pytest.fixture
def run_file_server(exclusive_lock, test_file):
	# Run an HTTP server in a process
	def runner():
		try:
			# Change to our integration files directory
			os.chdir(test_file(''))

			# Serve them up
			with HTTPServer(
				('127.0.0.1', 8000),
				SimpleHTTPRequestHandler
			) as httpd:
				httpd.serve_forever()
		except KeyboardInterrupt:
			# The signal to exit
			pass

	process = multiprocessing.Process(target=runner)
	process.daemon = True
	process.start()

	# Give us a second to get going
	time.sleep(1)

	yield

	# Tell the server it is time to clean up
	os.kill(process.pid, signal.SIGINT)
	process.join()

@pytest.fixture
def run_pallet_isos_server(exclusive_lock, create_pallet_isos):
	# Run an HTTP server in a process
	def runner():
		try:
			# Change to our pallet isos directory
			os.chdir(create_pallet_isos)

			# Serve them up
			with HTTPServer(
				('127.0.0.1', 8000),
				SimpleHTTPRequestHandler
			) as httpd:
				httpd.serve_forever()
		except KeyboardInterrupt:
			# The signal to exit
			pass

	process = multiprocessing.Process(target=runner)
	process.daemon = True
	process.start()

	# Give us a second to get going
	time.sleep(1)

	yield

	# Tell the server it is time to clean up
	os.kill(process.pid, signal.SIGINT)
	process.join()
