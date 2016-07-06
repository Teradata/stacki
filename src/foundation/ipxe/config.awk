/DOWNLOAD_PROTO_HTTPS/ {
	printf("#define DOWNLOAD_PROTO_HTTPS\n");
	next;
}
{ print $0 }
