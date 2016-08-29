#!/opt/stack/bin/python

import os
import shutil

# Create a pallets directory in RAMDISK
os.makedirs("/export/stack/pallets")
import stack.roll

# Read the rolls.xml file and get
# information about the pallets to install
g = stack.roll.Generator()
f = open('/tmp/rolls.xml','r')
g.parse(f)

# Download the graph and node XML files
# for all selected pallets
wget_cmd = "/usr/bin/wget -r -nH -A xml,pro --cut-dirs=2"
cwd = os.getcwd()
os.chdir("/export/stack/pallets")
for pallet in g.rolls:
	nodes_url = "%s/%s/%s/redhat/%s/nodes" % (pallet[4],pallet[0],pallet[1],pallet[3])
	os.system("%s %s" % (wget_cmd, nodes_url))
	graph_url = "%s/%s/%s/redhat/%s/graph" % (pallet[4],pallet[0],pallet[1],pallet[3])
	os.system("%s %s" % (wget_cmd, graph_url))

	#
	# convert any .pro files to .xml
	#
	graphdir = '/export/stack/pallets/%s/%s/redhat/%s/graph' \
		% (pallet[0], pallet[1], pallet[3])
	#
	# If graph directory does not exist, this could
	# indicate a foreign pallet. Ignore, and move on
	#
	if not os.path.exists(graphdir):
		continue
	for file in os.listdir(graphdir):
		base, ext = os.path.splitext(file)
		if ext == '.pro':
			profile = os.path.join(graphdir, file)
			xmlfile	= os.path.join(graphdir, '%s.xml' % base)
			shutil.copyfile(profile, xmlfile)

# RHEL 7 needs the repodata files too
wget_cmd = "/usr/bin/wget -r -nH -R TRANS.TBL --cut-dirs=2"
for pallet in g.rolls:
	repodata_url = "%s/%s/%s/redhat/%s/repodata" % (pallet[4],pallet[0],pallet[1],pallet[3])
	os.system("%s %s" % (wget_cmd, repodata_url))

os.chdir(cwd)

#
# now generate the kickstart file with the command line
#
cmd = '/opt/stack/bin/stack list node xml frontend '
cmd += 'attrs="/tmp/site.attrs" 2> /dev/null'
cmd += '| /opt/stack/bin/stack list host profile document=false'
cmd += '> /tmp/ks.cfg 2> /tmp/ks.cfg.debug'

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

