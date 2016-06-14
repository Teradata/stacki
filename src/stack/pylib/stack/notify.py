# @SI_Copyright@
# @SI_Copyright@

#! /opt/stack/bin/python

import sys

def notify(msg):
	''' generate some code to collect the contents of notify xml attrs as they are run
	TODO: make this code do something useful intead of just append to a file :)
	'''
	filename = '/tmp/notifications.txt'
	with open(filename, "a") as fi:
		fi.write(msg + "\n")

if __name__ == '__main__':
	# Allow the script to be called from the shell
	msg = ' '.join(sys.argv[1:])
	notify(msg)
