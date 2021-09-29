"""Tasks to help Robot Framework packaging and other development.

Executed by Invoke <http://pyinvoke.org>. Install it with `pip install invoke`
and run `invoke --help` and `invoke --list` for details how to execute tasks.

See BUILD.rst for packaging and releasing instructions.
"""

from pathlib import Path
from urllib.request import urlretrieve
import os
import shutil
import sys
import tarfile
import tempfile
import zipfile

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
POM_PATH = Path('pom.xml')
POM_VERSION_PATTERN = '<version>(.*)</version>'
RELEASE_NOTES_PATH = Path('doc/releasenotes/rf-{version}.rst')
RELEASE_NOTES_TITLE = 'Robot Framework {version}'
RELEASE_NOTES_INTRO = '''
`Robot Framework`_ {version} is a new release with **UPDATE** enhancements
and bug fixes. **MORE intro stuff...**

**REMOVE reference to tracker if release notes contain all issues.**
All issues targeted for Robot Framework {version.milestone} can be found
from the `issue tracker milestone`_.

Questions and comments related to the release can be sent to the
`robotframework-users`_ mailing list or to `Robot Framework Slack`_,
and possible bugs submitted to the `issue tracker`_.

**REMOVE ``--pre`` from the next command with final releases.**
If you have pip_ installed, just run

::

   pip install --pre --upgrade robotframework

to install the latest available release or use

::

   pip install robotframework=={version}

to install exactly this version. Alternatively you can download the source
distribution from PyPI_ and install it manually. For more details and other
installation approaches, see the `installation instructions`_.

Robot Framework {version} was released on {date}.

.. _Robot Framework: http://robotframework.org
.. _Robot Framework Foundation: http://robotframework.org/foundation
.. _pip: http://pip-installer.org
.. _PyPI: https://pypi.python.org/pypi/robotframework
.. _issue tracker milestone: https://github.com/robotframework/robotframework/issues?q=milestone%3A{version.milestone}
.. _issue tracker: https://github.com/robotframework/robotframework/issues
.. _robotframework-users: http://groups.google.com/group/robotframework-users
.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com
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
    Version(str(version), POM_PATH, POM_VERSION_PATTERN).write()
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


@task
def jar(ctx, jython_version='2.7.2', pyyaml_version='5.1',
        jar_name=None, remove_dist=False):
    """Create JAR distribution.

    Downloads Jython JAR and PyYAML if needed.

    Args:
        jython_version: Jython version to use as a base. Must match version in
            `jython-standalone-<version>.jar` found from Maven central.
        pyyaml_version: Version of PyYAML that will be included in the
            standalone jar. The version must be available from PyPI.
        jar_name: Name of the jar file. If not given, name is constructed
            based on the version. The `.jar` extension is added automatically
            if needed and the jar is always created under the `dist` directory.
        remove_dist:  Control is 'dist' directory initially removed or not.
    """
    clean(ctx, remove_dist, create_dirs=True)
    jython_jar = get_jython_jar(jython_version)
    print(f"Using '{jython_jar}'.")
    compile_java_files(ctx, jython_jar)
    unzip_jar(jython_jar)
    remove_tests()
    copy_robot_files()
    pyaml_archive = get_pyyaml(pyyaml_version)
    extract_and_copy_pyyaml_files(pyyaml_version, pyaml_archive)
    compile_python_files(ctx, jython_jar)
    version = Version(path=VERSION_PATH, pattern=VERSION_PATTERN)
    create_robot_jar(ctx, str(version), jar_name)


def get_jython_jar(version):
    filename = 'jython-standalone-{0}.jar'.format(version)
    url = (f'http://search.maven.org/remotecontent?filepath=org/python/'
           f'jython-standalone/{version}/{filename}')
    return get_extlib_file(filename, url)


def get_pyyaml(version):
    filename = f'PyYAML-{version}.tar.gz'
    url = f'https://pypi.python.org/packages/source/P/PyYAML/{filename}'
    return get_extlib_file(filename, url)


def get_extlib_file(filename, url):
    lib = Path('ext-lib')
    path = Path(lib, filename)
    if path.exists():
        return path
    print(f"'{filename}' not found, downloading it from '{url}'.")
    lib.mkdir(exist_ok=True)
    urlretrieve(url, path)
    return path


def extract_and_copy_pyyaml_files(version, filename, build_dir='build'):
    extracted = Path(tempfile.gettempdir(), 'pyyaml-for-robot')
    if extracted.is_dir():
        shutil.rmtree(str(extracted))
    print(f"Extracting '{filename}' to '{extracted}'.")
    with tarfile.open(filename) as t:
        t.extractall(extracted)
    source = Path(extracted, f'PyYAML-{version}', 'lib', 'yaml')
    target = Path(build_dir, 'Lib', 'yaml')
    shutil.copytree(str(source), str(target),
                    ignore=shutil.ignore_patterns('*.pyc'))


def compile_java_files(ctx, jython_jar, build_dir='build'):
    root = Path('src/java/org/robotframework')
    files = [str(path) for path in root.iterdir() if path.suffix == '.java']
    print(f'Compiling {len(files)} Java files.')
    ctx.run(f"javac -d {build_dir} -target 8 -source 8 -cp {jython_jar} "
            f"{' '.join(files)}")


def unzip_jar(path, target='build'):
    zipfile.ZipFile(path).extractall(target)


def remove_tests(build_dir='build'):
    for test_dir in ('distutils/tests', 'email/test', 'json/tests',
                     'lib2to3/tests', 'unittest/test'):
        path = Path(build_dir, 'Lib', test_dir)
        if path.is_dir():
            shutil.rmtree(str(path))


def copy_robot_files(build_dir='build'):
    source = Path('src', 'robot')
    target = Path(build_dir, 'Lib', 'robot')
    shutil.copytree(str(source), str(target),
                    ignore=shutil.ignore_patterns('*.pyc'))
    shutil.rmtree(str(Path(target, 'htmldata', 'testdata')))


def compile_python_files(ctx, jython_jar, build_dir='build'):
    ctx.run(f"java -jar {jython_jar} -m compileall -x '.*3.py' {build_dir}")
    # Jython will not work without its py-files, but robot will
    for directory, _, files in os.walk(str(Path(build_dir, 'Lib', 'robot'))):
        for name in files:
            if name.endswith('.py'):
                Path(directory, name).unlink()


def create_robot_jar(ctx, version, name=None, source='build'):
    write_manifest(version, source)
    if not name:
        name = f'robotframework-{version}.jar'
    elif not name.endswith('.jar'):
        name += '.jar'
    # https://bugs.jython.org/issue2924
    offending_file = Path(source) / 'module-info.class'
    if offending_file.exists():
        offending_file.unlink()
    target = Path(f'dist/{name}')
    ctx.run(f'jar cvfM {target} -C {source} .')
    print(f"Created '{target}'.")


def write_manifest(version, build_dir='build'):
    with open(Path(build_dir, 'META-INF', 'MANIFEST.MF'), 'w') as mf:
        mf.write(f'''\
Manifest-Version: 1.0
Main-Class: org.robotframework.RobotFramework
Specification-Version: 2
Implementation-Version: {version}
''')
