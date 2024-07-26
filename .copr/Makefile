rpmdev-spectool:
	if rpm -q rpmdevtools; then echo "RPM rpmdevtools is already installed"; else echo "RPM rpmdevtools need to be installed first"; dnf install -y rpmdevtools; fi

curl:
	if rpm -q curl; then echo "RPM curl is already installed"; else echo "RPM curl need to be installed first"; dnf install -y curl; fi

download: rpmdev-spectool curl
	rpmdev-spectool $(spec) | awk '$$1 ~ /^Source/ && $$2 ~ /^http/ { print $$2 }' | while read url; do \
		file=$$(basename $$url); \
		echo "INFO  : download source: $$url -> $$file"; \
		curl -L -s -o $$file $$url; \
		r=$$?; \
		if [ $$r -eq 0 ]; then \
			if [ -s $$file ]; then \
				echo "INFO  : download source: $$url (SUCCESS)"; \
			else \
				echo "ERROR : file empty $$file"; \
				exit 1; \
			fi; \
		else \
			echo "ERROR : download source: $$url (ERROR)"; \
			exit 1; \
		fi; \
		done

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
