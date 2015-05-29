#!/opt/stack/bin/python

import sys
import urllib2
import pickle
from HTMLParser import HTMLParser

#returns array of all instances of a substring from a string
def find_all(a_str, sub):
	start = 0
	while True:
		start = a_str.find(sub, start)
		if start == -1: return
		yield start
		start += len(sub)

#used by listctrl to search for duplicate of pallet
def search(L, n, v, i, u):
	return [item for item in L if item['name'] == n and item['version'] == v and \
		item["id"] == i and item['url'] == u]

class BossHTMLParser(HTMLParser):
	def __init__(self, url):
		HTMLParser.__init__(self)
		self.url = url
		self.pallets = []

	def handle_starttag(self, tag, attrs):
		if tag == 'a':
			for w in attrs:
				name = w[1]
				#check if value is a directory to proceed
				if name.find('/') > 0:
					#html for version directory
					response = urllib2.urlopen(self.url + name)
					html = response.read()

					#index of start and end tag for version value
					str1 = list(find_all(html, '<a href="'))
					str2 = list(find_all(html, '/">'))

					#extract name
					name = name[0: name.find('/')]

					if str1 and str2:

						#get all version links
						for i in range(len(str1)):
							n = str1[i]
							m = str2[i]

							ver = html[n+9: m]
							dup = search(self.pallets, name, ver, '', str(self.url))

							#do not add if duplicate
							if not dup:
								self.pallets.append({'name': name, 'version': ver, 'id':'', 'url': str(self.url)})


if __name__ == '__main__':
	url = sys.argv[1]
	response = urllib2.urlopen(url)
	html = response.read()
	parser = BossHTMLParser(url)
	parser.feed(html)
	print pickle.dumps(parser.pallets)
