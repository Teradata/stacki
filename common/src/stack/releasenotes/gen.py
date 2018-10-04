#! /opt/stack/bin/python3
#
# @copyright@
# @copyright@

import sys
import re
from collections import OrderedDict
from git import Repo


class CommitProcessor():

	tag = re.compile('tags/stacki\-([a-z0-9.]+)\^0$')
	cat = re.compile('^([A-Z]+[A-Z ]+[A-Z]+):\s*(.*)$')
	
	def __init__(self, commits):
		self.commits = OrderedDict()
		
		release = ''
		for commit in commits:
			release = self.process(release, commit)


	def process(self, release, commit):

		# check if this is the end of a release
		m = re.search(CommitProcessor.tag, commit.name_rev)
		if m:
			release, = m.groups()

		# skip merge commits
		if commit.summary.find('Merge ') == 0:
			return release
		
		if release not in self.commits:
			self.commits[release] = {}

		# check if this a well formatted commit
		m = re.search(CommitProcessor.cat, commit.summary)
		if m:
			self.process_formatted(release, commit)
		else:
			self.process_unformatted(release, commit)

		return release


	def add(self, release, category, bullet, message):
		if category not in self.commits[release]:
			self.commits[release][category] = [ ]
		self.commits[release][category].append((' '.join(bullet).strip(),
							'\n'.join(message).strip()))

	def process_formatted(self, release, commit):
		category   = None
		bullet     = None
		message    = None
		in_message = False
		for line in commit.message.split('\n'):
			m = re.search(CommitProcessor.cat, line)
			if m:
				if category:
					self.add(release, category, bullet, message)
				category, _bullet = m.groups()
				bullet   = [ _bullet.strip() ]
				category = category.lower()
				message  = []
			else:
				if not in_message:
					if len(line) > 0:
						bullet.append(line.strip())
					else:
						in_message = True
				else:
					message.append(line.strip())
		if category:
			self.add(release, category, bullet, message)


	def process_unformatted(self, release, commit):
		bullet   = [ commit.summary.strip() ]
		message  = []
		for line in commit.message.split('\n')[1:]:
			message.append(line)
		self.add(release, 'git', bullet, message)


		
try:
	repo = Repo('../../../..')
except: # when rpm is building this is correct
	repo = Repo('../../..')
assert not repo.bare

release = '%s' % repo.active_branch

cp = CommitProcessor(repo.iter_commits('stacki-5.0.1-rhel7..'))
for release in cp.commits.keys():
	print('# %s' % release)
	for category in [ 'feature', 'bugfix', 'docs', 'breaking change', 'git' ]:
		if category in cp.commits[release]:
			print('\n## %s' % category.title())
			for summary, message in cp.commits[release][category]:
				print('\n* %s' % summary)
				if message:
					print('')
					for line in message.split('\n'):
						print('  %s' % line)
	print('\n')
		





