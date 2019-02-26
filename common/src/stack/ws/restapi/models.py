#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
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

class SudoList(models.Model):
	"""
	Models that stores the commands for which sudo
	is required when run.
	"""
	command = models.CharField(max_length=1024)
