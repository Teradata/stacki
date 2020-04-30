ORDER      = 0
VERSION    = 3.8.2
# This was the hacky way I figured out to get %post and %postun in.
RPM.EXTRAS = "AutoReq: no\\n\\n%post\\n/sbin/ldconfig\\n\\n%postun\\n/sbin/ldconfig"
