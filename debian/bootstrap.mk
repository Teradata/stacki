# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

bootstrap:
	../common/src/stack/build/build/bin/package-install make openssh-server git emacs vim dpkg-dev ruby ruby-dev rubygems build-essential genisoimage curl
	@if [ ! -e /usr/local/bin/fpm ]; then gem install --no-document fpm; fi

