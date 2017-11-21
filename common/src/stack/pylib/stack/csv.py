#! /opt/stack/bin/python
# 
# @copyright@
# Copyright (c) 2006 - 2017 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import csv


class Iterator(object):

        def __init__(self, input, lcase):
                self.header = None
                self.reader = csv.reader(input)
                self.lcase  = lcase
                
        def __iter__(self):
                return self

        def __next__(self):
                row = None
                while not row:
                        row = self.reader.__next__()

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
                                    if self.lcase:
                                        self.header.append(cell.lower())
                                    else:
                                        self.header.append(cell)
                                row = self.header

                return row


def reader(fin, lcase=True):
        """
        Stacki version of the standard python cvs.reader() function with the
        following additions:

        - All cells have leading and trailing whitespace removed.
        - Empty rows are ignored.
        - A leading '#' comments out a line.
        - lcase flag controls lowercase vs using as is. Default is lowercase

        All Stacki code should use stack.cvs.reader() instead of cvs.reader()
        """
        return Iterator(fin, lcase)


