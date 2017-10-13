#!/opt/stack/bin/python3

#
# @copyright@
# @copyright@
#

"""
WSGI config for restapi project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11.6/howto/deployment/wsgi/
"""

import os

# Set the Django environment module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stack.restapi.settings")

import logging
import logging.handlers

# Set logging
log = logging.getLogger("stack-ws")
log.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address='/dev/log',
		facility=logging.handlers.SysLogHandler.LOG_LOCAL2)

formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

log.addHandler(handler)

# Start Logging
log.info("Starting WSGI Request")

# Run Django Application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Logging End
log.info("Completed WSGI Request")
