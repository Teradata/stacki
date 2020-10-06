# Updating Foundation Python

## Prepare python for stacki

### Fetch and upload the desired python version as a tarball to the teradata-stacki S3 bucket

### Update the foundation python tarball symlink in the stacki source.

Note that this is a broken symlink which is automatically corrected during build

```
cd common/src/foundation/python/
git rm Python-*xz
ln -s ../../../3rdparty/Python-$FULL_VERSION.xz
```

### Scan the codebase for existing references to python versions.

Update the version in:

* common/src/foundation/python/version.mk
* common/3rdparty.json
* common/3rdparty.md
* common/src/stack/build/build/etc/python.mk

A lot of work has been done to minimize places in the code using the full version number.  It is possible these are the only places necessary, if python is still 3.x.

## Prepare python for sles11

You must rebuild foundation-python and foundation-python-packages for sles11 (the portion that will land in sles11's squashfs/initrd)

### Setup a sles 11 build environment.

Build a sles11 backend (maybe you should use stacki for this!), based off of develop (so, not with the python version change yet).  Include the SLES11 SDK and OS-Updates.  Install the openssl that ships with OS-Updates. `zypper install -y curl-openssl1`

## build the new foundation python

Copy in the stacki source code with the new python branch and cd to it.

Sles11 has issues with old TLS.  We have a caching proxy setup for pip to get around this. Copy the pip.conf with our mirror to use it in the sles11 build host:

`cp sles/src/stack/images/SLES/sles11/11sp3/pip.conf /etc/pip.conf`

> in case this file disappears or moves, here's it's contents:

```
[global]
index-url = http://stacki-builds.labs.teradata.com/pypi
trusted-host = stacki-builds.labs.teradata.com
disable-pip-version-check = true
```

Then bootstrap the build host.

`make bootstrap; source /etc/profile.d/stack-build.sh && make bootstrap`

Then build python:

```
cd common/src/foundation/python
make
make install-rpm
```

Transfer the newly built rpm to S3:

`s3cmd put foundation-python-3*rpm s3://teradata-stacki/3rdparty/`

## Build the initrd python packages for the new foundation python

On the same system sles11 system, using the new foundation-python, we'll use pip to fetch and prepare our python packages and their dependencies.

> note, the system may have the older version of spython installed - make sure to specify full path to new one

```

mkdir -p /tmp/initrd/opt/stack/

PKGS="Jinja2 Flask MarkupSafe PyMySQL Werkzeug PyYAML certifi chardet Click idna itsdangerous requests setuptools six urllib3 jsoncomment"
/opt/stack/bin/pip3.8 install --ignore-installed --install-option="--prefix=/tmp/initrd/opt/stack" $PKGS

echo $? # to see if it failed

cd /tmp/initrd
tar -cvzf foundation-python-packages.tar.gz opt/

# Transfer the tarball to a stacki frontend to create an rpm

tar -xvzf foundation-python-packages.tar.gz

# for some reason, stack create package expects the dir parameter to be an absolute path?

stack create package dir=${PWD}/opt/ prefix=/ name=foundation-python-packages release=sles11 version=7.0
```

You can run `rpm -qilp foundation-python-packages-*-sles11.x86_64.rpm` to test the new package and check that the paths look correct

Transfer the package to s3:

`s3cmd put foundation-python-packages-*rpm s3://teradata-stacki/3rdparty/`

Update sles/3rdparty.json for the new filenames

## Fix the broken symlinks in the sles11 dir

```
cd sles/src/stack/images/SLES/sles11/11sp3/RPMS/
rm foundation-python-packages-*-sles11.x86_64.rpm
rm foundation-python-*-sles11.x86_64.rpm
ln -s ../../../../../../../3rdparty/foundation-python-3.8.1-sles11.x86_64.rpm
ln -s ../../../../../../../3rdparty/foundation-python-packages-7.0-sles11.x86_64.rpm
```
