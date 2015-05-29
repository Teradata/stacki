#!/opt/stack/bin/python

import os

try:
	dir = os.environ['DOCUMENT_ROOT'] + os.environ['REQUEST_URI']
except:
	dir = '.'
	pass

out = ''

out += '<html>'
out += '<body>'
out += '<table>'

listing = os.listdir(dir)
listing.sort(key=str.lower)
for file in listing:
	if file not in [ 'index.cgi' ]:
		out += '<tr><td>\n'

		if os.path.isdir(os.path.join(dir, file)):
			out += '<a href="%s/">%s/</a>\n' % (file, file)
		else:
			out += '<a href="%s">%s</a>\n' % (file, file)

		out += '</td></tr>'
		out += '\n'

out += '</table>'
out += '</body>'
out += '</html>'

print 'Content-type: text/html'
print 'Content-length: %d' % (len(out))
print ''
print out
