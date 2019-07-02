#!/bin/bash
#
# @copyright@
# Copyright (c) 2006 - 2019 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

cat > redis.yaml <<EOF
redis:
  password: ${REDIS_PASSWORD}
EOF

j2 -o /etc/redis.conf redis.conf.j2 redis.yaml

/usr/bin/redis-server /etc/redis.conf
