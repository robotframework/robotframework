"""Tasks to help Robot Framework documentation hosting.

Executed by Invoke <http://pyinvoke.org>. Install it with `pip install invoke`
and run `invoke --help` and `invode --list` for details how to execute tasks.
"""

import os
import os.path
import shutil
import zipfile
import re

from invoke import task, run


def dryrun(command):
    print command



assert os.getcwd() == os.path.dirname(__file__)


@task(default=True)
def help():
    """Show help, basically an alias for --help.

    This task can be removed once the fix to this issue is released:
    https://github.com/pyinvoke/invoke/issues/180
    """
    run('invoke --help')


@task
def add_docs(version):
    """Add documentation of given version.

    Uses other tasks to do everything.
    """
    copy_ug(version)
    extract_ug(version)
    update_latest(version)
    update_index(version)
    push_changes(version)


@task
def copy_ug(version):
    """Copy User Guide from dist to correct location."""
    target = 'robotframework-userguide-{}.zip'.format(version)
    source = os.path.join('dist', target)
    print "Copying {} to {} ".format(source, target)
    shutil.copy(source, target)


@task
def extract_ug(version):
    """Extract User Guide package to 'x.y(.z)' directory."""
    basename = 'robotframework-userguide-{}'.format(version)
    source = '{}.zip'.format(basename)
    if os.path.isdir(version):
        print "Removing directory '{}'".format(version)
        shutil.rmtree(version)
    print "Extracting {}".format(source)
    zipfile.ZipFile(source).extractall()
    print "Renaming {} to {}".format(basename, version)
    os.rename(basename, version)


@task
def update_latest(version):
    """Update 'latest' directory to point to now latest 'x.y(.z)' directory."""
    print "Removing 'latest'"
    shutil.rmtree('latest')
    print "Copying '{}' to 'latest'".format(version)
    shutil.copytree(version, 'latest')


def update_index(version):
    """Add information about the new release index.html."""
    contents = []
    matcher = re.compile(r'(\s+)<option value="latest".+')
    with open('index.html', 'r') as original:
        contents = original.readlines()
    with open('index.html', 'w') as out:
        for row in contents:
            match = matcher.match(row)
            if match:
                out.write(row)
                out.write('{indent}<option value="{version}">{version}</option>\n'.format(indent=match.groups()[0], version=version))
            else:
                out.write(row)
    print "Updated 'index.html' with links to {}".format(version)


@task
def push_changes(version):
    """Commit and push changes."""
    print "\nRun the following commands:\n"
    print "git add {} index.html latest".format(version)
    print "git commit -m 'Updated to {}'".format(version)
    print "git push"
