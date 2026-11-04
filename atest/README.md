# Robot Framework acceptance tests

Acceptance tests for Robot Framework are naturally created using Robot Framework itself. This folder contains all those acceptance tests and other test data they need.

## Directory contents

- **[`run.py`](run.py)** — Script for executing acceptance tests. See [Running acceptance tests](#running-acceptance-tests).
- **[`robot/`](robot/)** — Actual acceptance tests. See [Test data](#test-data).
- **[`resources/`](resources/)** — Resources needed by acceptance tests in `robot/`.
- **[`testdata/`](testdata/)** — Tests executed by the acceptance tests in `robot/`. See [Test data](#test-data).
- **[`testresources/`](testresources/)** — Resources needed by test cases in `testdata/`. Some are also used by [unit tests](../utest/README.rst).
- **[`results/`](results/)** — Generated test execution results. This directory is in `.gitignore` and can safely be deleted at any time.
- **[`genrunner.py`](genrunner.py)** — Generates acceptance test runners in `robot/` based on test data files in `testdata/`. Mainly useful when tests in these directories have a one-to-one mapping.

  Usage:

  ```bash
  atest/genrunner.py atest/testdata/path/data.robot [atest/robot/path/runner.robot]
  ```

## Running acceptance tests

Robot Framework's acceptance tests are executed using the [run.py](run.py) script. Its usage is as follows:

```text
atest/run.py [--interpreter interpreter] [--schema-validation] [options] [data]
```

`data` is the path (or paths) of the file or directory under the [`atest/robot`](robot/) folder to execute. If `data` is
not given, all tests except for tests tagged with `no-ci` are executed. See the [Test tags](#test-tags) section below for
more information about the `no-ci` tag and tagging tests in general.

Available `options` are the same that can be used with Robot Framework. See its help (e.g. `robot --help`) for more information.

By default, tests are executed using the same Python interpreter that is used for running the `run.py` script. That can
be changed by using the `--interpreter` (`-I`) option. It can be the name of the interpreter (e.g. `pypy3`) or a path to
the selected interpreter (e.g. `/usr/bin/python39`). If the interpreter itself needs arguments, the interpreter and its
arguments need to be quoted (e.g. `"py -3.9"`).

`--schema-validation` can be used to enable [schema validation](#schema-validation) for all output.xml files.

Examples:

```bash
# Execute all tests.
atest/run.py

# Execute all tests using a custom interpreter.
atest/run.py --interpreter pypy3

# Exclude tests requiring lxml. See the Test tags section for more information.
atest/run.py --exclude require-lxml

# Exclude tests requiring manual interaction or Telnet server.
# This is needed when executing a specified directory containing such tests.
# If data is not specified, these tests are excluded automatically.
atest/run.py --exclude no-ci atest/robot/standard_libraries
```

The results of the test execution are written into an interpreter specific directory under the [`atest/results`](results/) directory.
Temporary outputs created during the execution are created under the system temporary directory.

## Test data

The test data is divided into two sides, the execution side ([atest/robot](robot) directory) and the test data side
([atest/testdata](testdata) directory). The test data side contains test cases for different features. The execution side
contains the actual acceptance tests that run the tests on the test data side and verify their results.

The basic mechanism to verify that a test case in the test data side is executed as expected is setting the expected status
and possible error message in its documentation. By default, tests are expected to pass, but having `FAIL` or `SKIP`
(these and subsequent markers are case-sensitive) in the documentation changes the expectation. The text after the `FAIL`
or `SKIP` marker is the expected error message, which, by default, must match the actual error exactly. If the error message
starts with `REGEXP:`, `GLOB:` or `STARTS:`, the expected error is considered to be a regexp or glob pattern matching the
actual error, or to contain the beginning of the error. All other details can be tested also, but that logic is in the execution side.

## Test tags

The tests on the execution side ([`atest/robot`](robot/)) contain tags that are used to include or exclude them based on
the platform and required dependencies. Selecting tests based on the platform is done automatically by the [run.py](run.py)
script, but additional selection can be done by the user, for example, to avoid running tests with [dependencies](#dependencies)
that are not met.

| Tag | Purpose |
| --- | --- |
| `manual` | Require manual interaction from the user. Used with Dialogs library tests. |
| `telnet` | Require a Telnet server with a test account running on localhost. See [Telnet tests](#telnet-tests). |
| `no-ci` | Tests not executed in continuous integration, including all tests tagged `manual` or `telnet`. |
| `require-yaml`, `require-lxml`, `require-screenshot` | Require a Python module or other external tool. Exclude tests (e.g. `--exclude require-lxml`) if [dependencies](#dependencies) are not met. |
| `require-windows`, `require-py3.13`, ... | Require a particular operating system or Python interpreter. Automatically excluded on other platforms. |
| `no-windows`, `no-osx`, ... | Excluded on specified operating systems or Python interpreters. |

## Dependencies

Certain Robot Framework features require optional external modules or tools to be installed, and naturally tests related
to these features require the same modules/tools as well. This section lists what preconditions are needed to run all
tests successfully. See [Test tags](#test-tags) for instructions how to avoid running certain tests if all preconditions
are not met.

### Execution side dependencies

The execution side has some dependencies listed in [requirements-run.txt](requirements-run.txt) that need to be installed before running
tests. It is easiest to install them all in one go using `pip`:

```bash
pip install -r atest/requirements-run.txt
```

### Test data side dependencies

The test data side contains the tests for various features and has more dependencies than the execution side.

#### Needed Python modules

- [docutils](https://docutils.sourceforge.io/) is needed with tests related to parsing test data in reStructuredText format and with Libdoc tests fordocumentation in reST format.
- [Pygments](https://pygments.org/) is needed by Libdoc tests for syntax highlighting.
- [PyYAML](https://pyyaml.org/) is required with tests related to YAML variable files.
- [Pillow](https://pypi.org/project/Pillow/) for taking screenshots on Windows.
- [lxml](https://lxml.de/) is needed with XML library tests.

It is possible to install the above modules using `pip` individually, but it is easiest to use the provided [requirements.txt](requirements.txt)
file that installs needed packages conditionally depending on the platform:

```bash
pip install -r atest/requirements.txt
```

Notice that the lxml module may require compilation on Linux, which in turn may require installing development headers of
lxml dependencies. Alternatively lxml can be installed using a system package manager with a command like
`sudo apt-get install python-lxml`.

#### Screenshot module or tool

Screenshot library tests require a platform dependent module or tool that can take screenshots. The above instructions
already covered installing [Pillow](https://pypi.org/project/Pillow/) on Windows and on macOS it is possible to use tooling provided by the operating
system automatically. For Linux alternatives consult the [Screenshot library documentation](https://robotframework.org/robotframework/latest/libraries/Screenshot.html).

## Schema validation

### output.xml schema

The generated `output.xml` has a [schema](../doc/schema) that can be tested as part of acceptance tests. The schema is always used
to validate selected outputs (e.g. in [robot/rebot/compatibility.robot](robot/rebot/compatibility.robot)), but validating
all outputs would slow down execution a bit too much.

It is, however, possible to enable validating all outputs by setting `ATEST_VALIDATE_OUTPUT` environment variable to `TRUE`
(case-insensitive) or by using `--schema-validation` (`-S`) option with [`atest/run.py`](run.py). This is recommended
especially if the schema is updated or output.xml changed.

### Libdoc XML and JSON spec schemas

Libdoc can create spec files both in XML and JSON formats and they both have [schemas](../doc/schema).
All generated Libdoc specs are validated automatically in Libdoc tests.

## Telnet tests

Running telnet tests requires some extra setup. Instructions how to run them can be found from
[testdata/standard_libraries/telnet/README.rst](testdata/standard_libraries/telnet/README.rst).
If you don't want to run an unprotected telnet server on your machine, you can always skip these tests by excluding tests
with a tag `telnet` or `no-ci`.

## License and copyright

All content in the `atest` folder is under the following copyright:

```text
Copyright 2008-2015 Nokia Networks
Copyright 2016-     Robot Framework Foundation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
