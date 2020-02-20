# Stacki on Docker

This is active development and not a real feature yet. For now the
only supported use is to deploy a Frontend system for development. The
ability to build backend machines from this Frontend is not
supported. This is only the first step to exploring how to blow Stacki
apart into several containers.

Docker support only exists for CentOS (sorry SLES) at this time.

## Pre-Reqs

You must have docker installed and configured on your host. If you are
using Docker on the Mac go into the advanced/disk settings and
allocation at least 8GBs RAM, 2 CPUs, and 64GB of Disk.

### Build Source

```
# cd stacki/docker
# docker-compose build
```

## Running

Start the container using a persistent volume for `/root`. If the
`develop` volume does not already exist, docker will create it for
you.

```
# docker-compose up -d
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

Local port 2200 will forward to port 22 inside the container (see
`docker-compose.yaml`).

```
ssh -p2200 root@localhost
```

And you're in.

