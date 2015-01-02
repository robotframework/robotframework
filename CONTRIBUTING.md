# How to contribute

## Reporting bugs or requesting enhancements

Bugs and enhancements are tracked in 
[Github's issue tracker](https://github.com/robotframework/robotframework/issues).
You can try asking first in IRC (#robotframework on irc.freenode.net) or
in the [user group](https://groups.google.com/forum/#!forum/robotframework-users).
Make sure to look through the list of open issues first so that you don't create
a duplicate. When reporting a bug, provide as much information about the bug as
possible: a stack trace or error message, an example test case or keyword, a
log file, and so on. When requesting an enhancement, describe your use case in
as much detail as possible.

## Choosing something to work on

Look through the [issue tracker](https://github.com/robotframework/robotframework/issues)
to find bugs and enhancements to work on. The issues vary significantly in 
complexity and difficulty, so you can try to find something that matches your
skill level and knowledge.

## Creating a pull request

Github has a [good article describing pull requests](https://help.github.com/articles/using-pull-requests/).

### Style guidelines

As with most Python projects, Robot Framework mostly follows [PEP-8](https://www.python.org/dev/peps/pep-0008/).
Any new files you add should include the Apache License header.

### Testing your changes

There are two sets of tests within Robot Framework: `atest` and `utest`. When
submitting a pull request, you should always include tests for your changes.
These tests prove that your changes work, help prevent bugs in the future,
and help document what your changes do. Make sure to run all of the tests before
submitting a pull request to be sure that your changes don't break anything. If
you can, test in multiple environments and interpreters (Windows, Linux, OS X, 
python, jython, ironpython, etc).
 
#### Acceptance tests (atest)

This is a set of tests for Robot Framework written using Robot Framework.
See the [README](atest/README.rst) for more details. If possible, the tests for
your pull request should be acceptance tests.

#### Unit tests (utest)

This is a set of tests for Robot Framework written using Python's `unittest`
module. See the [README](utest/README.rst) for more details.

### Continuous integration

When a new pull request comes in, the CI will ask if one of the admins can 
verify the pull request. The admins are currently @jussimalinen and 
@pekkaklarck. The commands are:

* `robotci: once` (run once)
* `robotci: enable` (run when ever this pull request changes)
* `robotci: whitelist user` (enable CI for all pull requests coming from this 
  user)

The commands can be anywhere on the comment. Adding the skip statement 
(`[skip ci]`, with the square brackets) to the pull request body will cause the 
job not to run.

### AUTHORS.txt

Add yourself to `AUTHORS.txt` if you'd like credit for your changes.
