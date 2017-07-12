from flask import Flask, request, jsonify, send_from_directory, abort
from urllib2 import unquote
from random import shuffle
import os
import requests
import hashlib
import subprocess
import click

app = Flask(__name__)

tracker_settings = {
	'TRACKER' 		: '',
	'PORT' 			: 80,
	'LOCAL_SAVE_LOCATION' 	: '/install',
	'ENVIRONMENT'		: 'regular'
}

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

def lookup_file(params):
	print 'http://%s/avalanche/lookup' % tracker_settings['TRACKER']
	try:
		res = requests.get('http://%s/avalanche/lookup' % (tracker_settings['TRACKER']), params=params)
	except:
		raise
	return res

def get_file(peer, remote_file):
	try:
		res = requests.get('http://%s%s' % (peer, remote_file))
	except:
		raise

	return res

def register_file(params):
	try:
		res = requests.get('http://%s/avalanche/register' % (tracker_settings['TRACKER']), params=params)
	except:
		raise

def unregister_file(params):
	try:
		res = requests.get('http://%s/avalanche/unregister' % (tracker_settings['TRACKER']), params=params)
	except:
		raise

def stream_it(response, content):
	response.write(content)

@app.route('/install/<path:path>/<filename>')
def get_file_locally(path, filename):
	file_location 		= '%s/%s' % (tracker_settings['LOCAL_SAVE_LOCATION'], path)
	local_file 		= '%s/%s' % (file_location, filename)
	remote_file 		= '/install/%s/%s' % (path, filename)
	im_the_requester	= request.remote_addr == "127.0.0.1"

	# check if file is local
	if im_the_requester and not file_exists(local_file):
		params = {'port': tracker_settings['PORT'], 'hashcode': hashit(remote_file)}
		res = lookup_file(params)
		payload = res.json()
		if tracker_settings['ENVIRONMENT'] == 'regular' and res.status_code == 200 and payload['success'] and payload['peers']:
			for peer in payload['peers']:
				try:
					peer_res = get_file(peer, remote_file)
					if peer_res.status_code == 200:
						save_file(peer_res.content, '%s/%s/' % (tracker_settings['LOCAL_SAVE_LOCATION'], path), filename)
						if tracker_settings['ENVIRONMENT'] == 'regular':
							register_file(params)
							break
					else:
						unregister_params = params.copy()
						unregister_params["peer"] = peer.split(":")[0]
						unregister_file(unregister_params);	
				except:
					unregister_params = params.copy()
					unregister_params["peer"] = peer.split(":")[0]
					unregister_file(unregister_params);	

			else:
			# if no peers worked, use the frontend
				tracker_res = requests.get('http://%s%s' % (tracker_settings['TRACKER'], remote_file))
				if tracker_res.status_code == 200:
					save_file(tracker_res.content, '%s/%s/' % (tracker_settings['LOCAL_SAVE_LOCATION'], path), filename)
					if tracker_settings['ENVIRONMENT'] == 'regular':
						register_file(params)
				
				
		else:
			tracker_res = requests.get('http://%s%s' % (tracker_settings['TRACKER'], remote_file))
			if tracker_res.status_code == 200:
				save_file(tracker_res.content, '%s/%s/' % (tracker_settings['LOCAL_SAVE_LOCATION'], path), filename)
				if tracker_settings['ENVIRONMENT'] == 'regular':
					register_file(params)

	if file_exists(local_file):
		return send_from_directory(unquote(file_location), unquote(filename))
	else:
		abort(404)

@app.route('/running')
def running():
	return "0"

@app.route('/done')
def peerdone():
	peerdone_res = requests.get('http://%s/avalanche/peerdone' % tracker_settings['TRACKER'])

@app.errorhandler(404)
def page_not_found(e):
	return "", 404

@click.command()
@click.option('--environment', default='regular')
@click.option('--trackerfile', default='/tmp/stack.conf')
def main(environment, trackerfile):
	tracker_settings['ENVIRONMENT']	= environment
	with open(trackerfile) as f:
		line = f.readline()
		tracker_settings['TRACKER'] = line.split(' ')[-1]
	
	peerdone()

	if environment == 'initrd':
		pid = os.fork()
		if pid == 0:
			os.setsid()
			
			pid = os.fork()
			
			if pid != 0:
				os._exit(0)

			try:
				app.run(host='0.0.0.0', port=tracker_settings['PORT'], debug=False)
			except:
				pass
		else:
			os._exit(0)
	else:
		app.run(host='0.0.0.0', port=tracker_settings['PORT'], debug=False)
		
if __name__ == "__main__":
	main()
