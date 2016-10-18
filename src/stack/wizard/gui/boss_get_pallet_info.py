#!/opt/stack/bin/python

import os, sys
import urllib2
import json
import pickle

if __name__ == '__main__':
	url = sys.argv[1]
	url_cgi = url + '/pallets.cgi'
	try:
		response = urllib2.urlopen(url_cgi)
		pallets = json.loads(response.read())
		for pallet in pallets:
			pallet['id'] = ''
			pallet['url'] = str(url)
		print pickle.dumps(pallets)
	except:
		raise
		sys.exit(-1)
