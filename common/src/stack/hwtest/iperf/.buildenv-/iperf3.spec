Summary: iperf3
Name: iperf3
Version: 5.0_20171011_28bfe24
Release: master
License: (c)  StackIQ
Vendor: StackIQ
Group: System Environment/Base
Source: iperf3-5.0_20171011_28bfe24.tar.gz

Buildarch: x86_64


%description
iperf3
%prep
%setup
%build
printf "\n\n\n### build ###\n\n\n"
BUILDROOT=/export/src/stacki/common/src/stack/hwtest/iperf/iperf3.buildroot make -f /export/src/stacki/common/src/stack/hwtest/iperf/.buildenv-/iperf3.spec.mk build
%install
printf "\n\n\n### install ###\n\n\n"
BUILDROOT=/export/src/stacki/common/src/stack/hwtest/iperf/iperf3.buildroot make -f /export/src/stacki/common/src/stack/hwtest/iperf/.buildenv-/iperf3.spec.mk install
%files  -f /tmp/iperf3-fileslist
%clean
/bin/rm -rf /tmp/iperf3-fileslist
/bin/rm -rf /export/src/stacki/common/src/stack/hwtest/iperf/iperf3.buildroot
