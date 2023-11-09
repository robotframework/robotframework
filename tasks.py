"""Tasks to help Robot Framework packaging and other development.

Executed by Invoke <http://pyinvoke.org>. Install it with `pip install invoke`
and run `invoke --help` and `invoke --list` for details how to execute tasks.

See BUILD.rst for packaging and releasing instructions.
"""

from pathlib import Path
import sys

assert Path.cwd().resolve() == Path(__file__).resolve().parent
sys.path.insert(0, 'src')

from invoke import Exit, task
from rellu import initialize_labels, ReleaseNotesGenerator, Version
from rellu.tasks import clean
from robot.libdoc import libdoc


REPOSITORY = 'robotframework/robotframework'
VERSION_PATH = Path('src/robot/version.py')
VERSION_PATTERN = "VERSION = '(.*)'"
SETUP_PATH = Path('setup.py')
POM_VERSION_PATTERN = '<version>(.*)</version>'
RELEASE_NOTES_PATH = Path('doc/releasenotes/rf-{version}.rst')
RELEASE_NOTES_TITLE = 'Robot Framework {version}'
RELEASE_NOTES_INTRO = '''
`Robot Framework`_ {version} is a new release with **UPDATE** enhancements
and bug fixes. **MORE intro stuff...**

**REMOVE reference to tracker if release notes contain all issues.**
All issues targeted for Robot Framework {version.milestone} can be found
from the `issue tracker milestone`_.

Questions and comments related to the release can be sent to the `#devel`
channel on `Robot Framework Slack`_ and possible bugs submitted to
the `issue tracker`_.

**REMOVE ``--pre`` from the next command with final releases.**
If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework=={version}

to install exactly this version. Alternatively you can download the package
from PyPI_ and install it manually. For more details and other installation
approaches, see the `installation instructions`_.

Robot Framework {version} was released on {date}.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3A{version.milestone}
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Slack: http://slack.robotframework.org
.. _Robot Framework Slack: Slack_
.. _installation instructions: ../../INSTALL.rst
'''


@task
def set_version(ctx, version):
    """Set project version in `src/robot/version.py`, `setup.py` and `pom.xml`.

    Args:
        version: Project version to set or `dev` to set development version.

    Following PEP-440 compatible version numbers are supported:
    - Final version like 3.0 or 3.1.2.
    - Alpha, beta or release candidate with `a`, `b` or `rc` postfix,
      respectively, and an incremented number like 3.0a1 or 3.0.1rc1.
    - Development version with `.dev` postix and an incremented number like
      3.0.dev1 or 3.1a1.dev2.

    When the given version is `dev`, the existing version number is updated
    to the next suitable development version. For example, 3.0 -> 3.0.1.dev1,
    3.1.1 -> 3.1.2.dev1, 3.2a1 -> 3.2a2.dev1, 3.2.dev1 -> 3.2.dev2.
    """
    version = Version(version, VERSION_PATH, VERSION_PATTERN)
    version.write()
    Version(str(version), SETUP_PATH, VERSION_PATTERN).write()
    print(version)


@task
def print_version(ctx):
    """Print the current project version."""
    print(Version(path=VERSION_PATH, pattern=VERSION_PATTERN))


@task
def library_docs(ctx, name):
    """Generate standard library documentation.

    Args:
        name:  Name of the library or `all` to generate docs for all libs.
               Name is case-insensitive and can be shortened as long as it
               is a unique prefix. For example, `b` is equivalent to
               `BuiltIn` and `di` equivalent to `Dialogs`.
    """
    libraries = ['BuiltIn', 'Collections', 'DateTime', 'Dialogs',
                 'OperatingSystem', 'Process', 'Screenshot', 'String',
                 'Telnet', 'XML']
    name = name.lower()
    if name != 'all':
        libraries = [lib for lib in libraries if lib.lower().startswith(name)]
        if len(libraries) != 1:
            raise Exit(f"'{name}' is not a unique library prefix.")
    for lib in libraries:
        libdoc(lib, str(Path(f'doc/libraries/{lib}.html')))
        libdoc(lib, str(Path(f'doc/libraries/{lib}.json')), specdocformat='RAW')


@task
def release_notes(ctx, version=None, username=None, password=None, write=False):
    """Generate release notes based on issues in the issue tracker.

    Args:
        version:  Generate release notes for this version. If not given,
                  generated them for the current version.
        username: GitHub username.
        password: GitHub password.
        write:    When set to True, write release notes to a file overwriting
                  possible existing file. Otherwise just print them to the
                  terminal.

    Username and password can also be specified using `GITHUB_USERNAME` and
    `GITHUB_PASSWORD` environment variable, respectively. If they aren't
    specified at all, communication with GitHub is anonymous and typically
    pretty slow.
    """
    version = Version(version, VERSION_PATH, VERSION_PATTERN)
    file = RELEASE_NOTES_PATH if write else sys.stdout
    generator = ReleaseNotesGenerator(REPOSITORY, RELEASE_NOTES_TITLE,
                                      RELEASE_NOTES_INTRO)
    generator.generate(version, username, password, file)


@task
def init_labels(ctx, username=None, password=None):
    """Initialize project by setting labels in the issue tracker.

    Args:
        username: GitHub username.
        password: GitHub password.

    Username and password can also be specified using `GITHUB_USERNAME` and
    `GITHUB_PASSWORD` environment variable, respectively.

    Should only be executed once when taking `rellu` tooling to use or
    when labels it uses have changed.
    """
    initialize_labels(REPOSITORY, username, password)
