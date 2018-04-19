# @copyright@
# @copyright@

from stack.api.base import Base

class BootAction(Base):

	def get_names(self, action_type):
		result = [ ]
		for name, in self.db.select('name from bootnames where type=%s', (action_type, )):
			result.append(name)
		return result





