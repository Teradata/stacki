FROM centos
WORKDIR /tmp

EXPOSE 6379

RUN yum install -y epel-release
RUN yum install -y python2-pip redis
RUN pip install j2cli
RUN pip install j2cli[yaml]

COPY redis.conf.j2 .
COPY start.sh      /

CMD ["/bin/bash", "/start.sh"]
