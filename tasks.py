"""Tasks to help Robot Framework documentation hosting.

Executed by Invoke <http://pyinvoke.org>. Install it with `pip install invoke`
and run `invoke --help` and `invode --list` for details how to execute tasks.
"""

import os
import os.path

from invoke import task, run


def dryrun(command):
    print command

run = dryrun


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
    push_changes('Updated to version {}'.format(version))


@task
def copy_ug(version):
    """Copy User Guide from dist to correct location."""


@task
def extract_ug(version):
    """Extract User Guide package to 'x.y(.z)' directory."""


@task
def update_latest(version):
    """Update 'latest' directory to point to now latest 'x.y(.z)' directory."""


def update_index(version):
    """Add information about the new release index.html."""


@task
def push_changes(message, path='.'):
    """Commit and push changes."""
    run("git commit -m '{}' {}".format(message, path))
    run("git push")
