#!/bin/bash

# Reset the Django Database
/opt/stack/share/stack/bin/django_db_reset.py

# Create Django secret key file. Set permissions
/opt/stack/share/stack/bin/django_secret.py
chown root:apache /opt/stack/etc/django.secret
chmod 0640 /opt/stack/etc/django.secret

# Create django access to django db
/opt/stack/share/stack/bin/django_db_setup.py

# Create Django Database tables
DJANGO_SETTINGS_MODULE=stack.restapi.settings \
	/opt/stack/bin/django-admin.py makemigrations

DJANGO_SETTINGS_MODULE=stack.restapi.settings \
	/opt/stack/bin/django-admin.py migrate

# Create a default group
/opt/stack/bin/stack add api group default

# Set default permissions
/opt/stack/bin/stack add api group perms default perms="list *"

# Blacklist commands that must not be run
/opt/stack/bin/stack add api blacklist command command="list host message"
/opt/stack/bin/stack add api blacklist command command="add api sudo command"
/opt/stack/bin/stack add api blacklist command command="report system"

# Commands that require "sudo" to be run
STACK_CMDS=( "sync *"	\
	"load *" 	\
	"unload *"	\
	"remove host"	\
	"add pallet" 	\
	"enable pallet" 	\
	"disable pallet" 	\
	"remove pallet"	\
	"list host switch" \
	)


for i in "${STACK_CMDS[@]}"; do \
	/opt/stack/bin/stack add api sudo command command="${i}" sync=False
done

/opt/stack/bin/stack sync api sudo command

# Create an admin user, and write the credentials
#     to a webservice credential file
/opt/stack/bin/stack add api user admin admin=true output-format=json > /root/stacki-ws.cred

# Allow "nobody" to run stack list commands. These will
# be run with minimal privileges, and no write access
# to the database. This is so that apache can sudo down
# to nobody when running commands as non-privileged users
/opt/stack/bin/stack set access command='list *' group=nobody

# Allow write access to the pallets directory by apache.
chgrp apache /export/stack/pallets
chmod 0775 /export/stack/pallets
