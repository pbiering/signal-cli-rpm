rpmdev-spectool:
	if rpm -q rpmdevtools; then echo "RPM rpmdevtools is already installed"; else echo "RPM rpmdevtools need to be installed first"; dnf install -y rpmdevtools; fi

download: rpmdev-spectool
	rpmdev-spectool $(spec) -g

srpm:	download
	if [ -n "$(outdir)" ]; then \
		rpmbuild -bs $(spec) --undefine=_disable_source_fetch --define "_topdir ." --define "_sourcedir ." --define "_srcrpmdir $(outdir)"; \
		ls -vl $(outdir)/signal-cli-*.src.rpm; \
		rpm -qlp $(outdir)/signal-cli-*.src.rpm; \
	else \
		rpmbuild -bs $(spec) --undefine=_disable_source_fetch --define "_topdir ." --define "_sourcedir ." --define "_srcrpmdir ."; \
		ls -vl signal-cli-*.src.rpm; \
		rpm -qlp signal-cli-*.src.rpm; \
	fi
	rpmbuild --showrc | grep -i copr ||:
