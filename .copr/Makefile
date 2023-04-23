download:
	rpmdev-spectool $(spec) | awk '$$1 ~ /^Source/ && $$2 ~ /^http/ { print $$2 }' | while read url; do echo "Download source: $$url"; wget -nv -c $$url; done

srpm:	download
	rpmbuild -bs $(spec) --undefine=_disable_source_fetch --define "_topdir ." --define "_sourcedir ." --define "_srcrpmdir ."
