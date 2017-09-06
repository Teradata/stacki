#!/opt/stack/bin/python3

from flask import Flask, request, jsonify, send_from_directory, abort, render_template, redirect
from werkzeug.routing import BaseConverter
from urllib.request import unquote
from random import shuffle
import stack.api
import click
import os

app = Flask(__name__)

packages = {}
peers = {}

MAX_PEERS = 3

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

@app.route('/avalanche/lookup/<hashcode>', methods=['GET'])
def lookup(hashcode):
	res = {}
	res['success'] = True
	ipaddr = request.remote_addr

	# check if hash exists
	if(hashcode not in packages):
		packages[hashcode] = []

	# check if peer exists and is in our database
	if(ipaddr not in peers):
		hosts = [host['value'] for host in stack.api.Call('list.host.attr', ["attr=hostaddr"])]
		if ipaddr not in hosts:
			return four_o_four("Host not managed by frontend")

	# return list of peers with the request hash
	res['peers'] = []
	shuffle(packages[hashcode])
	for peer in packages[hashcode]:
		peer_ready	= peers[peer]['ready']
		not_my_ip	= peer != ipaddr
		if not_my_ip and peer_ready:
			res['peers'].append("%s:%s" % (peer, peers[peer]['port']))
		
		# if array of peers is max_peers, break
		if len(res['peers']) == 10:
			break

	return jsonify(res)

@app.route('/avalanche/register/<port>/<hashcode>', methods=['POST'])
def register(port=80, hashcode=None):
	res = {}
	res['success'] = True
	ipaddr = request.remote_addr

	if not hashcode:
		return four_o_four("asdf")

	# check if hash exists
	if(hashcode not in packages):
		packages[hashcode] = []

	# check if peer exists and is in our database
	if(ipaddr not in peers):
		if ipaddr in [host['value'] for host in stack.api.Call('list.host.attr', ["attr=hostaddr"])]:
			peers[ipaddr] = {
				'ready': False,
				'port': port
				}
		else:
			return four_o_four()

	# register file
	packages[hashcode].append(ipaddr)

	# mark peer as ready
	peers[ipaddr]['ready'] = True

	return jsonify(res)

@app.route('/avalanche/unregister/hashcode/<hashcode>', methods=['DELETE'])
def unregister(hashcode):
	ipaddr = unquote(request.args['peer'])
	res = {}
	res['success'] = True

	app.logger.debug("unquoted ip addr: %s", ipaddr)
	if packages.has_key(ipaddr) and ipaddr in packages[hashcode]:
		packages[hashcode].remove(ipaddr)
		res['message'] = "'%s' was unregistered for hash: %s" % (ipaddr, hashcode)
	else:
		res['message'] = "'%s' was not registered for hash: %s" % (ipaddr, hashcode)


	return jsonify(res)

@app.route('/avalanche/peerdone', methods=['DELETE'])
def peerdone():
	ipaddr = request.remote_addr
	res = {}
	res['success'] = True

	for package in packages:
		if ipaddr in packages[package]:
			packages[package].remove(ipaddr)
	
	if ipaddr in peers:	
		del(peers[ipaddr])	

	return ""

@app.route('/avalanche/stop', methods=['GET'])
def stop_server():
	return "-1"

# route for RPMS
@app.route('/install/<path:path>/<filename>')
def get_file_local(path, filename):
	app.logger.debug("Requesting File: %s" % request.args )
	path = path.replace('//', '/')
	file_location = '/var/www/html/install/%s' % (path)
	response_file = '%s/%s' % (file_location, filename)
	if os.path.isdir(response_file):
		return redirect('%s/' % response_file, 301)
	else:
		return send_from_directory(unquote(file_location), unquote(filename))

# catch all for returning static files
# if the request is a directory, the the request will be redirected
@app.route('/<path:path>/<filename>')
def get_file_catchall(path, filename):
	path = path.replace('//', '/')
	file_location = '/%s' % (path)
	response_file = '%s/%s' % (file_location, filename)
	if os.path.isdir(response_file):
		return redirect('%s/' % response_file, 301)
	else:
		return send_from_directory(unquote(file_location), unquote(filename))


# return a directory listing
@app.route('/<path:path>/<filename>/')
def get_repodata(path, filename):
	path = path.replace('//', '/')
	file_location = '/%s' % (path)
	response_file = '%s/%s' % (file_location, filename)
	items = [ f for f in os.listdir(response_file) if f[0] != '.' ]
	return render_template('directory.html', items=items)

def main():
	import logging
	logging.basicConfig(filename='/var/log/ludicrous-server.log',level=logging.DEBUG)
	app.run(host='0.0.0.0', port=80, debug=True)

if __name__ == "__main__":
	main()
