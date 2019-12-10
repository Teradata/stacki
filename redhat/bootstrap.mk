# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

bootstrap:
	../common/src/stack/build/build/bin/package-install -m "Development Tools" "Infrastructure Server"
	../common/src/stack/build/build/bin/package-install createrepo genisoimage git emacs vim httpd-devel libvirt-devel
