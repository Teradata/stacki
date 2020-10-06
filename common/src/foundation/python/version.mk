ORDER      = 0
VERSION    = 3.9.0
# This was the hacky way I figured out to get %post and %postun in.
RPM.EXTRAS = "AutoReq: no\\n\\n%post\\n/sbin/ldconfig\\n\\n%postun\\n/sbin/ldconfig"
