#
# @copyright@
# @copyright@
#

from django.db import models
from django.contrib.auth.models import User, Group

class GroupAccess(models.Model):
	"""
	Model that stores command permissions
	for a group.
	"""
	group = models.ForeignKey(Group)
	command = models.CharField(max_length=1024)	
	
class UserAccess(models.Model):
	"""
	Model that stores command permissions
	for a user.
	"""
	user = models.ForeignKey(User)
	command = models.CharField(max_length=1024)	

class BlackList(models.Model):
	"""
	Model that stores commands no one is
	allowed to run
	"""
	command = models.CharField(max_length=1024)
