#! /opt/stack/bin/python
# 
# @SI_Copyright@
#                             www.stacki.com
#                                  v3.1
# 
#      Copyright (c) 2006 - 2016 StackIQ Inc. All rights reserved.
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

from __future__ import absolute_import
import csv

class Iterator(object):

        def __init__(self, input):
                self.header = None
                self.reader = csv.reader(input)
                
        def __iter__(self):
                return self

        def next(self):
                row = None
                while not row:
                        row = self.reader.next()

                        # skip empty lines
                        # strip all cells of whitespace

                        empty = True
                        for cell in row:
                                if cell.strip():
                                        empty = False
                        if empty:
                                row = None
                                continue

                        # after stripping col 0 '#' is a comment

                        if len(row[0]) > 0 and row[0][0] == '#':
                                row = None
                                continue

                        # found the header line, now lowercase everthing

                        if not self.header:
                                self.header = []
                                for cell in row:
                                        self.header.append(cell.lower())
                                row = self.header

                return row


def reader(fin):
        """
        Stacki version of the standard python cvs.reader() function with the
        following additions:

        - All cells have leading and trailing whitespace removed.
        - Empty rows are ignored.
        - A leading '#' comments out a line.
        - Header row has all field names forced to lowercase

        All Stacki code should use stack.cvs.reader() instead of cvs.reader()
        """
        return Iterator(fin)


