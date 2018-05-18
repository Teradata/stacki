#! /opt/stack/bin/python
# 
# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@
#
# $Log$
# Revision 1.13	 2010/09/07 23:53:08  bruno
# star power for gb
#
# Revision 1.12	 2009/05/01 19:07:08  mjk
# chimi con queso
#
# Revision 1.11	 2008/10/18 00:56:02  mjk
# copyright 5.1
#
# Revision 1.10	 2008/03/06 23:41:44  mjk
# copyright storm on
#
# Revision 1.9	2007/06/23 04:03:24  mjk
# mars hill copyright
#
# Revision 1.8	2006/09/11 22:47:23  mjk
# monkey face copyright
#
# Revision 1.7	2006/08/10 00:09:41  mjk
# 4.2 copyright
#
# Revision 1.6	2006/01/16 06:48:59  mjk
# fix python path for source built foundation python
#
# Revision 1.5	2005/10/12 18:08:42  mjk
# final copyright for 4.1
#
# Revision 1.4	2005/09/16 01:02:21  mjk
# updated copyright
#
# Revision 1.3	2005/07/11 23:51:35  mjk
# use rocks version of python
#
# Revision 1.2	2005/05/24 21:21:57  mjk
# update copyright, release is not any closer
#
# Revision 1.1	2005/03/01 00:22:08  mjk
# moved to base roll
#
# Revision 1.15	 2004/03/25 03:15:48  bruno
# touch 'em all!
#
# update version numbers to 3.2.0 and update copyrights
#
# Revision 1.14	 2004/02/04 20:29:37  mjk
# graph reverse was broken
#
# Revision 1.13	 2004/02/02 21:43:52  mjk
# remove coloring from base graph classes
#
# Revision 1.12	 2004/01/30 18:41:19  mjk
# edges have color
#
# Revision 1.11	 2004/01/29 20:28:43  mjk
# added fillColor to nodes
#
# Revision 1.10	 2003/08/15 22:34:46  mjk
# 3.0.0 copyright
#
# Revision 1.9	2003/05/22 16:39:28  mjk
# copyright
#
# Revision 1.8	2003/04/29 18:37:38  mjk
# fixed reverving
#
# Revision 1.7	2003/04/28 16:01:58  mjk
# reverse() doesn't change pointers
#
# Revision 1.6	2003/04/25 23:16:37  mjk
# mo graph
#
# Revision 1.5	2003/04/24 16:56:13  mjk
# - Better DFS Graph traversing
# - Adding includes directory for the graph
#
# Revision 1.4	2003/02/17 18:43:04  bruno
# updated copyright to 2003
#
# Revision 1.3	2002/10/18 21:33:26  mjk
# Rocks 2.3 Copyright
#
# Revision 1.2	2002/02/21 21:33:28  bruno
# added new copyright
#
# Revision 1.1	2001/09/10 18:31:12  mjk
# wish I remembered what changed...
#

import string


class Node:
	def __init__(self, name):
		self.name      = name
		self.marked    = 0
		self.inDegree  = 0
		self.outDegree = 0

	def reverse(self):
		inDegree  = self.inDegree
		outDegree = self.outDegree
		self.inDegree  = outDegree
		self.outDegree = inDegree

	def setInDegree(self, n):
		self.inDegree = n

	def setOutDegree(self, n):
		self.outDegree = n

	def getInDegree(self):
		return self.inDegree

	def getOutDegree(self):
		return self.outDegree

	def mark(self):
		self.marked = 1

	def unmark(self):
		self.marked = 0

	def isMarked(self):
		return self.marked

	def __repr__(self):
		return self.name



class Edge:
	def __init__(self, a, b):
		self.parent	= a
		self.child	= b
		self.isReversed	= 0 
		a.setOutDegree(a.getOutDegree() + 1)
		b.setInDegree(b.getInDegree() + 1)

	def reverse(self):
		if self.isReversed:
			self.isReversed = 0
		else:
			self.isReversed = 1
		
	def getParent(self):
		if self.isReversed:
			return self.child
		return self.parent

	def getChild(self):
		if self.isReversed:
			return self.parent
		return self.child

	def __repr__(self):
		line = '%s -> %s' % (self.getParent(), self.getChild())
		return line


class Graph:

	def __init__(self):
		self.adjList	= {}
		self.nodes	= {}

	def getNodes(self):
		list = []
		for key, val in self.nodes.items():
			list.append(val)
		return list

	def getEdges(self):
		list = []
		for key, val in self.adjList.items():
			list.extend(val)
		return list
			

	def reverse(self):
		adjList	     = self.adjList
		self.adjList = {}
		for key, node in self.nodes.items():
			node.reverse()
		for key, val in adjList.items():
			for edge in val:
				edge.reverse()
				self.addEdge(edge)

		
	def addEdge(self, e):
		if not e.getParent().name in self.nodes:
			self.nodes[e.getParent().name] = e.getParent()
		if not e.getChild().name in self.nodes:
			self.nodes[e.getChild().name] = e.getChild()

		if e.getParent() in self.adjList:
			self.adjList[e.getParent()].append(e)
		else:
			self.adjList[e.getParent()] = [ e ]

	def hasNode(self, node):
		if node in self.nodes:
			return 1
		return 0

	def getNode(self, node):
		if self.hasNode(node):
			return self.nodes[node]
		return None

	def __getitem__(self, node):
		if node in self.adjList:
			return self.adjList[node]
		else:
			return []
		
	def __repr__(self):
		list = []
		for key, val in self.adjList.items():
			for e in val:
				list.append(e.__repr__())
		return '\n'.join(list)
	

class GraphIterator:

	def __init__(self, graph):
		self.graph	= graph
		self.visited	= {}
		self.finished	= {}

	def run(self, root=None):
		nodes = self.graph.getNodes()
		for node in nodes:
			self.visited[node]  = 0
			self.finished[node] = 0

		if root:
			self.visit(root)
		else:
			for node in nodes:
				if self.visited[node] or node.getInDegree():
					continue
				self.visit(node)

	def visit(self, parent, edge=None):
		self.visitHandler(parent, edge)
		for e in self.graph[parent]:
			child = e.getChild()
			if not self.visited[child]:
				self.visit(child, e)
		self.finishHandler(parent, edge)
		

	def visitHandler(self, n, e):
		self.visited[n] = 1
	
	def finishHandler(self, n, e):
		self.finished[n] = 1
		
	

