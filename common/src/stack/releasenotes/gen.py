#! /opt/stack/bin/python3
#
# @copyright@
# @copyright@

import re
from collections import OrderedDict
from git import Repo

try:
	repo = Repo('../../../..')
except: # when rpm is building this is correct
	repo = Repo('../../..')
assert not repo.bare

commits = OrderedDict()
release = '%s' % repo.active_branch
tag_pattern = re.compile('tags/stacki\-([a-z0-9.]+)\^0$')
cat_pattern = re.compile('^([A-Z]+):\s+(.*)$')

for commit in repo.iter_commits('stacki-5.0.1-rhel7..'):

	# check if this is the end of a release
	m = re.search(tag_pattern, commit.name_rev)
	if m:
		release, = m.groups()

	# skip merge commits
	if commit.summary.find('Merge ') == 0:
		continue


	if release not in commits:
		commits[release] = {}

	# check if this a well formatted commit
	m = re.search(cat_pattern, commit.summary)
	if m:
		category, summary = m.groups()
		category = category.lower()
		if category not in commits[release]:
			commits[release][category] = [ ]
		message = []
		for line in commit.message.split('\n')[1:]:
			if line.find('INTERNAL:') != -1:
				break
			message.append(line)
		commits[release][category].append((summary, '\n'.join(message).strip()))

	else:
		# sloppy old commits (this should not happen anymore
		if 'git' not in commits[release]:
			commits[release]['git'] = [ ]
		summary = commit.summary
		message = []
		for line in commit.message.split('\n')[1:]:
			message.append(line)
		commits[release]['git'].append((summary, '\n'.join(message).strip()))


for release in commits:
	print('# %s' % release)
	for category in [ 'feature', 'bugfix', 'docs', 'git' ]:
		if category in commits[release]:
			print('\n## %s' % category.title())
			for summary, message in commits[release][category]:
				print('\n* %s' % summary)
				if message:
					print('')
					for line in message.split('\n'):
						print('  %s' % line)
	print('\n')
		





