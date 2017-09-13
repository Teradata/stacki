#!/opt/stack/bin/python3

import os, sys
from urllib import urlopen
import json
import pickle

if __name__ == '__main__':
	url = sys.argv[1]
	url_cgi = url + '/pallets.cgi'
	response = urlopen(url_cgi)
	pallets = json.loads(response.read())
	for pallet in pallets:
		pallet['id'] = ''
		pallet['url'] = str(url)
	print pickle.dumps(pallets)
