FROM centos as builder
WORKDIR /tmp

RUN yum group install -y "Development Tools" "Infrastructure Server"

COPY . stacki/

RUN make -Cstacki bootstrap; exit 0
RUN source ~/.bashrc; make -Cstacki bootstrap
RUN source ~/.bashrc; make -Cstacki BOOTABLE=0
RUN cd stacki/build-stacki-*/disk1; tar -chf ../../../stacki.tar stacki


FROM centos/systemd
WORKDIR /tmp

EXPOSE 22

RUN yum group install -y "Infrastructure Server"
RUN yum install -y emacs git

COPY --from=builder /tmp/stacki.tar .
COPY docker/barnacle.sh .

RUN sh -x barnacle.sh

CMD ["/usr/sbin/init"]
