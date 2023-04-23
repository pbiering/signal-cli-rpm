# signal-cli-rpm
RPM packaged signal-cli

### Information

### supports
- dbus configuration/service file, see also: https://github.com/AsamK/signal-cli/wiki/DBus-service
- systemd unit file

### confilg files
- required ones taken+adjusted from https://github.com/AsamK/signal-cli/tree/master/data

## Usage

### Build RPM

*Recommended on a dedicated build host*

#### preparation

##### based on upstream/main

```
# clone repo
git clone https://github.com/pbiering/signal-cli.git
# change into directory
cd signal-cli-rpm
```

##### based on a published release

```
# fetch release package
wget https://github.com/pbiering/signal-cli-rpm/archive/refs/tags/<VERSION>-<RELEASE>.tar.gz
# extract package
tar xzf signal-cli-rpm-<VERSION>-<RELEASE>.tar.gz
# change into directory
cd signal-cli-rpm-<VERSION>-<RELEASE>
```

#### install dependencies

##### as build user

Extract dependencies

```
rpmbuild -bb signal-cli.spec 2>&1 | awk '$0 ~ "is needed" { print $1 }' | xargs echo "dnf install"
```

##### as system user

Install packages listed above

```
dnf install ...
```

#### create source RPM

create Source RPM by downloading external dependencies

```
make srpm
```

#### build binary RPM

```
make rpm
```


### Install RPM

Transfer RPM to final destination system and install (this will also resolve and install required dependencies)

#### native build

```
dnf localinstall signal-cil-<VERSION>-<RELEASE>.<DIST>.<ARCH>.rpm
``` 

#### via Fedora copr

See here for details: https://copr.fedorainfracloud.org/coprs/pbiering/InternetServerExtensions/

### configuration

See https://github.com/AsamK/signal-cli/wiki
