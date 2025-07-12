# ruff: noqa: E402

"""Tasks to help Robot Framework packaging and other development.

Executed by Invoke <http://pyinvoke.org>. Install it with `pip install invoke`
and run `invoke --help` and `invoke --list` for details how to execute tasks.

See `BUILD.rst` for packaging and releasing instructions.
"""

import json
import subprocess
import sys
from pathlib import Path

assert Path.cwd().resolve() == Path(__file__).resolve().parent
sys.path.insert(0, "src")

from invoke import Exit, task
from rellu import initialize_labels, ReleaseNotesGenerator, Version
from rellu.tasks import clean as clean

from robot.libdoc import libdoc

REPOSITORY = "robotframework/robotframework"
VERSION_PATH = Path("src/robot/version.py")
VERSION_PATTERN = 'VERSION = "(.*)"'
SETUP_PATH = Path("setup.py")
RELEASE_NOTES_PATH = Path("doc/releasenotes/rf-{version}.rst")
RELEASE_NOTES_TITLE = "Robot Framework {version}"
RELEASE_NOTES_INTRO = """
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
"""


@task
def format(ctx, targets="src atest utest"):
    """Format code.

    Args:
        targets: Directories or files to format.

    Formatting is done in multiple phases:

    1. Lint code using Ruff. If linting fails, the process is stopped.
    2. Format code using Black.
    3. Re-organize multiline imports using isort to use less vertical space.
       Public APIs using redundant import aliases are excluded.

    Tool configurations are in `pyproject.toml`.
    """
    print("Linting...")
    try:
        ctx.run(f"ruff check --fix --quiet {targets}")
    except Exception:
        print("Linting failed! Fix reported problems.")
        raise
    print("OK")
    print("Formatting...")
    ctx.run(f"black --quiet {targets}")
    ctx.run(f"isort --quiet {targets}")
    print("OK")


@task
def set_version(ctx, version):
    """Set project version in `src/robot/version.py` and `setup.py`.

    Args:
        version: Project version to set or `dev` to set development version.

    Following PEP-440 compatible version numbers are supported:
    - Final version like 3.0 or 3.1.2.
    - Alpha, beta or release candidate with `a`, `b` or `rc` postfix,
      respectively, and an incremented number like 3.0a1 or 3.0.1rc1.
    - Development version with `.dev` postfix and an incremented number like
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
    libraries = [
        "BuiltIn",
        "Collections",
        "DateTime",
        "Dialogs",
        "OperatingSystem",
        "Process",
        "Screenshot",
        "String",
        "Telnet",
        "XML",
    ]
    name = name.lower()
    if name != "all":
        libraries = [lib for lib in libraries if lib.lower().startswith(name)]
        if len(libraries) != 1:
            raise Exit(f"'{name}' is not a unique library prefix.")
    for lib in libraries:
        libdoc(lib, str(Path(f"doc/libraries/{lib}.html")))
        libdoc(lib, str(Path(f"doc/libraries/{lib}.json")), specdocformat="RAW")


@task
def release_notes(ctx, version=None, username=None, password=None, write=False):
    """Generate release notes based on issues in the issue tracker.

    Args:
        version:  Generate release notes for this version. If not given,
                  generated them for the current version.
        username: GitHub username.
        password: GitHub password.
        write:    When set to True, write release notes to a file overwriting
                  possible existing file. Otherwise, just print them to the
                  terminal.

    Username and password can also be specified using `GITHUB_USERNAME` and
    `GITHUB_PASSWORD` environment variable, respectively. If they aren't
    specified at all, communication with GitHub is anonymous and typically
    pretty slow.
    """
    version = Version(version, VERSION_PATH, VERSION_PATTERN)
    file = RELEASE_NOTES_PATH if write else sys.stdout
    generator = ReleaseNotesGenerator(
        REPOSITORY, RELEASE_NOTES_TITLE, RELEASE_NOTES_INTRO
    )
    generator.generate(version, username, password, file)


@task
def build_libdoc(ctx):
    """Update Libdoc HTML template and language support.

    Regenerates `libdoc.html`, the static template used by Libdoc.

    Update the language support by reading the translations file from the Libdoc
    web project and updates the languages that are used in the Libdoc command line
    tool for help and language validation.

    This task needs to be run if there are any changes to Libdoc.
    """
    # FIXME: Use `ctx.run` instead.
    subprocess.run(["npm", "run", "build", "--prefix", "src/web/"])

    source = Path("src/web/libdoc/i18n/translations.json")
    data = json.loads(source.read_text(encoding="UTF-8"))
    languages = sorted([key.upper() for key in data])

    target = Path("src/robot/libdocpkg/languages.py")
    content = target.read_text(encoding="UTF-8")
    in_languages = False
    with target.open("w", encoding="UTF-8") as out:
        for line in content.splitlines():
            if line == "LANGUAGES = [":
                out.write(line + "\n")
                for lang in languages:
                    out.write(f'    "{lang}",\n')
                out.write("]\n")
                in_languages = True
            elif not in_languages:
                out.write(line + "\n")
            elif line == "]":
                in_languages = False


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
