./stack.py add bootaction default type=install kernel=vmlinuz-3.3_20170202-7.x-x86_64 ramdisk=initrd.img-3.3_20170202-7.x-x86_64 args="ip=bootif:dhcp inst.ks=https://172.16.1.2/install/sbin/profile.cgi inst.geoloc=0 inst.noverifyssl inst.ks.sendmac ramdisk_size=300000"

./stack.py add bootaction no-parallel-format type=install kernel=vmlinuz-3.3_20170202-7.x-x86_64 ramdisk=initrd.img-3.3_20170202-7.x-x86_64 args="ip=bootif:dhcp inst.ks=https://172.16.1.2/install/sbin/profile.cgi inst.geoloc=0 inst.noverifyssl inst.ks.sendmac no-parallel-format ramdisk_size=300000"

./stack.py add bootaction headless type=install kernel=vmlinuz-3.3_20170202-7.x-x86_64 ramdisk=initrd.img-3.3_20170202-7.x-x86_64 args="ip=bootif:dhcp inst.ks=https://172.16.1.2/install/sbin/profile.cgi inst.geoloc=0 inst.noverifyssl inst.ks.sendmac inst.vnc ramdisk_size=300000"

./stack.py add bootaction rescue type=install kernel=vmlinuz-3.3_20170202-7.x-x86_64 ramdisk=initrd.img-3.3_20170202-7.x-x86_64 args="ip=bootif:dhcp inst.ks=https://172.16.1.2/install/sbin/profile.cgi inst.geoloc=0 inst.noverifyssl inst.ks.sendmac rescue ramdisk_size=300000"

./stack.py add bootaction default   type=os kernel="com32 chain.c32" args="hd0"
./stack.py add bootaction localboot type=os kernel="localboot 0"
./stack.py add bootaction hp        type=os kernel="localboot -1"
./stack.py add bootaction memtest   type=os kernel="kernel memtest"
./stack.py add bootaction pxeflash  type=os kernel="kernel memdisk bigraw" ramdisk=pxeflash.img args=keeppxe
