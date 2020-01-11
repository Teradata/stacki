from collections import namedtuple

from stack.exception import ArgError, ArgNotFound

class RepoArgProcessor:
	REQUIRED_REPO_COLUMNS = [
		'name',
		'alias',
		'url',
	]

	OPTIONAL_REPO_COLUMNS = [
		'autorefresh',
		'assumeyes',
		'type',
		'is_mirrorlist',
		'gpgcheck',
		'gpgkey',
		'os',
		'pallet_id',
	]

	REPO_COLUMNS = REQUIRED_REPO_COLUMNS + OPTIONAL_REPO_COLUMNS

	def insert_repo(self, name, alias, url, **kwargs):
		'''
		Insert a repo with optional kwargs into the repos table.
		If a repo with the same name or alias already exists, raise ArgError
		'''

		if self.get_repo_id(name, alias) is not None:
			raise ArgError(self, name, f'a repo already exists with the name/alias: {name}/{alias}')

		data = {}
		for key in self.OPTIONAL_REPO_COLUMNS:
			if key in kwargs:
				data[key] = kwargs[key]

		cols = ', '.join(['name', 'alias', 'url'] + list(data))
		vals = ', '.join(['%s'] * (3 + len(data.values())))

		sql = f'''INSERT INTO repos
			({cols})
			VALUES
			({vals})
			'''

		self.db.execute(sql, (name, alias, url, *data.values()))

	def delete_repo(self, repo_name_or_alias):
		''' delete the repo from the database, should also remove any box associations '''

		sql = '''DELETE FROM repos WHERE name LIKE %s OR alias LIKE %s '''
		self.db.execute(sql, (repo_name_or_alias, repo_name_or_alias))

	def enable_repo(self, repo_name_or_alias, box):
		''' add a row to the repo_stacks table, tying a repo to a box '''

		repo_id = self.get_repo_id(repo_name_or_alias)
		box_id = self.db.select('id FROM boxes WHERE name=%s', (box,))[0][0]
		sql = '''INSERT INTO repo_stacks
			(box, repo)
			VALUES
			(%s, %s)
			'''
		self.db.execute(sql, (box_id, repo_id))

	def disable_repo(self, repo_name_or_alias, box):
		''' disable the repo for a given box '''

		repo_id = self.get_repo_id(repo_name_or_alias)
		box_id = self.db.select('id FROM boxes WHERE name=%s', (box,))[0][0]
		sql = '''DELETE FROM repo_stacks WHERE box=%s AND repo=%s '''
		self.db.execute(sql, (box_id, repo_id))

	def get_repo_id(self, repo_name, repo_alias = None):
		''' lookup the id of a repo (either by name or alias).  return the id or None '''

		if repo_alias is None:
			repo_alias = repo_name

		rows = self.db.select('''id
			FROM repos
			WHERE name LIKE %s OR alias LIKE %s
		''', (repo_name, repo_alias))

		if not rows:
			return None

		return rows[0][0]

	def get_repos(self, args=None):
		'''
		Return a list of repo named tuples.  For each arg in args, find
		all the box names that match the arg (assume SQL regexp). If an
		arg does not match anything in the database we raise an
		exception. If the ARGS list is empty return all box names.
		'''

		if not args:
			args = ['%']

		cols = ["repos.{}".format(c) for c in self.REPO_COLUMNS if c != 'pallet_id']
		cols.append('pallets.name AS palletname')
		cols.append('pallets.version AS palletversion')
		cols.append('pallets.rel AS palletrelease')
		cols.append('pallets.os AS palletos')
		cols.append('pallets.arch AS palletarch')

		sql = f'''{", ".join(cols)}
			FROM repos
			LEFT JOIN rolls AS pallets
				ON pallets.id = repos.pallet_id
			WHERE repos.name LIKE %s OR repos.alias LIKE %s
		'''

		Repo = namedtuple('Repo', ['pallet' if c == 'pallet_id' else c for c in self.REPO_COLUMNS])
		
		repos = []
		for arg in args:
			rows = self.db.select(sql, (arg, arg))
			if not rows and arg != '%':
				raise ArgNotFound(self, arg, 'repo')

			for row in rows:
				# if a pallet is associated with this repo, return a unique name for it
				repo_data = row[:len(self.REPO_COLUMNS) - 1]
				palletinfo = row[-5:]
				if all(palletinfo):
					row = repo_data + ('-'.join(palletinfo),)
				else:
					row = repo_data + (None, )
				repos.append(Repo(*row))

		return repos

	def get_repos_by_box(self, box):
		'''
		return a dictionary `{box_name: [{repo_name: {repo_keys: repo_vals}}]}`"
		For example:
		{'default': [{
			'stacki 5.4.1 sles15': {
				'name': "stacki 5.4.1 sles15",
				'alias': 'stacki-5.4.1-sles15',
				'url': 'http://example.com/etc/',
				'foo': 'bar',
				},
			},]
		}
		'''

		sql = f'''{", ".join(["repos.{}".format(c) for c in self.REPO_COLUMNS])}
			FROM repos, repo_stacks, boxes
			WHERE boxes.id=repo_stacks.box
				AND repos.id=repo_stacks.repo
				AND boxes.id=%s
			'''

		box_id = self.db.select('id FROM boxes WHERE name=%s', box)[0][0]
		box_data = {}
		for result in self.db.select(sql, (box_id, )):
			repo_data = dict(zip(self.REPO_COLUMNS, result))
			# who knows, maybe someday we want disabled repos in a box?
			repo_data['is_enabled'] = 1
			box_data[repo_data['name']] = repo_data
		return {box: box_data}

	def update_repo_field(self, repo_name_or_alias, **kwargs):
		'''
		update the given field(s) from kwargs into the database for repo
		'''

		repo_id = self.get_repo_id(repo_name_or_alias)


		data = {}
		for key in self.REPO_COLUMNS:
			if key in kwargs:
				data[f'{key}=%s'] = kwargs[key]

		fields = ', '.join(data.keys())

		sql = f'''UPDATE repos
			SET {fields}
			WHERE id={repo_id}
			'''

		self.db.execute(sql, list(kwargs.values()))
