rpmdev-spectool:
	if rpm -q rpmdevtools; then echo "RPM rpmdevtools is already installed"; else echo "RPM rpmdevtools need to be installed first"; dnf install -y rpmdevtools; fi

wget:
	if rpm -q wget; then echo "RPM wget is already installed"; else echo "RPM wget need to be installed first"; dnf install -y wget; fi

download: rpmdev-spectool wget
	rpmdev-spectool $(spec) | awk '$$1 ~ /^Source/ && $$2 ~ /^http/ { print $$2 }' | while read url; do echo "Download source: $$url"; wget -nv -c $$url; done

srpm:	download
	rpmbuild -bs $(spec) --undefine=_disable_source_fetch --define "_topdir ." --define "_sourcedir ." --define "_srcrpmdir ."
	rpm -qlp *.src.rpm
	rpmbuild --showrc |grep -i copr
