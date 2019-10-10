from abc import ABC, abstractmethod
from operator import attrgetter
import pathlib
import importlib
import pkgutil
import inspect
from dataclasses import dataclass

@dataclass(eq=True, order=True, frozen=True)
class PalletInfo:
	name: str
	version: str
	release: str
	arch: str
	distro_family: str
	pallet_root: str

	def is_complete(self):
		return all((self.name, self.version, self.release, self.arch, self.distro_family))


class Probe(ABC):
	'''
	Base probe class.  Subclasses must implement probe() and __init__()
	Lower weight probes will be attempted first.

	Subclassed `Probe.probe()` must return a (potentially empty) list of PalletInfo() objects

	Probe instances are callables. `__call__(arg)` will pass through to `Probe.probe()`
	'''

	isProbe = True

	@abstractmethod
	def __init__(self, desc, weight=90):
		self.weight = weight
		self.desc = desc

	@abstractmethod
	def probe(self, pallet_root):
		raise NotImplementedError

	def __str__(self):
		return f'{self.__class__.__name__} (supports {self.desc})'

	def __repr__(self):
		return f'{self.__class__.__name__}(weight={self.weight})'

	def __call__(self, pallet_root):
		return self.probe(pallet_root)

class Prober:

	def __init__(self):
		'''
		find and import all pallet probes in python modules in the directory.
		Probes are returned sorted by their weight to allow us to do things like check
		for rolls.xml inside foreign pallets, or potentially insert a probe at the end
		which might false-positive ID something else
		'''
		path = pathlib.Path(__file__).resolve().parent
		pkg_paths = {fi.parent for fi in path.glob('probe_*.py')}

		plugins = {}
		for _, name, _ in pkgutil.walk_packages(pkg_paths):
			if not name.startswith('probe'):
				continue
			plugins[name] = importlib.import_module('.' + name, 'stack.probepal')

		probes = []
		for module in plugins.values():
			# Get the listing of all classes defined in the module, and instantiate the
			# ones that are subclasses of Prober
			# note, issubclass() doesn't work, as the class as found in the module above
			# is stack.probepal.Prober, not Prober
			for _, cls in inspect.getmembers(module, inspect.isclass):
				if cls.__module__ == module.__name__ and getattr(cls, 'isProbe', False):
					probes.append(cls())

		self.probes = sorted(probes, key=attrgetter('weight'))

	def find_pallets(self, *paths):
		pallet_map = {}
		for path in paths:
			for probe in self.probes:
				# probes return [] if it's a hard non-match
				# n any case, keep looking -- a later probe has a better chance to ID
				pallet = probe(path)
				if pallet:
					# success!
					pallet_map[path] = pallet
					break
			else: #nobreak
				pallet_map[path] = []

		return pallet_map
