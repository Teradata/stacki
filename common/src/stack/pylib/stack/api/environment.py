# @copyright@
# @copyright@

from stack.api.base import Base

class Environment(Base):

	def get_names(self):
		result = [ ]
		for name, in self.db.select('name from environments'):
			result.append(name)
		return result





