"""Tasks to help Robot Framework packaging and other development.

Executed by Invoke <http://pyinvoke.org>. Install it with `pip install invoke`
and run `invoke --help` and `invode --list` for details how to execute tasks.

See BUILD.rst for packaging and releasing instructions.
"""

from __future__ import print_function
import os
import re
import shutil
import sys
import tarfile
import tempfile
import time
import urllib
import zipfile

try:
    from invoke import task, __version_info__ as invoke_version

    if invoke_version < (0, 13):
        raise ImportError
except ImportError:
    sys.exit('invoke 0.13 or newer required. See BUILD.rst for details.')


assert os.getcwd() == os.path.dirname(os.path.abspath(__file__))


VERSION_RE = re.compile('^(((?:2|3)\.\d+)(\.\d+)?)((a|b|rc|.dev)(\d+))?$')
VERSION_FILE = os.path.join('src', 'robot', 'version.py')


@task
def tag_release(ctx, version):
    """Tag specified release.

    Updates version using `set_version`, creates tag, and pushes changes.
    """
    version = set_version(ctx, version, push=True)
    ctx.run("git tag -a {0} -m 'Release {0}'".format(version))
    ctx.run("git push --tags")


@task
def set_version(ctx, version, push=False):
    """Set version in `src/robot/version.py`.

    Version can have these values:
    - Actual version number to use. See below for supported formats.
    - String 'dev' to update version to latest development version
      (e.g. 2.8 -> 2.8.1.dev, 2.8.1 -> 2.8.2.dev, 2.8a1 -> 2.8.dev) with
      the current date added or updated.
    - String 'keep' to keep using the previously set version.

    Given version must be in one of these PEP-440 compatible formats:
    - Stable version in 'X.Y' or 'X.Y.Z' format (e.g. 2.8, 2.8.6)
    - Pre-releases with 'aN', 'bN' or 'rcN' postfix (e.g. 2.8a1, 2.8.6rc2)
    - Development releases with '.devYYYYMMDD' postfix (e.g. 2.8.6.dev20141001)
      or with '.dev' alone (e.g. 2.8.6.dev) in which case date is added
      automatically.

    Args:
        version:  Version to use. See above for supported values and formats.
        push:     Commit and push changes to the remote repository.
    """
    if version and version != 'keep':
        version = validate_version(version)
        write_version_file(version)
        write_pom_file(version)
    version = get_version_from_file()
    print('Version:', version)
    if push:
        git_commit(ctx, [VERSION_FILE, 'pom.xml'],
                   'Updated version to {}'.format(version), push=True)
    return version

def validate_version(version):
    if version == 'dev':
        version = get_dev_version()
    if version.endswith('.dev'):
        version += time.strftime('%Y%m%d')
    if not VERSION_RE.match(version):
        raise ValueError("Invalid version '{}'.".format(version))
    return version

def get_dev_version():
    previous = get_version_from_file()
    major, minor, pre = VERSION_RE.match(previous).groups()[1:4]
    if not pre:
        minor = '.{}'.format(int(minor[1:]) + 1 if minor else 1)
    if not minor:
        minor = ''
    return '{}{}.dev'.format(major, minor)

def write_version_file(version):
    update_file(VERSION_FILE, "VERSION = '.*'", version)

def write_pom_file(version):
    update_file('pom.xml', '<version>.*</version>', version)

def update_file(path, pattern, replacement):
    replacement = pattern.replace('.*', replacement )
    with open(path) as version_file:
        content = ''.join(re.sub(pattern, replacement, line)
                          for line in version_file)
    with open(path, 'w') as version_file:
        version_file.write(content)

def get_version_from_file():
    namespace = {}
    execfile(VERSION_FILE, namespace)
    return namespace['get_version']()

def git_commit(ctx, paths, message, push=False):
    paths = paths if isinstance(paths, basestring) else ' '.join(paths)
    ctx.run("git commit -m '{}' {}".format(message, paths))
    if push:
        ctx.run('git push')


@task
def clean(ctx, remove_dist=True, create_dirs=False):
    """Clean workspace.

    By default deletes 'build' and 'dist' directories and removes '*.pyc',
    '*$py.class' and '*~' files.

    Args:
        remove_dist:  Remove also 'dist' (default).
        create_dirs:  Re-create 'build' and 'dist' after removing them.
    """
    directories = ['build', 'dist']
    for name in directories:
        if os.path.isdir(name) and (name != 'dist' or remove_dist):
            shutil.rmtree(name)
        if create_dirs and not os.path.isdir(name):
            os.mkdir(name)
    for directory, dirs, files in os.walk('.'):
        for name in files:
            if name.endswith(('.pyc', '$py.class', '~')):
                os.remove(os.path.join(directory, name))
        if '__pycache__' in dirs:
            shutil.rmtree(os.path.join(directory, '__pycache__'))


@task
def sdist(ctx, deploy=False, remove_dist=False):
    """Create source distribution.

    Args:
        deploy:       Register and upload sdist to PyPI.
        remove_dist:  Control is 'dist' directory initially removed or not.
    """
    clean(ctx, remove_dist, create_dirs=True)
    ctx.run('python setup.py sdist --formats gztar,zip'
        + (' register upload' if deploy else ''))
    announce()

def announce():
    print()
    print('Distributions:')
    for name in os.listdir('dist'):
        print(os.path.join('dist', name))


@task
def jar(ctx, jython_version='2.7.0', pyyaml_version='3.11', remove_dist=False):
    """Create JAR distribution.

    Downloads Jython JAR and PyYAML if needed.

    Args:
        remove_dist:  Control is 'dist' directory initially removed or not.
        jython_version: Jython version to use as a base. Must match version in
            `jython-standalone-<version>.jar` found from Maven central.
        pyyaml_version: Version of PyYAML that will be included in the
            standalone jar. The version must be available from PyPI.
    """
    clean(ctx, remove_dist, create_dirs=True)
    jython_jar = get_jython_jar(jython_version)
    print('Using {0}'.format(jython_jar))
    compile_java_files(ctx, jython_jar)
    unzip_jar(jython_jar)
    copy_robot_files()
    pyaml_archive = get_pyyaml(pyyaml_version)
    extract_and_copy_pyyaml_files(pyyaml_version, pyaml_archive)
    compile_python_files(ctx, jython_jar)
    filename = create_robot_jar(ctx, get_version_from_file())
    announce()
    return os.path.abspath(filename)

def get_jython_jar(version):
    filename = 'jython-standalone-{0}.jar'.format(version)
    url = ('http://search.maven.org/remotecontent?filepath=org/python/'
           'jython-standalone/{0}/{1}').format(version, filename)
    return get_extlib_file(filename, url)

def get_pyyaml(version):
    filename = 'PyYAML-{0}.tar.gz'.format(version)
    url = 'https://pypi.python.org/packages/source/P/PyYAML/{0}'.format(filename)
    return get_extlib_file(filename, url)

def get_extlib_file(filename, url):
    lib = 'ext-lib'
    path = os.path.join(lib, filename)
    if os.path.exists(path):
        return path
    print('{0} not found, downloading it from {1}.'.format(filename, url))
    if not os.path.exists(lib):
        os.mkdir(lib)
    urllib.urlretrieve(url, path)
    return path

def extract_and_copy_pyyaml_files(version, filename, build_dir='build'):
    t = tarfile.open(filename)
    extracted = os.path.join(tempfile.gettempdir(), 'pyyaml-for-robot')
    if os.path.isdir(extracted):
        shutil.rmtree(extracted)
    print('Extracting {0} to {1}'.format(filename, extracted))
    t.extractall(extracted)
    source = os.path.join(extracted, 'PyYAML-{0}'.format(version), 'lib', 'yaml')
    target = os.path.join(build_dir, 'Lib', 'yaml')
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('*.pyc'))

def compile_java_files(ctx, jython_jar, build_dir='build'):
    root = os.path.join('src', 'java', 'org', 'robotframework')
    files = [os.path.join(root, name) for name in os.listdir(root)
             if name.endswith('.java')]
    print('Compiling {0} Java files.'.format(len(files)))
    ctx.run('javac -d {target} -target 1.7 -source 1.7 -cp {cp} {files}'.format(
        target=build_dir, cp=jython_jar, files=' '.join(files)))

def unzip_jar(path, target='build'):
    zipfile.ZipFile(path).extractall(target)

def copy_robot_files(build_dir='build'):
    source = os.path.join('src', 'robot')
    target = os.path.join(build_dir, 'Lib', 'robot')
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('*.pyc'))
    shutil.rmtree(os.path.join(target, 'htmldata', 'testdata'))

def compile_python_files(ctx, jython_jar, build_dir='build'):
    ctx.run("java -jar {0} -m compileall -x '.*3.py' {1}".format(jython_jar, build_dir))
    # Jython will not work without its py-files, but robot will
    for directory, _, files in os.walk(os.path.join(build_dir, 'Lib', 'robot')):
        for name in files:
            if name.endswith('.py'):
                os.remove(os.path.join(directory, name))

def create_robot_jar(ctx, version, source='build'):
    write_manifest(version, source)
    target = os.path.join('dist', 'robotframework-{0}.jar'.format(version))
    ctx.run('jar cvfM {0} -C {1} .'.format(target, source))
    return target

def write_manifest(version, build_dir='build'):
    with open(os.path.join(build_dir, 'META-INF', 'MANIFEST.MF'), 'w') as mf:
        mf.write('''\
Manifest-Version: 1.0
Main-Class: org.robotframework.RobotFramework
Specification-Version: 2
Implementation-Version: {version}
'''.format(version=version))
