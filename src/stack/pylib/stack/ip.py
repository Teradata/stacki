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
#
# $Log$
# Revision 1.16  2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.15  2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.14  2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.13  2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.12  2007/06/23 04:03:24  mjk
# mars hill copyright
#
# Revision 1.11  2007/05/30 20:43:15  anoop
# *** empty log message ***
#
# Revision 1.10  2006/09/11 22:47:23  mjk
# monkey face copyright
#
# Revision 1.9  2006/08/10 00:09:41  mjk
# 4.2 copyright
#
# Revision 1.8  2006/01/20 19:19:21  mjk
# python 2.4 fixes
#
# Revision 1.7  2006/01/16 06:49:00  mjk
# fix python path for source built foundation python
#
# Revision 1.6  2005/10/12 18:08:42  mjk
# final copyright for 4.1
#
# Revision 1.5  2005/09/16 01:02:21  mjk
# updated copyright
#
# Revision 1.4  2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.3  2005/05/24 21:21:57  mjk
# update copyright, release is not any closer
#
# Revision 1.2  2005/03/15 20:00:16  fds
# Suppress FutureWarnings.
#
# Revision 1.1  2005/03/01 00:22:08  mjk
# moved to base roll
#
# Revision 1.8  2004/03/25 03:15:48  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.7  2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.6  2003/05/22 16:39:28  mjk
# copyright
#
# Revision 1.5  2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.4  2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.3  2002/02/21 21:33:28  bruno
# added new copyright
#
# Revision 1.2  2001/08/08 17:56:38  mjk
# - Added support for contiguous networks.  But, we can't use this code
#   until we switch to the 10.0.0.0 network.
#
# Revision 1.1  2001/05/16 21:44:40  mjk
# - Major changes in CD building
# - Added ip.py, sql.py for SQL oriented scripts
#



# This code now no longer assumes a default netmask and supports
# subnets.  Subnet have some complex rules and implications.  Make
# sure you really need to do this.  Non-contiguous subnets are not
# supported.

# The basic form of an ip address is network-subnet-host.  The main
# rule is both the host and subnet portion cannot have all the bits
# set or all the bits unset.  This mean some addresses that people
# like to use are just wrong.

# For example the address 192.168.0.1 is invalid.  This is because the
# network is not a class B network rather a set of 254 class C
# addresses.  This is why subnets get scary.  Several people do not
# understand this and run around with bogus ip addresses.


from __future__ import print_function
import string
import types
import sys
import warnings

class IPError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return self.value
	def __repr__(self):
		return self.value

class IPAddr:

    def __init__(self, addr):
        if type(addr) == types.StringType:
            self.list = map(int, string.split(addr,'.'))
            self.list.reverse()
        else:
            self.list = []
            self.list.append((addr & 0x000000ff))
            self.list.append((addr & 0x0000ff00) >> 8)
            self.list.append((addr & 0x00ff0000) >> 16)
            self.list.append(((addr & 0xff000000) >> 24) & 0x000000ff)
        

    def address(self):
        return ((self.list[3] << 24) +
                (self.list[2] << 16) +
                (self.list[1] << 8) + self.list[0])
    
    def __call__(self):
        return self.address()
    
    def __getitem__(self, i):
        return self.list[i]

    def __setitem__(self, i, v):
       self.list[i] = v

    def __add__(self, n):
        return IPAddr(self.address() + n)

    def __sub__(self, n):
        return IPAddr(self.address() - n)
    
    def __invert__(self):
        return ~self.address()
    
    def __or__(self, o):
        return self.address() | o.address()

    def __and__(self, o):
        return self.address() & o.address()
        
    def __xor__(self, o):
        return self.address() ^ o.address()

    
    def __repr__(self):
        return '%d.%d.%d.%d' % ( self.list[3], self.list[2],
                                 self.list[1], self.list[0] )




class IPGenerator:

    def __init__(self, network, netmask=None):

        self.network = IPAddr(network)

        # If no netmask was provided infer it from the address
        #
        # 0*   - class A
        # 10*  - class B
        # 110* - class C

        if not netmask:
            if self.network()   & 0x80 == 0x00:
                self.netmask = IPAddr('255.0.0.0')
            elif self.network() & 0xc0 == 0x80:
                self.netmask = IPAddr('255.255.0.0')
            elif self.network() & 0xe0 == 0xc0:
                self.netmask = IPAddr('255.255.255.0')
            else:
                print('not a unicast address', self.network)
                sys.exit(-1)
        else:
            self.netmask = IPAddr(netmask)

        # Set the initial address to the top of the address range.
        
        self.addr = IPAddr(self.network | IPAddr(~self.netmask))


    def curr(self):
        if (self.addr & IPAddr(~self.netmask)) == ~self.netmask:
            raise IPError('At top of address range')

        if (self.addr & IPAddr(~self.netmask)) == 0x00:
            raise IPError('At bottom of address range')

        return self.addr

    def dec(self):
        return self.next()

    def get_network(self):
    	return IPAddr(self.addr & self.netmask)

    def next(self, n=-1):
        addr = self.addr + n

        if (addr & IPAddr(~self.netmask)) == ~self.netmask:
            raise IPError('At top of address range')

        if (addr & IPAddr(~self.netmask)) == 0x00:
            raise IPError('At bottom of address range')

        self.addr = addr
        return self.addr

    def first(self):
	return IPAddr((self.addr & self.netmask) + 1)

    def last(self):
	return IPAddr((self.addr | IPAddr(~self.netmask)) - 1)

    def broadcast(self):
	return IPAddr(self.addr | IPAddr(~self.netmask))

    def cidr(self):
	d = 0
	n = list(self.netmask.list)
	n.reverse()
	for i in n:
		while i > 0:
			i = (i << 1) % (256)
			d = d + 1
	return d

if __name__ == '__main__':
    a = IPGenerator('10.1.1.0', '255.255.255.128')
    print(a.curr())
    a.next(-126)
    print(a.curr())
