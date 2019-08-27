#!/opt/stack/bin/python3

import os

try:
	directory = os.environ['DOCUMENT_ROOT'] + os.environ['REQUEST_URI']
except:
	directory = '.'
	pass

out = ''

out += '<html>'
out += '<body>'
out += '<table>'

listing = os.listdir(directory)
listing.sort(key=str.lower)
for filename in listing:
	if 'index.cgi' not in filename:
		out += '<tr><td>\n'

		if os.path.isdir(os.path.join(directory, filename)):
			out += '<a href="%s/">%s/</a>\n' % (filename, filename)
		else:
			out += '<a href="%s">%s</a>\n' % (filename, filename)

		out += '</td></tr>'
		out += '\n'

out += '</table>'
out += '</body>'
out += '</html>'

print('Content-type: text/html')
print('Content-length: %d' % (len(out)))
print('')
print(out)
