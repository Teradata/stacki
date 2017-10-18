#
# @copyright@
# @copyright@
# 
from django.conf.urls import include, url
from stack.restapi.views import *

ftoken = '[A-Za-z0-9_\-\.\/]*'

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', StackWS.as_view()),
    url(r'^dir/(?P<file>%s)$' % (ftoken), list_dir),
    url(r'^login$',log_in),
    url(r'^logout$',log_out),
    url(r'^user$',check_user),
    url(r'^upload',upload),
]
