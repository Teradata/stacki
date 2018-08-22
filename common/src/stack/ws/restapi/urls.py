#
# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@
# 
from django.conf.urls import include, url
from stack.restapi.views import *

ftoken = '[A-Za-z0-9_\-\.\/]*'

urlpatterns = [
    url(r'^$', StackWS.as_view()),
    url(r'^login$',log_in),
    url(r'^logout$',log_out),
    url(r'^user$',check_user),
    url(r'^upload',upload),
]
