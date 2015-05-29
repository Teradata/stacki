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

required_rolls = []
other_rolls = []
for file in os.listdir(dir):
	if file not in [ 'index.cgi' ]:
		if file in [ 'os', 'base', 'kernel', 'kernel', \
				'core', 'service-pack' ]:
			required_rolls.append(file)
		elif file[0:7] == 'RHEL':
			required_rolls.append(file)
		elif file[0:5] == 'CentOS':
			required_rolls.append(file)
		else:
			other_rolls.append(file)

required_rolls.sort()
other_rolls.sort()

for roll in required_rolls + other_rolls:
	out += '<tr><td>\n'

	if os.path.isdir(os.path.join(dir, roll)):
		out += '<a href="%s/">%s/</a>\n' % (roll, roll)
	else:
		out += '<a href="%s">%s</a>\n' % (roll, roll)

	out += '</td></tr>'
	out += '\n'

out += '</table>'
out += '</body>'
out += '</html>'

print 'Content-type: text/html'
print 'Content-length: %d' % (len(out))
print ''
print out
