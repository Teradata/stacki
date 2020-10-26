from stack.util import flatten
from stack.exception import ArgNotFound
from stack.argument_processors.pallet import Pallet

class BoxArgProcessor:
	"""
	An Interface class to add the ability to process box arguments.
	"""

	def get_box_name_by_id(self, box_id):
		return self.db.select('name from boxes where id=%s', box_id)[0][0]

	def get_box_names(self, args=None):
		"""
		Returns a list of box names from the database. For each arg in
		the ARGS list find all the box names that match the arg (assume
		SQL regexp). If an arg does not match anything in the database we
		raise an exception. If the ARGS list is empty return all box names.
		"""

		boxes = []
		if not args:
			args = ['%']		      # find all boxes

		for arg in args:
			names = flatten(self.db.select(
				'name from boxes where name like %s', (arg,)
			))

			if not names and arg != '%':
				raise ArgNotFound(self, arg, 'box')

			boxes.extend(names)

		return boxes

	def get_box_pallets(self, box='default'):
		"""
		Returns a list of pallets for a box
		"""

		# Make sure 'box' exists
		self.get_box_names([box])

		pallets = []

		rows = self.db.select("""
			r.id, r.name, r.version, r.rel, r.arch, o.name, r.url
			from rolls r, boxes b, stacks s, oses o
			where b.name=%s and b.id=s.box and s.roll=r.id and b.os=o.id
			ORDER BY r.id
		""", (box,))

		pallets.extend([Pallet(*row) for row in rows])

		return pallets

	def get_box_carts(self, box='default'):
		"""
		Returns a list of carts for a box
		"""

		# Make sure 'box' exists
		self.get_box_names([box])

		rows = self.db.select("""
			carts.name, boxes.name AS box
			FROM carts, cart_stacks AS cs, boxes
			WHERE carts.id = cs.cart
			AND cs.box = boxes.id
			AND boxes.name=%s
			ORDER BY carts.id
		""", (box,))

		return list(rows)
