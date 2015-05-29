#! /opt/stack/bin/python
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

import os
import sys
import string
import getopt
import types
import stack.util
import xml
from xml.sax import saxutils
from xml.sax import handler
from xml.sax import make_parser
from xml.sax._exceptions import SAXParseException

class Application:

    def __init__(self, argv=None):

        # Applets (code in the kickstart graph) doesn't pass sys.argv
        # so pick it up anyway to keep everything working.
        
        if not argv:
            argv = sys.argv
            
        self.args		= []
	self.caller_args	= argv[1:]
        self.usage_command	= os.path.basename(argv[0])
        self.usage_name		= 'Application'
        self.usage_version	= 0
        self.rcfileHandler      = RCFileHandler
        self.rcfileList		= []
	self.rcForce		= []

        self.projectName	 = 'stack'
        self.projectVersionName  = 'base'
        self.projectVersionMajor = '0'
        self.projectVersionMinor = '0'
        self.projectVersionMicro = '0'
        

        self.getopt		= stack.util.Struct()
        self.getopt.s		= [ 'h' ]
        self.getopt.l		= [ 'help',
                                    'list-rcfiles',
                                    'list-project-info',
				    'rcfile='
				    ]

        # Unset our locale
	try:
        	del os.environ['LANG']
	except KeyError:
		pass

        
    def run(self):
        sys.exit(-1)

    def projectInfo(self):
        return [ self.projectName,
                 self.projectVersionName,
                 int(self.projectVersionMajor),
                 int(self.projectVersionMinor),
                 int(self.projectVersionMicro) ]

    def getArgs(self):
        return self.args

    def setArgs(self, list):
        self.args = list


    def parseArgs(self, rcbase=None):
        """Parses the command line arguments and all the relevant
        resource-control (RC) files for this application. The usage_command
        (generally argv[0]) will determine which the name of our rcfile,
        unless overrided with the rcbase argument."""

	# Save any existing options
	args = self.getArgs()

	# First pass to get rcfiles specified on the cmd line
	self.setArgs(self.caller_args)
        self.parseCommandLine(rcfile=1)

	# Parse Resource Control files
	self.setArgs([])
        if not rcbase:
            rcbase = self.usage_command
        self.parseRC(rcbase)
	for rc in self.rcForce:
		self.parseRCFile(rc, rcbase)

	# Command line options always win
        self.setArgs(args + self.args + self.caller_args)
        self.parseCommandLine()


    def parseRC(self, rcbase, section=None):
        rcfile  = rcbase + 'rc'

        if not section:
            section = rcbase

        # Where we look for resource-control files. First in 
        # the default 'etc' location, then HOME, finally in this dir.
        # We use data from all three, such that later rc files take 
        # precedence.

        dirList = [ os.path.join(os.sep,'opt', self.projectName, 'etc') ]
        if os.environ.has_key('HOME'):
            dirList.append(os.environ['HOME'])
        dirList.append('.')

        # Look for both hidden and visible rc files.
        for dir in dirList:
            self.parseRCFile(os.path.join(dir, '.' + rcfile), section)
            self.parseRCFile(os.path.join(dir, rcfile), section)


    def parseRCFile(self, filename, section):
        if os.path.isfile(filename) and filename not in self.rcfileList:
            #print "Parsing:", filename
            self.rcfileList.append(filename)
            file = open(filename, 'r')
            parser  = make_parser()
            handler = self.rcfileHandler(self)
            if section:
                handler.setSection(section)
            parser.setContentHandler(handler)
            try:
                parser.parse(file)
            except SAXParseException, msg:
                print filename, "XML parse exception: ", msg
            file.close()
            

    def parseCommandLine(self, rcfile=0):
    	"""Calls getopt to parse the command line flags. In
	rcfile mode we just get --rcfile options."""

        short = ''
        for e in self.getopt.s:
            if type(e) == types.TupleType:
                short = short + e[0]
            else:
                short = short + e
        long = []
        for e in self.getopt.l:
            if type(e) == types.TupleType:
                long.append(e[0])
            else:
                long.append(e)
        try:
            opts, args = getopt.getopt(self.args, short, long)
        except getopt.GetoptError, msg:
	    sys.stderr.write("error - %s\n" % msg)
            self.usage()
            sys.exit(1)

	for c in opts:
		if rcfile:
			if c[0] != "--rcfile":
				continue
		self.parseArg(c)

	if not rcfile:
        	self.args = args


    def parseArg(self, c):
        if c[0] in ('-h', '--help'):
            self.help()
            sys.exit(0)
        elif c[0] == '--list-rcfiles':
            print self.rcfileList
            sys.exit(0)
        elif c[0] == '--list-project-info':
            print self.projectInfo()
            sys.exit(0)
	elif c[0] == '--rcfile':
		self.rcForce.append(c[1])
        else:
            return 0
        return 1
    
    def usage(self):

        if os.environ.has_key('COLUMNS'):
            cols = os.environ['COLUMNS']
        else:
            cols = 80

        list = [ 'Usage: ', self.usage_command, ' ' ]
        
        # Build string of argument-free short options.
        s = '[-'
        for e in self.getopt.s:
            if len(e) == 1:
                s = s + e
        s = s + ']'
        if len(s) == 3:
            s = ''
        list.append(s)

        # Add the argument short options to the above string
        for e in self.getopt.s:
            if type(e) == types.TupleType:
                v = e[0]
                h = e[1]
            else:
                v = e
                h = 'arg'
            if len(v) != 1:
                list.append(' [-' + v[:-1] + ' ' + h + ']')

        # Add argument-free long options
        for e in self.getopt.l:
            if type(e) == types.TupleType:
                v = e[0]
            else:
                v = e
            if v[len(v)-1] != '=':
                list.append(' [--' + v + ']')

        # Add argument long options
        for e in self.getopt.l:
            if type(e) == types.TupleType:
                v = e[0]
                h = e[1]
            else:
                v = e
                h = 'arg'
            if v[len(v)-1] == '=':
                list.append(' [--' + v[:-1] + ' ' + h + ']')

        list.append(self.usageTail())

        # Print the usage, word wrapped to the correct screen size.
        print self.usage_name, '- version', self.usage_version
        l = 0
        s = ''
        for e in list:
            if l + len(e) <= cols:
                s = s + e
                l = l + len(e)
            else:
                print s
                l = len(e)
                s = e
        if s:
            print s


    def help(self):
        self.usage()


    def usageTail(self):
        return ''


    def getArch(self):
	return stack.util.getNativeArch()



class RCFileHandler(stack.util.ParseXML):

    def __init__(self, application):
        stack.util.ParseXML.__init__(self, application)
        self.foundSection = 0
        self.section	  = self.app.usage_command

    def setSection(self, section):
        self.section = section

    def startElement(self, name, attrs):
        #
        # need to convert all the attributes to ascii strings.
        # starting in python 2, the xml parser puts the attributes in
        # unicode which causes problems with rocks apps classes, specifically
        # those that append path names found in the attributes to the sys.path
        #
        newattrs = {}
        for (aname, avalue) in attrs.items():
            newattrs[aname] = str(attrs[aname])

        if self.foundSection:
            stack.util.ParseXML.startElement(self, name, newattrs)
        elif name == self.section:
            self.startElementSection(name, newattrs)

    def endElement(self, name):
        if self.foundSection and name == self.foundSection:
            self.endElementSection(name)
        if self.foundSection:
            stack.util.ParseXML.endElement(self, name)

    def getOptions(self):
        return self.options


    # <section parent="base">

    def startElementSection(self, name, attrs):
        parent = attrs.get('parent')
        if parent:
            self.app.parseRC(parent, parent)
        self.foundSection = 1

    def endElementSection(self, name, attrs):
        self.foundSection = 0
    
    # <usage>

    def startElement_usage(self, name, attrs):
        usageName    = attrs.get('name')
        usageVersion = attrs.get('version')

        if usageName:
            self.app.usage_name = usageName
        if usageVersion:
            self.app.usage_version = usageVersion
        
    # <option>

    def startElement_option(self, name, attrs):
        argName  = attrs.get('name')
        # Will return None if value is not present.
        argValue = attrs.get('value')

        list = self.app.getArgs()
        
        if len(argName) > 1:
            flag = '--' + argName

            # We differentiate between empty values and
            # no value at all.
            if argValue is not None:
                list.append('%s=%s' % (flag, argValue))
            else:
                list.append(flag)
        else:
            flag = '-' + argName
            if argValue:
                list.append('%s %s' % (flag, argValue))
            else:
                list.append(flag)
        
        self.app.setArgs(list)


    # <project>

    def startElement_project(self, name, attrs):
        self.app.projectName = attrs.get('name')
        self.app.projectVersionName = attrs.get('versionName')
        self.app.projectVersionMajor = attrs.get('versionMajor')
        self.app.projectVersionMinor = attrs.get('versionMinor')
        self.app.projectVersionMicro = attrs.get('versionMicro')
