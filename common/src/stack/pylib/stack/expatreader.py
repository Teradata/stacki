#! /opt/stack/bin/python
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import xml.sax.expatreader

class ExpatParser(xml.sax.expatreader.ExpatParser):

    def external_entity_ref(self, context, base, sysid, pubid):
	    return 1

def create_parser(*args, **kwargs):
    return ExpatParser(*args, **kwargs)
