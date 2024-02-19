### *** signal-cli
###
### see also:
###  - https://github.com/pbiering/signal-cli-rpm
###  - description (below)
###
### Step 1: create source package by
###   download required packages and store to ~/rpmbuild/SOURCES
###   $ rpmbuild -bp --undefine=_disable_source_fetch signal-cli.spec
###
### Step 2: rebuild
### $ rpmbuild -bb signal-cli.spec

# do not create debug packages
%define debug_package %{nil}

%define pname signal-cli


## MAIN VERSIONS+RELEASE
%global version_signal_cli	0.13.0

# EL8: since 0.12.0 bundled libsignal_jni.so requires GLIBC_2.33 while has only 2.28 -> build from https://github.com/exquo/signal-libs-build/ is required
%global version_libsignal	0.36.1

%global release_token 1

## VIRTUALENV+BUNDLED-AS-REQUIRED by EL+EPEL destination directories
%global basedir         /usr/lib/%{pname}
%global bindir		%{basedir}/bin
%global vardir		%{_localstatedir}/lib/%{pname}

%global builddir	%{_builddir}/%{pname}-%{version_signal_cli}


# The user and group signal-cli will run as
# user/group system id will be autogenerated by using -r
%global scuser       signal-cli
%global scgroup      signal-cli

Name:		%{pname}
Summary:	signal-cli commandline, dbus and JSON-RPC interface for the Signal messenger
Version:	%{version_signal_cli}
Release:	%{release_token}%{?dist}

License:	GPLv3
URL:		https://github.com/AsamK/signal-cli

Source0:	https://github.com/AsamK/signal-cli/releases/download/v%{version}/signal-cli-%{version}.tar.gz

# only used on EL8 since 0.12.0
Source1:	https://github.com/exquo/signal-libs-build/releases/download/libsignal_v%{version_libsignal}/libsignal_jni.so-v%{version_libsignal}-x86_64-unknown-linux-gnu.tar.gz


## config files taken+adjusted from https://github.com/AsamK/signal-cli/tree/master/data

# dbus
Source100:	org.asamk.Signal.conf
Source101:	org.asamk.Signal.service

# systemd
Source200:	signal-cli.service


%{?systemd_requires}
BuildRequires:  systemd
Requires(pre):  shadow-utils
Requires:       java-21-openjdk-headless

# for downloading sources
BuildRequires:	wget
BuildRequires:	rpmdevtools

# for testing the build
BuildRequires:	java-21-openjdk-headless

# for dbus
Requires:	dbus-common dbus-tools


%description
signal-cli provides an unofficial commandline, dbus and JSON-RPC interface for the Signal messenger.
user/group      : %{scuser}/%{scgroup}
home directory  : %{vardir}
binary for native interface: %{_bindir}/signal-cli
binary for dbus   interface: %{_bindir}/signal-cli-dbus



%prep
%{__rm} -rf %{builddir}
%{__mkdir} %{builddir}
cd %{builddir}

# nothing to build -> nothing to extract


## SELinux
# (currently no policy)



%build
# nothing to build



%install

cd %{builddir}

install -d -p %{buildroot}%{basedir}

# extract
%{__tar} xf %{SOURCE0} -C %{buildroot}%{basedir} --strip-components=1

# remove non Linux files
%{__rm} -f %{buildroot}%{basedir}/bin/%{pname}.bat

# replace libsignal_jni.so
%if 0%{?rhel} == 8
%{__tar} xf %{SOURCE1} -C %{buildroot}%{basedir}
# check compatibility
ldd %{buildroot}%{basedir}/libsignal_jni.so
# check for file is existing
if [ ! -f %{buildroot}%{basedir}/lib/libsignal-client-%{version_libsignal}.jar ]; then
	echo "ERROR : on implant libsignal_jni.so because of version mismatch"
	%define version_jar $(ls -1 %{buildroot}%{basedir}/lib/libsignal-client-*.jar | %{__sed} 's/.*-\\([0-9.]*\\).jar/\\1/g')
	echo "ERROR : SOURCE0 contains: %{version_jar} (signal-cli-%{version}.tar.gz)"
	echo "ERROR : SOURCE1 contains: %{version_libsignal} (libsignal_jni.so-v%{version_libsignal}-x86_64-unknown-linux-gnu.tar.gz)"
	echo "ERROR : fix version in SPEC file: version_libsignal"
	exit 1
fi
# implant libsignal
echo "INFO  : implant libsignal_jni.so (libsignal_jni.so-v%{version_libsignal}-x86_64-unknown-linux-gnu.tar.gz) into libsignal-client-%{version_libsignal}.jar"
zip -j %{buildroot}%{basedir}/lib/libsignal-client-%{version_libsignal}.jar %{buildroot}%{basedir}/libsignal_jni.so
# remove
%{__rm} %{buildroot}%{basedir}/libsignal_jni.so
%endif

### wrapper scripts
install -d -p %{buildroot}%{_bindir}

## create wrapper "native"
cat > %{buildroot}%{_bindir}/signal-cli << EOF
#!/bin/sh
if [ "\$(whoami)" != "%{scuser}" ]; then
    echo "This command must be run under the signal-cli user (%{scuser})."
    exit 1
fi
export JAVA_HOME=/etc/alternatives/jre_21
%{bindir}/signal-cli "\$@"
EOF


## create wrapper "dbus"
cat > %{buildroot}%{_bindir}/signal-cli-dbus << EOF
#!/bin/sh
export JAVA_HOME=/etc/alternatives/jre_21
%{bindir}/signal-cli --dbus-system "\$@"
EOF


## dbus files
install -d -p %{buildroot}%{_prefix}/share/dbus-1/system.d/
install -D -m 0644 %{SOURCE100} %{buildroot}%{_prefix}/share/dbus-1/system.d/

install -d -p %{buildroot}%{_prefix}/share/dbus-1/system-services/
install -D -m 0644 %{SOURCE101} %{buildroot}%{_prefix}/share/dbus-1/system-services/


# systemd files
install -d -p %{buildroot}%{_unitdir}/
install -D -m 0644 %{SOURCE200} %{buildroot}%{_unitdir}


# home directory setup
install -d -p -m 700 %{buildroot}/var/lib/%{pname}

for d in data avatars; do
	install -d -p -m 700 %{buildroot}%{vardir}/.local/share/%{pname}/$d
	%{__ln_s} .local/share/%{pname}/$d %{buildroot}%{vardir}/$d
done


## SELinux
# (currently no policy)


# replace placeholders
find %{buildroot}%{_unitdir} -type f | while read file; do
        # replace directories
        sed -i -e 's,@BINDIR@,%{bindir},g;s,@BASEDIR@,%{basedir},g;s,@VARDIR@,%{vardir},g;s,@SCUSER@,%{scuser},g;s,@SCGROUP@,%{scgroup},g' $file
done


%check
%{buildroot}%{basedir}/bin/signal-cli --version


%pre
# User & Group
if getent group %{scgroup} >/dev/null; then
	echo "system group for %{pname} already exists: %{scgroup}"
else
	echo "system group for %{pname} needs to be created: %{scgroup}"
	groupadd -r %{scgroup} >/dev/null
fi

if getent passwd %{scuser} >/dev/null; then
	echo "system user  for %{pname} already exists: %{scuser}"
	homedir=$(getent passwd %{scuser} | awk -F: '{ print $6 }')
	if [ "$homedir" != "%{vardir}" ]; then
		echo "system user  for %{pname} already exists: %{scuser} bu has not required home directory: %{vardir} (current: $homedir)"
		exit 1
	fi
else
	echo "system user  for %{pname} needs to be created: %{scuser}"
    	useradd -r -g %{scgroup} -d %{vardir} -s /bin/bash -c "signal-cli commandline, dbus and JSON-RPC interface for the Signal messenger" %{scuser} >/dev/null
fi


# move files from a manual installation
for file in /etc/dbus-1/system.d/org.asamk.Signal.conf /etc/systemd/system/signal-cli.service; do
	if [ -e $file ]; then
		echo "file found from manual installation, renamed: $file -> $file.rpmunknown"
		mv $file $file.rpmunknown
	fi
done


# SELinux
# (currently no policy)



%post
# SELinux
# (currently no policy)

## systemd/service
%systemd_post %{pname}.service



%preun
## systemd/service
%systemd_preun %{pname}.service

# SELinux
# (currently no policy)



%postun
## systemd/service
%systemd_postun %{pname}.service


%posttrans
# SELinux
# (currently no policy)

systemctl daemon-reload
systemctl condrestart %{pname}.service


%files

%attr(755,-,-) %{_bindir}/*

%{_unitdir}/*.service

%{_prefix}/share/dbus-1/system.d/org.asamk.Signal.conf
%{_prefix}/share/dbus-1/system-services/org.asamk.Signal.service

%dir %attr(770,%{scuser},%{scgroup}) %{vardir}
%dir %attr(770,%{scuser},%{scgroup}) %{vardir}/.local/share/%{pname}/*

%{vardir}/*

%{basedir}

## SELinux
# (currently no policy)


%changelog
* Mon Feb 19 2024 Peter Bieringer <pb@bieringer.de> - 0.13.0-1
- New upstream version 0.13.0
- Update requirement to Java 21
- Enforce use of Java 21 in wrapper scripts

* Tue Feb 06 2024 Frank Wall <github@moov.de> - 0.12.8-1
- New upstream version 0.12.8

* Sat Dec 30 2023 Peter Bieringer <pb@bieringer.de>
- Add requirements: dbus-common dbus-tools

* Sun Dec 17 2023 Peter Bieringer <pb@bieringer.de> - 0.12.7-5
- EL8: update libsignal_jni.so to 0.36.1

* Sat Dec 16 2023 Peter Bieringer <pb@bieringer.de> - 0.12.7-4
- New upstream version 0.12.7

* Tue Dec 12 2023 Peter Bieringer <pb@bieringer.de> - 0.12.6-4
- New upstream version 0.12.6

* Mon Oct 23 2023 Peter Bieringer <pb@bieringer.de> - 0.12.5-4
- New upstream version 0.12.5

* Mon Oct 23 2023 Peter Bieringer <pb@bieringer.de> - 0.12.4-4
- New upstream version 0.12.4

* Tue Oct 17 2023 Peter Bieringer <pb@bieringer.de> - 0.12.3-4
- New upstream version 0.12.3

* Sat Oct 07 2023 Peter Bieringer <pb@bieringer.de> - 0.12.2-4
- New upstream version 0.12.2
- EL8: update libsignal_jni.so to 0.32.1

* Sun Aug 27 2023 Peter Bieringer <pb@bieringer.de> - 0.12.1-4
- New upstream version 0.12.1

* Sun Aug 20 2023 Peter Bieringer <pb@bieringer.de> - 0.12.0-4
- EL8: implant libsignal_jni.so 0.30.0 from https://github.com/exquo/signal-libs-build/ to fix minimum required GLIBC_2.33 by upstream
- Add check section

* Sat Aug 19 2023 Peter Bieringer <pb@bieringer.de> - 0.12.0-3
- New upstream version 0.12.0

* Sun May 28 2023 Peter Bieringer <pb@bieringer.de> - 0.11.11-3
- New upstream version 0.11.11

* Sat May 13 2023 Peter Bieringer <pb@bieringer.de> - 0.11.10-3
- systemd unit file: specify PrivateTmp to avoid files with insecure permissions in /tmp
- wrapper scripts: quote arguments

* Thu May 11 2023 Peter Bieringer <pb@bieringer.de> - 0.11.10-2
- Conditional restart after update

* Thu May 11 2023 Peter Bieringer <pb@bieringer.de> - 0.11.10-1
- New upstream version 0.11.10

* Sun Apr 23 2023 Peter Bieringer <pb@bieringer.de> - 0.11.9.1-1
- Initial version
