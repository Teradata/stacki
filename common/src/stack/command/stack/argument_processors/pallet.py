import pathlib
from operator import attrgetter
import re
import subprocess
from dataclasses import dataclass
import jsoncomment
from stack.exception import ArgNotFound

# Pallet info from Probepal and the database columns do not have the same names.
# They do have a mapping that ends up being the same values as one another. So
# here we map PalletInfo attribute names to the pallet DB column names.
PALLET_ATTR_MAPPINGS = {
	'name': 'name',
	'version': 'version',
	'rel': 'release',
	'arch': 'arch',
	'os': 'distro_family',
}
# Since we normalize to a Pallet dataclass, this pallet_info_getter uses those
# attribute names (the keys) from the mappings.
pallet_info_getter = attrgetter(*PALLET_ATTR_MAPPINGS)
# Module level "constants"
PALLET_HOOK_DIRNAME = "pallet_hooks"
PALLET_HOOK_ROOT = pathlib.Path(f"/opt/stack/") / PALLET_HOOK_DIRNAME
PALLET_HOOK_METADATA_FILENAME = "pallet_hooks.json"

@dataclass(eq=True, order=True, frozen=True)
class Pallet:
	"""A dataclass representation of the Roll schema in the database."""
	id: int
	# name, version, rel, arch, and os need to match the keys of PALLET_ATTR_MAPPINGS
	name: str
	version: str
	rel: str
	arch: str
	os: str
	url: str

	@classmethod
	def create_from_probepal_pallet_info(cls, pallet_info):
		"""Create a Pallet from a PalletInfo instance."""
		# Don't try to create if attributes are missing from the pallet_info object provided.
		if not all(hasattr(pallet_info, attr_name) for attr_name in PALLET_ATTR_MAPPINGS.values()):
			raise ValueError(
				f"Unable to create Pallet from provided PalletInfo.\nPalletInfo was: {pallet_info}."
			)

		# Map the values of probepal.PalletInfo to the correct attributes of Pallet.
		mapped_kwargs = {
			key: getattr(pallet_info, PALLET_ATTR_MAPPINGS[key])
			for key in PALLET_ATTR_MAPPINGS
		}
		# id and url aren't known from a PalletInfo so just set them to non-existant values.
		return cls(
			id=-1,
			**mapped_kwargs,
			url="",
		)

class PalletArgumentProcessor:

	def get_pallets(self, args, params):
		"""
		Returns a Pallet dataclass with the fields:
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

	def _normalize_pallet_info(self, pallet_info):
		"""Normalize the pallet info to a Pallet dataclass."""
		# If this already has the attributes to be a Pallet, just use it.
		if all(hasattr(pallet_info, attr_name) for attr_name in PALLET_ATTR_MAPPINGS):
			return pallet_info

		return Pallet.create_from_probepal_pallet_info(pallet_info)

	def _get_pallet_hooks(self, operation, pallet_info):
		"""Yield the pallet hooks that should run for this pallet and operation."""
		# Find all pallet_hooks.json
		hook_metadata_files = (
			path for path in PALLET_HOOK_ROOT.glob(f"**/{PALLET_HOOK_METADATA_FILENAME}")
		)

		# Filter to the hooks that should run for this pallet.
		# We allow comments in our JSON.
		json_comment = jsoncomment.JsonComment()
		for hook_file in hook_metadata_files:
			hook_metadata = json_comment.loads(hook_file.read_text())

			# Check if any scripts called out in the file should be run.
			# This should only happen if all conditions are satisfied and we
			# are performing a matching operation.
			for script_file, conditions in hook_metadata.items():
				try:
					if all(
						re.fullmatch(conditions[key], getattr(pallet_info, key))
						for key in PALLET_ATTR_MAPPINGS
					) and any(
						re.fullmatch(operation_condition, operation)
						for operation_condition in conditions["operations"]
					):
						yield (hook_file.parent / script_file).resolve(strict=True)
				except KeyError as exception:
					self.notify(f"{hook_file} is missing the following required key: {exception}")
				except FileNotFoundError as exception:
					self.notify(f"{script_file} specified in {hook_file} not found:\n\n{exception}")

	def run_pallet_hooks(self, operation, pallet_info):
		"""Run the hooks for the pallet operation in progress."""
		pallet_info = self._normalize_pallet_info(pallet_info)
		self.notify(f'checking for hooks in {PALLET_HOOK_ROOT} for {"-".join(pallet_info_getter(pallet_info))}')

		# Find all executable files within the script directory and sort them by name.
		hooks = sorted(
			self._get_pallet_hooks(operation=operation, pallet_info=pallet_info),
			key=lambda script_path: script_path.name,
		)
		# Execute the hooks in name sorted order.
		for hook in hooks:
			self.notify(f'running hook: {hook}')
			try:
				self._exec(str(hook), cwd=hook.parent, check=True)
			except (PermissionError, subprocess.CalledProcessError) as exception:
				self.notify(f'Unable to run hook {hook}:\n\n{exception}\n\nstdout:\n{exception.stdout}\n\nstderr:\n{exception.stderr}')

	def get_pallet_hook_directory(self, pallet_info):
		"""Calculate the hook directory for a given pallet."""
		pallet_info = self._normalize_pallet_info(pallet_info)
		pallet_hook_dir = pathlib.Path("-".join(pallet_info_getter(pallet_info)))
		return pathlib.Path(PALLET_HOOK_ROOT) / pallet_hook_dir
