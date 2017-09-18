#!/opt/stack/bin/python3

from flask import Flask, request, jsonify, send_from_directory, abort, render_template, redirect
from urllib.request import unquote
from random import shuffle
import os
import requests
import hashlib
import subprocess
import click
import signal

app = Flask(__name__)

tracker_settings = {
	'TRACKER' : '',
	'PORT' : 3825,
}

client_settings = {
	'TRACKER' : '',
	'PORT' : 80,
	'LOCAL_SAVE_LOCATION' : '',
	'ENVIRONMENT' : 'regular',
	'SAVE_FILES' : True
}

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

def hashit(filename):
	hashcode = hashlib.md5()
	hashcode.update(filename.encode('utf-8'))
	return hashcode.hexdigest()

def save_file(content, location, filename):
	subprocess.call(['mkdir', '-p', location])
	with open(location + filename, 'wb') as f:
		f.write(content)

def file_exists(local_file):
	return os.path.isfile(local_file)

def tracker():
	return "%s:%s" % (tracker_settings['TRACKER'], tracker_settings['PORT'])

def lookup_file(hashcode):
	try:
		res = requests.get('http://%s/avalanche/lookup/%s' % (tracker(), hashcode))
	except:
		raise
	return res

def get_file(peer, remote_file):
	try:
		res = requests.get('http://%s%s' % (peer, remote_file), timeout=1)
	except:
		raise

	return res

def register_file(port, hashcode):
	try:
		res = requests.post('http://%s/avalanche/register/%s/%s' % (
									tracker(), 
									port,
									hashcode)
									)
	except:
		raise

def unregister_file(hashcode, params):
	try:
		res = requests.delete('http://%s/avalanche/unregister/hashcode/%s' % (
									tracker(),
									hashcode),
									params=params
									)
	except:
		raise

def stream_it(response, content):
	response.write(content)

@app.route('/install/<path:path>/<filename>')
def get_file_locally(path, filename):
	save_location = client_settings['LOCAL_SAVE_LOCATION']
	file_location = '%s/install/%s' % (save_location, path)
	local_file = '%s/%s' % (file_location, filename)
	remote_file = '/install/%s/%s' % (path, filename)
	im_the_requester = request.remote_addr == "127.0.0.1"
	environment = client_settings['ENVIRONMENT']

	if not client_settings['SAVE_FILES']:
		return redirect('http://%s%s' % (tracker_settings['TRACKER'], remote_file))

	# check if file is local
	if client_settings['SAVE_FILES'] and im_the_requester and not file_exists(local_file):
		
		hashcode = hashit(remote_file)
		port = client_settings['PORT'] 
		params = {'port': port, 'hashcode': hashcode}
		res = lookup_file(hashcode)
		payload = res.json()
		successful = res.status_code == 200 and payload['success']

		if successful and payload['peers']:
			for peer in payload['peers']:
				app.logger.debug("requesting file: %s from peer: %s", (filename, peer))
				try:
					peer_res = get_file(peer, remote_file)
					if peer_res.status_code == 200:
						app.logger.debug("  %s from %s was successful", (filename, peer))
						save_file(peer_res.content, '%s/' % (file_location), filename)
						if environment == 'regular':
							register_file(port, hashcode)
							break
					else:
						app.logger.debug("  %s from %s was unsuccessful", (filename, peer))
						unregister_params = params.copy()
						unregister_params["peer"] = peer.split(":")[0]
						unregister_file(hashcode, unregister_params);
				except Exception as e:
					app.logger.debug("  %s from %s was unsuccessful", (filename, peer))
					app.logger.debug("    %s", e)
					unregister_params = params.copy()
					unregister_params["peer"] = peer.split(":")[0]
					unregister_file(hashcode, unregister_params);

	if not file_exists(local_file):
		app.logger.debug("requesting %s from frontend", (filename))
		try:
			tracker_res = requests.get('http://%s%s' % (tracker_settings['TRACKER'], remote_file))
			if tracker_res.status_code == 200:
				save_file(tracker_res.content, '%s/' % (file_location), filename)
				if client_settings['SAVE_FILES']:
					register_file(port, hashcode)
		except Exception as e:
			app.logger.debug("error requesting from frontend")
			app.logger.debug("%s", (e))

	if file_exists(local_file):
		app.logger.debug("%s is saved locally", (filename))
		return send_from_directory(unquote(file_location), unquote(filename))
	else:
		app.logger.debug("%s 404", (filename))
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
	peerdone_res = requests.delete('http://%s/avalanche/peerdone' % tracker())
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
	import logging
	#signal.signal(signal.SIGPIPE, signal.SIG_DFL)
	logging.basicConfig(filename='/var/log/ludicrous-client-debug.log',level=logging.DEBUG)
	client_settings['ENVIRONMENT']	= environment
	client_settings['SAVE_FILES']	= False if nosavefile else True
	client_settings['PORT']	= port
	with open(trackerfile) as f:
		line = f.readline()
		t = line.split(' ')[-1].strip()
		tracker_settings['TRACKER'] = t.split(':')[0].strip()
		tracker_settings['PORT'] = t.split(':')[-1].strip()

	#peerdone()

	if environment == 'initrd':
		pid = os.fork()
		if pid == 0:
			os.setsid()

			pid = os.fork()

			if pid != 0:
				os._exit(0)

			try:
				app.run(host='0.0.0.0', port=client_settings['PORT'], debug=False)
			except:
				pass
		else:
			os._exit(0)
	else:
		app.run(host='0.0.0.0', port=client_settings['PORT'], debug=False)

if __name__ == "__main__":
	main()
