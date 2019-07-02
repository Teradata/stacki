# Stacki on Docker

This is active development and not a real feature yet. For now the
only supported use is to deploy a Frontend system for development. The
ability to build backend machines from this Frontend is not
supported. This is only the first step to exploring how to blow Stacki
appart into several containers.

Docker support only exists for CentOS (sorry SLES) at this time.

## Pre-Reqs

You must have docker installed and configured on your host. If you are
using Docker on the Mac go into the advanced/disk settings and
allocation at least 8GBs RAM, 2 CPUs, and 64GB of Disk.

## Grab the Stacki image

You can grab an image from the Stacki Docker repository, or just build
it yourself.

### From Docker

```
# docker pull stacki/frontend-centos:latest
```

### Build Source

```
# cd stacki/docker
# make
```

This will create an image called `stacki/frontend-centos:<version>`.

## Running

Start the contianer using a persistent volume for `/root`. If the
`develop` volume does not already exist, docker will create it for
you.

```
docker run --mount source=develop,target=/root -P --privileged stacki/frontend-centos:<version>
```

On first boot the container start the final stages of a *barnacle*
install. This will take a minute or so, after which the SSH service
will be started and you can log in. You can proceed to the next step
(if needed) without waiting for the *barancle* to complete.

Or you can just `tail -f /tmp/barnacle.log` and wait for it to say
`DONE`.


### Attach

The first time you run a Stacki container do the following:

```
docker ps
```

This will give you the docker generated name of the container

```
docker exec -it <container-name> /bin/bash
```

This will break into the container and run a shell. From here you
should go to `/root/.ssh` and setup your ssh credentials. Because this
volume is persistent you only need to do this once.

### SSH 

Once your credentials are setup in the persistent `/root` volume you
can just ssh directly into the container.

```
docker ps
```

This will give you the local port number that is forwarded to the container's ssh service.

```
ssh -p<local-port> root@localhost
```

And you're in.

