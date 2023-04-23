all: clean srpm rpm

rpm:
	for srpms in *.src.rpm; do \
		echo "BUILD: create RPM from SRPM: $$srpms"; \
		rpmbuild --rebuild $$srpms; \
	done

clean:
	echo "CLEAN: *.src.rpm"
	if ls -1 *.src.rpm >/dev/null 2>&1; then ls -1 *.src.rpm  | xargs rm; fi

distclean: clean
	echo "CLEAN: downloaded *.tar.gz"
	if ls -1 *.tar.gz  >/dev/null 2>&1; then ls -1 *.tar.gz   | xargs rm; fi

srpm:
	echo "BUILD: create SRPM like COPR is doing"
	make -f ./.copr/Makefile srpm outdir="." spec="signal-cli.spec"
