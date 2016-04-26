#! /opt/stack/bin/python
# 
# @SI_Copyright@
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

                        if row[0][0] == '#':
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


