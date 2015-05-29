#!/opt/stack/bin/python

import os
import stack.installcgi
import stack.roll

#
# first download the minimum set of packages in order to build a kickstart
# file (i.e., all the roll-<rollname>-kickstart.*rpm files
#
icgi = stack.installcgi.InstallCGI()
g = stack.roll.Generator()

if os.path.exists('/tmp/rolls.xml'):
	g.parse('/tmp/rolls.xml')
elif os.path.exists('/tmp/pallets.xml'):
	g.parse('/tmp/pallets.xml')

rolls = g.rolls

for roll in rolls:
	icgi.getKickstartFiles(roll)

icgi.rebuildDistro(rolls)

#
# now generate the kickstart file with the command line
#
cmd = '/opt/stack/bin/stack list node xml frontend '
cmd += 'attrs="/tmp/site.attrs" 2> /dev/null'
cmd += '| /opt/stack/bin/stack list host profile '
cmd += '| /opt/stack/bin/stack list host installfile '
cmd += 'section=kickstart > '
cmd += '/tmp/ks.cfg 2> /tmp/ks.cfg.debug'

os.system(cmd)

#
# make a symbolic link so lighttpd can find this new 'distribution'.
# this isn't a full-blown distribution, just one with the node XML files in
# it as well as some repodata files. the symbolic link will give anaconda
# access to the repodata files which fakes out the installer just long enough
# for us to drop in the real repodata files
#
cmd = 'rm -f /install ; ln -s /export/stack /install'
os.system(cmd)

