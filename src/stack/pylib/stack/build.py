#! /opt/stack/bin/python
# 
# @SI_Copyright@
#                             www.stacki.com
#                                  v3.0
# 
#      Copyright (c) 2006 - 2015 StackIQ Inc. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	 "This product includes software developed by StackIQ" 
#  
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY STACKIQ AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL STACKIQ OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @SI_Copyright@
#
# @Copyright@
#  				Rocks(r)
#  		         www.rocksclusters.org
#  		         version 5.4 (Maverick)
#  
# Copyright (c) 2000 - 2010 The Regents of the University of California.
# All rights reserved.	
#  
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#  
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#  
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
#  
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
#  
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
#  
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# @Copyright@

from __future__ import print_function
import sys
import os
import shutil
import re
import tempfile
import string
import time
import popen2
import xml
import socket
import stack.dist
import stack.file
import stack.ks
import stack.util


class BuildError(Exception):
	pass


class Builder:
    
	def __init__(self):
        	self.verbose = 0
		self.debug   = 0

	def build(self):
		pass

	def setVerbose(self, level=1):
		self.verbose = level

	def setDebug(self, level=1):
		self.debug = level


class DistributionBuilder(Builder):

    def __init__(self, dist, links=1):
        Builder.__init__(self)
        self.dist		= dist
        self.useLinks		= links
        self.carts		= []
        self.compsPath		= None
	self.useRolls		= {}
	self.allRolls		= 1
	self.onlyRolls		= 0
	self.withSiteProfiles   = 0
	self.doMD5		= True
	self.doResolve		= False
	self.version	 = '1.0'

        # Build the Tree objects for the Mirror and Distribution
        # trees.  The actual files for the distibution may or may not
        # exist.  We no longer nuke pre-existing distibutions before
        # building a new one.  This will make mirroring simpler.

        for mirror in self.dist.getMirrors():
            if not mirror.isBuilt():
                mirror.build()

        if not self.dist.isBuilt():
            self.dist.build()


    def setResolveVersions(self, resolve):
	    self.doResolve = resolve

    def setCarts(self, list):
            if list:
                    self.carts = list
                    
    def setRolls(self, list, only=0):
	    if list:
		    for e in list:
			    self.useRolls[e[0]] = (e[1], e[2])
		    self.allRolls = 0
	    else:
		    self.useRolls = {}
		    self.allRolls = 1
	    self.onlyRolls = only



    def setVersion(self, ver):
    	self.version = ver

    def setSiteProfiles(self, bool):
	    self.withSiteProfiles = bool

    def setMD5(self, bool):
	    self.doMD5 = bool
	    
    def clean(self):
        # Nuke the previous distribution.  The cleaner() method will
        # preserve any build/ directory.
        print('Cleaning distribution')
        self.dist.getTree('release').apply(self.cleaner)


    def useRoll(self, key, ver, arch):
    	"Returns true if we should include this roll"

	if arch == self.dist.arch:
		if self.allRolls:
			return 1
		if self.useRolls.has_key(key):
			version, enabled = self.useRolls[key]
			if enabled and version == ver:
				return 1
	return 0


    def getRollLiveOSFiles(self):
	    files = []
	    for m in self.dist.getMirrors():
		    for key, value in m.getRolls().items():
			    for v, a in value:
				    if self.useRoll(key, v, a):
					    f = m.getRollLiveOSFiles(key, v, a)
					    if f:
						    files.extend(f)
						    print('\tusing files from %s' % (key))
						    for name in f:
							    print('\t\t%s' % name.getBaseName())
	    return files


    def getRollBaseFiles(self):
	    files = []
	    for m in self.dist.getMirrors():
		    for key, value in m.getRolls().items():
			    for v, a in value:
				    if self.useRoll(key, v, a):
					    f = m.getRollBaseFiles(key, v, a)
					    if f:
						    files.extend(f)
						    print('\tusing files from %s' % (key))
						    for name in f:
							    print('\t\t%s' % name.getBaseName())
	    return files


    def getRollRPMS(self):
	    rpms = []
	    for m in self.dist.getMirrors():
		    for key, value in m.getRolls().items():
			    for v, a in value:
				    if self.useRoll(key, v, a):
					    r = m.getRollRPMS(key, v, a)
					    if r:
						    print('\tfound %4d packages on pallet %s %s' % (len(r), key, v))
						    rpms.extend(r)
	    return rpms


    def getCartRPMS(self):
            rpms = []
            for cart in self.carts:
                    tree = stack.file.Tree(os.path.join('/export/stack/carts',
                                                                cart))
                    r = tree.getFiles('RPMS')
                    print('\tfound %4d packages on cart   %s' % (len(r), cart))
                    rpms.extend(r)

            # fix rpm permissions in the cart dirs (files get symlinked)
            
            for rpm in rpms:
                    rpm.chmod(0o644)
                    
            return rpms
    
    def buildRPMSList(self):

	    # Build and resolve the list of RPMS.  Then drop in all
	    # the other non-rpm directories from the Mirror's release.

	    rpms = self.getRollRPMS()
	    for mirror in self.dist.getMirrors():
		    rpms.extend(mirror.getRPMS())
	    if not self.onlyRolls:
		    rpms.extend(self.getCartRPMS())
	    	    rpms.extend(self.dist.getContribRPMS())
	    	    rpms.extend(self.dist.getLocalRPMS())
	    if not os.path.isdir(self.dist.getForceRPMSPath()):
		    os.makedirs(self.dist.getForceRPMSPath())
	    else:
		    rpms.extend(self.dist.getForceRPMS()) 
	    return rpms

    
    def buildBase(self):
        print('Resolving versions (base files)')
        self.dist.setBaseFiles(self.resolveVersions(self.getRollBaseFiles()))


    def buildRPMS(self):
        print('Gathering RPMs')
        self.dist.setRPMS(self.resolveVersions(self.buildRPMSList()))


    def buildLiveOS(self):
        print('Resolving versions (LiveOS)')
        self.dist.setLiveOS(self.resolveVersions(self.getRollLiveOSFiles()))


    def insertImage(self, image):
	print('Applying %s' % image)
	import stat
	
	try:
		self.applyRPM('stack-images', self.dist.getReleasePath())
	except:
		print("Couldn't find the package stack-images")
		print("\tIf you are building the OS roll, this is not a problem")
		return

	imagesdir = os.path.join(self.dist.getReleasePath(), 'images')
	if not os.path.exists(imagesdir):
		os.makedirs(imagesdir)

	imageold = os.path.join(self.dist.getReleasePath(),
		'opt', 'stack', 'images', image)
	imagenew = os.path.join(imagesdir, image)
	os.rename(imageold, imagenew)
	os.chmod(imagenew, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)

	#
	# clean up other image files from the stack-image RPM
	#
	rmdir = os.path.join(self.dist.getReleasePath(), 'opt')
	shutil.rmtree(rmdir, ignore_errors = 1)

	return


    def build(self):
		import stack

		self.clean()
		self.dist.syncMirror()
		self.buildBase()

		if stack.release == '7.x':
			self.buildLiveOS()

		self.buildRPMS()

		print('Creating files', end=' ')
		if self.useLinks:
			print('(symbolic links - fast)')
		else:
			print('(deep copy - slow)')
		self.dist.getReleaseTree().apply(self.builder)
		self.dist.getReleaseTree().apply(self.normalizer)

		print('Applying comps.xml')
		self.applyRPM('foundation-comps', self.dist.getReleasePath())

		if stack.release == '7.x':
			self.insertImage('upgrade.img')
			self.insertImage('updates.img')
		else:
			self.insertImage('install.img')
		
		self.buildKickstart()
		if self.doMD5:
			self.createrepo()
		self.buildProductImg()
	
		return


    def buildKickstart(self):
	print('Installing XML Kickstart profiles')

	build   = self.dist.getBuildPath()

	for rpm in self.dist.getRPMS():
		tok = rpm.getBaseName().split('-')
		if tok[0] != 'roll':
			continue
		try:
			k = tok.index('kickstart')
			rollname = '-'.join(tok[1:k])
		except ValueError:
			continue
			
		print('\tinstalling %s' % rpm.getBaseName())
		self.applyRPM(rpm.getBaseName(), build)

	# Copy local profiles into the distribution.
	if self.withSiteProfiles:
		print('\tinstalling site-profiles')
		tree = self.dist.getSiteProfilesTree()
		for dir in tree.getDirs():
			for file in tree.getFiles(dir):
				path = os.path.join(build, dir)
				if not os.path.isdir(path):
					os.makedirs(path)
				shutil.copy(file.getFullName(),
					os.path.join(path, file.getName()))
				# make sure apache can read site XML
				file.chmod(0o664)
                                
	# Copy cart profiles into the distribution.
        for cart in self.carts:
		print('\tinstalling %s cart' % cart)
                tree = stack.file.Tree(os.path.join('/export/stack/carts',
                                                            cart))
                for file in tree.getFiles('graph'):
                        shutil.copy(file.getFullName(),
                        	os.path.join(build, 'graphs', 'default', file.getName()))
                        
                for file in tree.getFiles('nodes'):
                        shutil.copy(file.getFullName(),
                        	os.path.join(build, 'nodes', file.getName()))
                

    def applyRPM(self, name, root, flags=''):
        """Used to 'patch' the new distribution with RPMs from the
        distribution.  We use this to always get the correct
        genhdlist, and to apply eKV to Stack distributions.
        
        Throws a ValueError if it cannot find the specified RPM, and
        BuildError if the RPM was found but could not be installed."""

	rpm = None
	try:
        	rpm = self.dist.getRPM(name)
	except stack.dist.DistRPMList, e:
		for r in e.list:
			if r.getPackageArch() == self.dist.getArch():
				rpm = r
				break

        if not rpm:
            raise ValueError, "could not find %s" % name

        dbdir = os.path.join(root, 'var', 'lib', 'rpm')
        if not os.path.isdir(dbdir):
            os.makedirs(dbdir)

        reloc = os.system("rpm -q --queryformat '%{prefixes}\n' -p " +
                        rpm.getFullName() + "| grep none > /dev/null")

	cmd = 'rpm -i --ignoresize --nomd5 --force --nodeps --ignorearch '
        if reloc:
	    cmd = cmd + '--prefix %s %s %s' % (root, flags,
					       rpm.getFullName())
        else:
	    cmd = cmd + '--badreloc --relocate /=%s %s %s' % (root, flags,
							      rpm.getFullName())

	# Run with dbpath
        dbpath_cmd = cmd + ' --dbpath %s > /dev/null' % dbdir
        retval = os.system(dbpath_cmd)

	# If it fails, try running without dbpath
	if retval != 0:
	    retval = os.system('%s > /dev/null' % cmd)

        shutil.rmtree(os.path.join(root, 'var'))

        if retval != 0:
            raise BuildError, "could not apply RPM %s" % (name)

        return retval


    def buildProductImg(self):
	print('Building product.img')
	#
	# the directory where the python files exist that are used to
	# extend anaconda
	#
	product = '../../images/product.img'
	productfilesdir = os.path.join(self.dist.getBuildPath(), 'include')

	if not os.path.exists(productfilesdir):
		os.makedirs(productfilesdir)

	cwd = os.getcwd()

	#
	# make an MD5 checksum for all files in the distribution
	#
	# the 'sed' command strips off the leading "./" from the pathnames
	#
	# don't include the build, SRPMS and force directories
	#
	os.chdir(self.dist.getReleasePath())
	cmd = '/usr/bin/md5sum `find -L . -type f | sed "s/^\.\///" | '
	cmd += 'egrep -v "^build|^SRPMS|^force"` '
	cmd += '> %s/packages.md5' % (productfilesdir)
	os.system(cmd)

	#
	# create the product.img file
	#
	os.chdir(productfilesdir)

	if not os.path.exists('../../images'):
		os.makedirs('../../images')

	os.system('rm -f %s' % (product))
	cmd = '/sbin/mksquashfs * %s ' % (product)
	cmd += '-keep-as-directory > /dev/null 2>&1'
	os.system(cmd)

	if os.path.exists(product):
		#
		# on a server installation (e.g., frontend), mksquashfs
		# fails, but it is not important that product.img is built
		# during the installation. product.img was already downloaded
		# off the CD, so it will not be needed for the remainder of
		# the server installation.
		#
		os.chmod(product, 0o666)

	os.chdir(cwd)
	return


    def createrepo(self):

        # If we can determince the number of CPUs create N worker threads,
        # Otherwise just do the default of 1.

        try:
	    import multiprocessing
            n = multiprocessing.cpu_count()
        except:
            n = 0
        if not n:
            n = 1

	print('Creating repository ...')

	cwd = os.getcwd()
	releasedir = self.dist.getReleasePath()
	os.chdir(releasedir)

	#
	# first check in the install environment (/tmp/updates), then
	# look in the 'normal' place (on a running frontend).
	#
	createrepo = '/tmp/updates/usr/share/createrepo/genpkgmetadata.py'
	if not os.path.exists(createrepo):
		createrepo = '/usr/share/createrepo/genpkgmetadata.py'

	os.system('%s ' % (createrepo) + 
		'--groupfile %s/RedHat/base/comps.xml .' % (releasedir))

	os.chdir(cwd)

	return

    def cleaner(self, path, file, root):
        if not root:
            root = self.dist.getReleasePath()
        dir = os.path.join(root, path)
        if dir not in [ self.dist.getForceRPMSPath() ]:
            os.unlink(os.path.join(dir, file.getName()))

    def builder(self, path, file, root):
        if not root:
            root = self.dist.getReleasePath()
        dir	 = os.path.join(root, path)
        fullname = os.path.join(dir, file.getName())

        if file.getFullName() == fullname:
            return

        if not os.path.isdir(dir):
            os.makedirs(dir)

        # Create the new distribution either with all symbolic links
        # into the mirror, contrib, and local rpms.  Or copy
        # everything.  The idea is local distributions should be all
        # symlinks, but a published base distribution (like the NPACI
        # Rocks master) should be copys.  This keeps the FTP chroot
        # environment happy, extends the lifetime of the release past
        # that of scattered RPMS.  It may also make sense to have your
        # master distribution for your cluster done by copy.
        
        if self.useLinks:
            file.symlink(fullname, self.dist.getRootPath())
        else:

            # For copied distributions, the timestamps of the new
            # files are forced to that of the source files.  This
            # keeps wget happy.

            if os.path.islink(file.getFullName()):
                os.symlink(os.readlink(file.getFullName()), fullname)
            else:
                shutil.copy(file.getFullName(), fullname)
                os.utime(fullname, (file.getTimestamp(), file.getTimestamp()))

    def normalizer(self, path, file, root):
        if not root:
            root = self.dist.getReleasePath()
        dir	 = os.path.join(root, path)
        fullname = os.path.join(dir, file.getName())

        # Reset the File to represent the one we just created in the new
        # distribution.
        
        if file.getFullName() != fullname:
            file.setFile(fullname)

    def resolveVersions(self, files):

        # Use a dictionary (hash table) to find and resolve all the
        # version conflict in the list of files.  We use a dictionary
        # to avoid an O(n) list based approach.  Burn memory, save
        # time.

        dict = {}
        for e in files:
            if self.doResolve:
		name = e.getUniqueName() # name w/ arch string appended
	    else:
                name = e.getName()
            if not dict.has_key(name) or e >= dict[name]:
                dict[name] = e

        # Extract the File objects from the dictionary and return
        # them as a list.
        
        list = []
        for e in dict.keys():
            list.append(dict[e])

        if self.doResolve:
            print('\tremoving %d older packages' % (len(files) - len(list)))
        return list

    def setComps(self, path):
    	self.compsPath = path

