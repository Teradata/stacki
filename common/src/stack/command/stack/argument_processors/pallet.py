from collections import namedtuple
from stack.exception import ArgNotFound

class PalletArgumentProcessor:

	def get_pallets(self, args, params):
		"""
		Returns a Pallet namedtuple with the fields:
			name, version, rel, arch, os, url

		If args is None or empty then all pallets are returned.

		SQL regexp can be used in both the parameter and arg lists, but
		must expand to something.
		"""

		# Load the params but default to SQL wildcards
		version = params.get('version', '%')
		rel = params.get('release', '%')
		arch = params.get('arch', '%')
		os = params.get('os', '%')

		# Find all pallet names if we weren't given one
		if not args:
			args = ['%']

		Pallet = namedtuple('Pallet', [
			'id', 'name', 'version', 'rel', 'arch', 'os', 'url'
		])

		pallets = []
		for arg in args:
			rows = self.db.select("""
				id, name, version, rel, arch, os, url from rolls
				where name like binary %s and version like binary %s
				and rel like binary %s and arch like binary %s
				and os like binary %s
			""", (arg, version, rel, arch, os))

			if not rows and arg != '%':
				raise ArgNotFound(self, arg, 'pallet', params)

			# Add our pallet models to the list
			pallets.extend([Pallet(*row) for row in rows])

		return pallets
