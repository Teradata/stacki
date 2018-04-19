# @copyright@
# @copyright@

from stack.api.base import Base

class Box(Base):

	def get_names(self):
		result = [ ]
		for name, in self.db.select('name from boxes'):
			result.append(name)
		return result





