# Integration Tests

In the test framework, integration tests are for testing our code at the level of full stack commands. Each PyTest file should focus on testing a single stack command.

In between tests, the following clean up is performed:
1. The MySQL database is rolled back to the state before tests were run.
2. Any file system changes in the "/etc", "/export/stack", and
"/tftpboot" directories are reverted. 

These actions are performed by the `revert_database` and `revert_filesystem` fixtures, defined in `test/conftest.py`. These fixures are set up to automatically run via the `tests/pytest.ini` file, so you do not need to include them in your testing code.

**Any other side-effects caused by your tests will need to be undone** after your test has run, even if your test has failed. The frontend should be brought back to the same exact state between test runs.

## Test Organization and Structure

The tests themselves live in the `tests` directory, and are organized in subfolders based on the stack "verb" (EX: list, load, etc). The PyTest files are named ofter the the command run, for example `stack list host` would be in file `test_list_host.py`. 

There are empty test files for all the stack commands, at the time I ran `generate-test-stubs.sh`. You can re-run that script safely to generate blank test file stubs, if new stack commands are added.

The tests themselves should be organized in a class named after the command, for example `stack list host` should have a class named "TestListHost". The test functions exist in that class and began with "test_". See [tests/report/test_report_discovery.py](tests/report/test_report_discovery.py) for an example of the test class structure.

As you develop tests, if you find yourself doing the same set up or tear down code repeatedly, you can consolidate that code into a PyTest fixture. Place your new fixture in [tests/conftest.py](tests/conftest.py) and it will be automatically loaded into PyTest.

If your test required some static files, you can place them in the `test-files` directory. This directory will be mounted inside of the frontend at `/export/test-files`.

## Test Development Workflow

Here is the workflow I use when developing new tests:

1. Change into the root of the `test-framework` directory and run `make` to build the framework, if you haven't previously built it.

2. Change into the `test-suites/integration/` directory.

3. Run `./set-up.sh STACKI_ISO`, where STACKI_ISO is the path to the Stacki ISO you want to use while developing tests. This will bring up a Stacki frontend into a Vagrant VM, which the tests will be run in.

4. You can now run `./run-tests.sh` to run the tests stored in the `tests` directory. You can run this as many time as you need to as you develop your new tests. You can pass the `--no-cov` flag to disable generating the code coverage output.

5. If you want to just run the specific test you are working on, you can SSH directly into the frontend with the command: `vagrant ssh frontend`. Switch to root user and then you can run `pytest` directly. The "tests" directory on the VM host (IE: your laptop running Vagrant) is mounted in the frontend at `/export/tests`.

6. When you are done with the frontend, or need to rebuild it, run `./tear-down.sh` to destroy the VM.
