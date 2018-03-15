#!/opt/stack/bin/python3

from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
from urllib.request import unquote
import os
import requests
import hashlib
import subprocess
import click
import logging
from logging import FileHandler
from time import sleep


app = Flask(__name__)

tracker_settings = {
	'TRACKER' : '',
	'PORT' : 80,
}

client_settings = {
	'TRACKER' : '',
	'PORT' : 80,
	'LOCAL_SAVE_LOCATION' : '',
	'ENVIRONMENT' : 'regular',
	'SAVE_FILES' : True
}

timed_out_hosts = []


@app.errorhandler(404)
def four_o_four(error=None):
        error_message = error if type(error) is str else "File not found."
        message = {
                'status': 404,
                'message': error_message
        }

        resp = jsonify(message)
        resp.status_code = 404

        return resp

# Returns an md5 hash of a filename
def hashit(filename):
	hashcode = hashlib.md5()
	hashcode.update(filename.encode('utf-8'))
	return hashcode.hexdigest()

# Save the file locally
def save_file(content, location, filename):
	try:
		subprocess.call(['mkdir', '-p', location])
		with open(location + filename, 'wb') as f:
			f.write(content)
	except:
		app.logger.info("save_file: Error saving file")
		raise

# Check if the file exists locally
def file_exists(local_file):
	return os.path.isfile(local_file)

# Returns the tracking server's ip and port as a string to be used
# in a request
def tracker():
	return "%s:%s" % (tracker_settings['TRACKER'], tracker_settings['PORT'])

# Lookup a file to see if any hosts have it
# Input is the md5 of the filename
# returns a list of hosts
def lookup_file(hashcode):
	try:
		# timeout=(connect timeout, read timeout).
		res = requests.get('http://%s/ludicrous/lookup/%s' % (tracker(), hashcode), timeout=(0.1, 5))
		return res
	except:
		raise

# Get a file from a host
def get_file(peer, remote_file):
	_counter = 0
	while _counter < 3:
		try:
			# timeout=(connect timeout, read timeout).
			res = requests.get('http://%s%s' % (peer, remote_file), timeout=(0.1, 5))
			return res
		except requests.ConnectTimeout:
			app.logger.debug('get_file: Connect Timeout. Retrying.')
		except requests.ConnectionError:
			app.logger.debug('get_file: Connection Error. Retrying.')
		except:
			app.logger.info("get_file: Error getting file from %s." % peer)

		_counter += 1


# Register a file for a host on the frontend
def register_file(port, hashcode):
	_counter = 0
	while _counter < 3:
		try:
			res = requests.post('http://%s/ludicrous/register/%s/%s' % (
									tracker(),
									port,
									hashcode)
									, timeout=(0.1, 5))
			break
		except requests.ConnectTimeout:
			app.logger.debug('register_file: Connect Timeout. Retrying.')
		except requests.ConnectionError:
			app.logger.debug('register_file: Connection Error. Retrying.')
		except:
			app.logger.info("register_file: Error registering file.")

		_counter += 1

# Unregister a single file from a host on the frontend
def unregister_file(hashcode, params):
	_counter = 0
	while _counter < 3:
		try:
			res = requests.delete('http://%s/ludicrous/unregister/hashcode/%s' % (
									tracker(),
									hashcode),
									params=params
									, timeout=(0.1, 5))
			break
		except requests.ConnectTimeout:
			app.logger.debug('unregister_file: Connect Timeout. Retrying.')
		except requests.ConnectionError:
			app.logger.debug('unregister_file: Connection Error. Retrying.')
		except:
			app.logger.info("unregister_file: Error unregistering file.")

		_counter += 1

# Unregister all hosts packages on frontend
def unregister_host(host):
	_counter = 0
	while _counter < 3:
		try:
			res = requests.delete('http://%s/ludicrous/unregister/host/%s' % (tracker(), host), timeout=(0.1, 5))
			break
		except requests.ConnectTimeout:
			app.logger.debug('unregister_host: Connect Timeout. Retrying.')
		except requests.ConnectionError:
			app.logger.debug('unregister_host: Connection Error. Retrying.')
		except:
			app.logger.info("unregister_host: Error unregistering host.")

		_counter += 1

@app.route('/install/<path:path>/<filename>')
def get_file_locally(path, filename):
	save_location = client_settings['LOCAL_SAVE_LOCATION']
	file_location = '%s/install/%s' % (save_location, path)
	local_file = '%s/%s' % (file_location, filename)
	remote_file = '/install/%s/%s' % (path, filename)
	hashcode = hashit(remote_file)
	im_the_requester = request.remote_addr == "127.0.0.1"
	environment = client_settings['ENVIRONMENT']
	port = client_settings['PORT']

	if not client_settings['SAVE_FILES']:
		return redirect('http://%s%s' % (tracker_settings['TRACKER'], remote_file))

	# check if file is local
	if client_settings['SAVE_FILES'] and im_the_requester and not file_exists(local_file):

		params = {'port': port, 'hashcode': hashcode}

		# Check if there are any hosts that have the file
		try:
			res = lookup_file(hashcode)
			payload = res.json()
			successful = res.status_code == 200 and payload['success']
		except:
			successful = False

		if successful and payload['peers']:
			peers = set(payload['peers'])
			for peer in peers.difference(timed_out_hosts):
				peer_ip = peer.split(":")[0]
				app.logger.info("requesting file: %s from peer: %s", filename, peer)
				try:
					peer_res = get_file(peer, remote_file)
					if peer_res.status_code == 200:
						save_file(peer_res.content, '%s/' % (file_location), filename)
						app.logger.info("  %s from %s was successful", filename, peer)
						register_file(port, hashcode)
						break
					else:
						app.logger.info("  %s from %s was unsuccessful", filename, peer)
						unregister_params = params.copy()
						unregister_params["peer"] = peer.split(":")[0]
						unregister_file(hashcode, unregister_params)

				except:
					app.logger.info("  %s from %s was unsuccessful", filename, peer)
					unregister_params = params.copy()
					unregister_params["peer"] = peer.split(":")[0]
					unregister_file(hashcode, unregister_params)

	if not file_exists(local_file):
		# Keep trying to get file from frontend if there is a
		# connection error or a timeout.
		while True:
			app.logger.info("requesting %s from frontend", filename)
			try:
				# timeout=(connect timeout, read timeout).
				tracker_res = requests.get('http://%s%s' % (tracker_settings['TRACKER'], remote_file), timeout=(0.1, 5))
				if tracker_res.status_code == 200:
					save_file(tracker_res.content, '%s/' % (file_location), filename)
					if client_settings['SAVE_FILES']:
						register_file(port, hashcode)
				break
			except requests.ConnectTimeout:
				app.logger.debug('Frontend Request: Connect Timeout. Retrying.')
				sleep(1)
			except requests.ConnectionError:
				app.logger.debug('Frontend Request: Connection Error. Retrying.')
				sleep(1)
			except:
				app.logger.info("Frontend Request: Error requesting %s from frontend" % filename)
				sleep(1)

	if file_exists(local_file):
		app.logger.info("%s is saved locally", (filename))
		return send_from_directory(unquote(file_location), unquote(filename))
	else:
		app.logger.info("%s 404", (filename))
		return redirect('http://%s%s' % (tracker_settings['TRACKER'], remote_file), code=307)


# catch all for returning static files
# if the request is a directory, the the request will be redirected
@app.route('/<path:path>/<filename>')
def get_file_route(path, filename):
	path = path.replace('//', '/')
	save_location = client_settings['LOCAL_SAVE_LOCATION']
	file_location = '%s/%s' % (save_location, path)
	response_file = '%s/%s' % (file_location, filename)
	if os.path.isdir(response_file):
		return redirect('%s/' % response_file, 301)
	else:
		return send_from_directory(unquote(file_location), unquote(filename))


# return a directory listing
@app.route('/<path:path>/<filename>/')
def get_repodata(path, filename):
	path = path.replace('//', '/')
	save_location = client_settings['LOCAL_SAVE_LOCATION']
	file_location = '%s/%s' % (save_location, path)
	response_file = '%s/%s' % (file_location, filename)
	items = [ f for f in os.listdir(response_file) if f[0] != '.' ]
	return render_template('directory.html', items=items)


@app.route('/running')
def running():
	return jsonify({"success": True})


@app.route('/peerdone')
def peerdone():
	peerdone_res = requests.delete('http://%s/ludicrous/peerdone' % tracker())
	return jsonify({"success": True})


@app.errorhandler(404)
def page_not_found(e):
	return "", 404


@click.command()
@click.option('--environment', default='regular')
@click.option('--trackerfile', default='/tmp/stack.conf')
@click.option('--nosavefile', is_flag=True)
@click.option('--port', default=80)
def main(environment, trackerfile, nosavefile, port):

	# Setup the logger
	logHandler = FileHandler('/var/log/ludicrous-client-debug.log')
	formatter = logging.Formatter("%(asctime)s: %(message)s", "%Y-%m-%d %H:%M:%S")
	logHandler.setFormatter(formatter)
	logHandler.setLevel(logging.DEBUG)
	app.logger.setLevel(logging.DEBUG)
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.DEBUG)
	app.logger.addHandler(logHandler)

	client_settings['ENVIRONMENT']	= environment
	client_settings['SAVE_FILES']	= False if nosavefile else True
	client_settings['PORT']	= port
	with open(trackerfile) as f:
		line = f.readline()
		t = line.split(' ')[-1].strip()
		tracker_settings['TRACKER'] = t.split(':')[0].strip()
		#tracker_settings['PORT'] = t.split(':')[-1].strip()

	#peerdone()

	if environment == 'initrd':
		pid = os.fork()
		if pid == 0:
			os.setsid()

			pid = os.fork()

			if pid != 0:
				os._exit(0)

			try:
				app.run(host='0.0.0.0', port=client_settings['PORT'])
			except:
				pass
		else:
			os._exit(0)
	else:
		app.run(host='0.0.0.0', port=client_settings['PORT'])


if __name__ == "__main__":
	main()
