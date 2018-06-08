# Stacki Test Framework

A test framework for running unit, integration, and system test suites against a Stacki ISO.

## Installation

You need to have [Vagrant](https://www.vagrantup.com/) and either [VirtualBox](https://www.virtualbox.org/) or KVM installed. If using KVM, you also need to [install the vagrant-libvirt plugin](https://github.com/vagrant-libvirt/vagrant-libvirt#installation) and NFS server on the host, with the NFS firewall ports opened.

Then change into the `test-framework` folder in the `stacki` codebase on your computer and run `make`. This will build a Python virtualenv that contains all the Python modules needed to run the tests.

## Usage

After running `make` to build the test framework, you can run all the tests with this script:
    
    ./run-tests.sh [flags...] STACKI_ISO

where STACKI_ISO is the ISO you want to use to provision a frontend for running tests against. Besides passing a local path as the STACKI_ISO argument, you can also pass a URL, like so:

    ./run-tests.sh http://example.com/stacki-5.0_20180214_b19821a-redhat7.x86_64.disk1.iso

The following flags are available to just run the specified test suite types. Without any flags, all three types of test suites are run:

    --unit
    --integration
    --system

There is also a flag that currently just runs the first system test, which installs Stacki on a frontend node and then provisions two backend nodes:

    --system-quick

So, if you want to just run the unit and integration test suites, you could do so like this:

    ./run-tests.sh --unit --integration http://example.com/stacki-5.0_20180214_b19821a-redhat7.x86_64.disk1.iso

You can also supply extra ISOs to the framework as a comma seperated list, which will be passed to the system tests, using this flag:

    --extra-isos=FIRST_ISO,SECOND_ISO...

For example, Stacki SLES11 can't be a frontend, but the 01-barnacle-install is aware of Stacki SLES11 ISOs, and will use it to test provisioning SLES11 backends, like so:
    
    ./run-tests.sh --system stacki-5.1rc2-sles12.x86_64.disk1.iso --extra-isos=stacki-5.1rc2-sles11.x86_64.disk1.iso

By default, code coverage reports will be generated in the `reports` directory, in `unit` and `integration` subdirectories for those types of tests. To turn off this report generation, you can use the flag:

    --no-cov

You can destroy the Python virtualenv and clean up the project by running:

    make clean

## Test Types

The exact borders between different test types is a bit of a gray area in the industry, so for this project I'm defining them as follows:

**Unit** - Tests for a single Python function. The tests for class's functions should be grouped in a TestCLASSNAME class. All dependencies other than the Python standard libary (network data, database access, function calls, etc) should be mocked out. The functions should be tested in complete isolation.

**Integration** - Tests for a single Stacki command. There is no need to mock out any dependencies, such as database
access. However, you may want to mock out network access, to speed up the tests as needed.

**System** - Tests for installing complete systems, frontend and backend nodes, from a blank VM to a fully running cluster.

## How To Write New Tests

* **Unit** - TBD
* **Integration** - [test-suites/integration/README.md](test-suites/integration/README.md)
* **System** - TBD
