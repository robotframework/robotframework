"""Tasks to help Robot Framework packaging and other development.

Executed by Invoke <http://pyinvoke.org>. Install it with `pip install invoke`
and run `invoke --help` and `invode --list` for details how to execute tasks.

See BUILD.rst for packaging and releasing instructions.
"""

import os
import os.path
import re
import shutil
import sys
import time
import urllib
import zipfile

from fnmatch import fnmatchcase
from invoke import task, run


assert os.getcwd() == os.path.dirname(os.path.abspath(__file__))

VERSION_RE = re.compile('^((2\.\d+)(\.\d+)?)((a|b|rc|.dev)(\d+))?$')
VERSION_FILE = os.path.join('src', 'robot', 'version.py')


@task(default=True)
def help():
    """Show help, basically an alias for --help.

    This task can be removed once the fix to this issue is released:
    https://github.com/pyinvoke/invoke/issues/180
    """
    run('invoke --help')


@task
def tag_release(version):
    """Tag specified release.

    Updates version using `set_version`, creates tag, and pushes changes.
    """
    version = set_version(version, push=True)
    run("git tag -a {0} -m 'Release {0}'".format(version))
    run("git push --tags")


@task
def set_version(version, push=False):
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
    print 'Version:', version
    if push:
        git_commit([VERSION_FILE, 'pom.xml'],
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

def git_commit(paths, message, push=False):
    paths = paths if isinstance(paths, basestring) else ' '.join(paths)
    run("git commit -m '{}' {}".format(message, paths))
    if push:
        run('git push')


@task
def clean(remove_dist=True, create_dirs=False):
    """Clean workspace.

    By default deletes 'build' and 'dist' directories and removes '*.pyc'
    and '$py.class' files.

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
    for directory, _, files in os.walk('.'):
        for name in files:
            if name.endswith(('.pyc', '$py.class')):
                os.remove(os.path.join(directory, name))


@task
def sdist(deploy=False, remove_dist=False):
    """Create source distribution.

    Args:
        deploy:       Register and upload sdist to PyPI.
        remove_dist:  Control is 'dist' directory initially removed or not.
    """
    clean(remove_dist, create_dirs=True)
    run('python setup.py sdist --force-manifest'
        + (' register upload' if deploy else ''))
    announce()

def announce():
    print
    print 'Distributions:'
    for name in os.listdir('dist'):
        print os.path.join('dist', name)


@task
def wininst(remove_dist=False):
    """Create Windows installer.

    Args:
        remove_dist:  Control is 'dist' directory initially removed or not.
    """
    clean(remove_dist, create_dirs=True)
    run('python setup.py bdist_wininst '
        '--bitmap robot.bmp --install-script robot_postinstall.py')
    announce()


@task
def jar(jython_version='2.7.0', remove_dist=False):
    """Create JAR distribution.

    Downloads Jython JAR if needed.

    Args:
        remove_dist:  Control is 'dist' directory initially removed or not.
        jython_version: Jython version to use as a base. Must match version in
            `jython-standalone-<version>.jar` found from Maven central.
            Currently `2.7.0` by default.
    """
    clean(remove_dist, create_dirs=True)
    jython_jar = get_jython_jar(jython_version)
    print 'Using {}'.format(jython_jar)
    compile_java_files(jython_jar)
    unzip_jar(jython_jar)
    copy_robot_files()
    compile_python_files(jython_jar)
    create_robot_jar(get_version_from_file())
    announce()

def get_jython_jar(version):
    lib = 'ext-lib'
    jar = os.path.join(lib, 'jython-standalone-{}.jar'.format(version))
    if os.path.exists(jar):
        return jar
    url = ('http://search.maven.org/remotecontent?filepath=org/python/'
           'jython-standalone/{0}/jython-standalone-{0}.jar').format(version)
    print 'Jython not found, downloading it from {}.'.format(url)
    if not os.path.exists(lib):
        os.mkdir(lib)
    urllib.urlretrieve(url, jar)
    return jar

def compile_java_files(jython_jar, build_dir='build'):
    root = os.path.join('src', 'java', 'org', 'robotframework')
    files = [os.path.join(root, name) for name in os.listdir(root)
             if name.endswith('.java')]
    print 'Compiling {} Java files.'.format(len(files))
    run('javac -d {target} -target 1.5 -source 1.5 -cp {cp} {files}'.format(
        target=build_dir, cp=jython_jar, files=' '.join(files)))

def unzip_jar(path, target='build'):
    zipfile.ZipFile(path).extractall(target)

def copy_robot_files(build_dir='build'):
    source = os.path.join('src', 'robot')
    target = os.path.join(build_dir, 'Lib', 'robot')
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('*.pyc'))
    shutil.rmtree(os.path.join(target, 'htmldata', 'testdata'))

def compile_python_files(jython_jar, build_dir='build'):
    run('java -jar {} -m compileall {}'.format(jython_jar, build_dir))
    # Jython will not work without its py-files, but robot will
    for directory, _, files in os.walk(os.path.join(build_dir, 'Lib', 'robot')):
        for name in files:
            if name.endswith('.py'):
                os.remove(os.path.join(directory, name))

def create_robot_jar(version, source='build'):
    write_manifest(version, source)
    target = os.path.join('dist', 'robotframework-{}.jar'.format(version))
    run('jar cvfM {} -C {} .'.format(target, source))

def write_manifest(version, build_dir='build'):
    with open(os.path.join(build_dir, 'META-INF', 'MANIFEST.MF'), 'w') as mf:
        mf.write('''\
Manifest-Version: 1.0
Main-Class: org.robotframework.RobotFramework
Specification-Version: 2
Implementation-Version: {version}
'''.format(version=version))


@task
def release_notes(version=get_version_from_file(), login=None, password=None):
    """Create release notes template based on issues on GitHub.

    Requires PyGithub <https://github.com/jacquev6/PyGithub>. Install it with:
        pip install PyGithub

    Args:
        version:  Version to get the issues for. By default the current version.
        login:    GitHub login. If not given, anonymous login is used. GitHub
                  API has 60 request/hour limit in that case.
        password: The password for GitHub login.
    """
    milestone, preview, preview_number = _split_version(version)
    issues = _get_issues(milestone, preview, preview_number, login, password)
    _print_header("Robot Framework {}".format(version), level=1)
    _print_intro(version)
    _print_if_label("Most important enhancements", issues, "prio-critical", "prio-high")
    _print_if_label("Backwards incompatible changes", issues, "bwic")
    _print_if_label("Deprecated features", issues, "depr")
    _print_header("Acknowledgements")
    print("*UPDATE* based on AUTHORS.txt.")
    _print_issue_table(issues, version, preview)

def _split_version(version):
    match = VERSION_RE.match(version)
    if not match:
        raise ValueError("Invalid version '{}'".format(version))
    milestone, _, _, _, preview, preview_number = match.groups()
    return milestone, preview, preview_number

def _get_issues(milestone, preview, preview_number, login=None, password=None):
    try:
        from github import Github
    except ImportError:
        sys.exit("You need to install PyGithub:\n\tpip install PyGithub\n")
    repo = Github(login_or_token=login, password=password).get_repo("robotframework/robotframework")
    issues = [Issue(issue) for issue in repo.get_issues(milestone=_get_milestone(repo, milestone), state="all")]
    preview_matcher = PreviewMatcher(preview, preview_number)
    if preview_matcher:
        issues = [issue for issue in issues if preview_matcher.matches(issue.labels)]
    return sorted(issues)

def _get_milestone(repo, milestone):
    for m in repo.get_milestones(state="all"):
        if m.title == milestone:
            return m
    raise AssertionError("Milestone {} not found from repository {}!".format(milestone, repo.name))

def _print_header(header, level=2):
    if level > 1:
        print
    print "{} {}\n".format('#'*level, header)

def _print_if_label(header, issues, *labels):
    filtered = [issue for issue in issues
                if any(label in issue.labels for label in labels)]
    if filtered:
        _print_header(header)
        print '*EXPLAIN* or remove these.\n'
        for issue in filtered:
            print "* {} {}".format(issue.id, issue.summary),
            print " ({})".format(issue.preview) if issue.preview else ""

def _print_intro(version):
    print """
Robot Framework {version} is a new release with *UPDATE* \
enhancements and bug fixes. It was released on {date}.

Questions and comments related to the release can be sent to the \
[robotframework-users](http://groups.google.com/group/robotframework-users) and \
possible bugs submitted to the \
[issue tracker](https://github.com/robotframework/robotframework/issues).

If you have pip just run `pip install --update robotframework`. Otherwise see \
[installation instructions](https://github.com/robotframework/robotframework/blob/master/INSTALL.rst).
""".format(version=version, date=time.strftime("%A %B %d, %Y")).strip()

def _print_issue_table(issues, version, preview):
    _print_header("Full list of fixes and enhancements")
    print "ID  | Type | Priority | Summary" + (" | Added&nbsp;In" if preview else "")
    print "--- | ---- | -------- | -------" + (" | --------" if preview else "")
    for issue in issues:
        info = [issue.id, issue.type, issue.priority, issue.summary]
        if preview:
            info.append(issue.preview)
        print " | ".join(info)
    print
    print "Altogether {} issues.".format(len(issues)),
    version = VERSION_RE.match(version).group(1)
    print "See on [issue tracker](https://github.com/robotframework/robotframework/issues?q=milestone%3A{}).".format(version)


@task
def print_issues(version=get_version_from_file(), login=None, password=None):
    """Get issues from GitHub issue tracker.

    Requires PyGithub <https://github.com/jacquev6/PyGithub>. Install it with:
        pip install PyGithub

    Args:
        version:  Version to get the issues for. By default the current version.
        login:    GitHub login. If not given, anonymous login is used. GitHub
                  API has 60 request/hour limit in that case.
        password: The password for GitHub login.
    """
    issues = _get_issues(version, login, password)
    print "{:5}  {:11}  {:8}  {}".format("id", "type", "priority", "summary")
    for issue in issues:
        print "{:5}  {:11}  {:8}  {}".format(issue.id, issue.type, issue.priority, issue.summary)


class Issue(object):
    PRIORITIES = ["critical", "high", "medium", "low", ""]

    def __init__(self, issue):
        self.id = "#{}".format(issue.number)
        self.summary = issue.title
        self.labels = [label.name for label in issue.get_labels()]
        self.type = self._get_label("bug", "enhancement")
        self.priority = self._get_priority()

    def _get_label(self, *values):
        for value in values:
            if value in self.labels:
                return value
        return None

    def _get_priority(self):
        labels = ['prio-' + p for p in self.PRIORITIES if p]
        priority = self._get_label(*labels)
        return priority.split('-')[1] if priority else ''

    def __cmp__(self, other):
        return cmp(self.order, other.order)

    @property
    def order(self):
        return (self.PRIORITIES.index(self.priority),
                0 if self.type == 'bug' else 1,
                self.id)

    @property
    def preview(self):
        for label in self.labels:
            if label.startswith(('alpha ', 'beta ', 'rc ')):
                return label
        return ''


class PreviewMatcher(object):

    def __init__(self, preview, number):
        self._patterns = self._get_patterns(preview, number)

    def _get_patterns(self, preview, number):
        if not preview:
            return ()
        return {'a': (self._range('alpha', number),),
                'b': ('alpha ?', self._range('beta', number)),
                'rc': ('alpha ?', 'beta ?', self._range('rc', number))}[preview]

    def _range(self, name, number):
        return '%s [%s]' % (name, ''.join(str(i) for i in range(1, int(number)+1)))

    def matches(self, labels):
        return any(fnmatchcase(l, p) for p in self._patterns for l in labels)

    def __nonzero__(self):
        return bool(self._patterns)
