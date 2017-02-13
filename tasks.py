"""Tasks to help Robot Framework documentation hosting.

Executed by Invoke <http://pyinvoke.org>. Install it with `pip install invoke`
and run `invoke --help` and `invode --list` for details how to execute tasks.
"""

from __future__ import print_function
import os
import os.path
import shutil
import zipfile
import re

from invoke import task


assert os.getcwd() == os.path.dirname(__file__)


@task
def add_docs(ctx, version, push=False):
    """Add documentation of given version.

    Uses other tasks to do everything.

    Args:
        version:   Version of userguide. Must be precompiled in dist.
        push:      Whether to push changes to git. Defaults to False.
    """
    copy_ug(version)
    extract_ug(version)
    if not is_preview(version):
        update_latest(version)
    update_index(version)
    add_changes(ctx, version)
    if push:
        push_changes(ctx, version)


def is_preview(version):
    return any(c not in '1234567890.' for c in version)


def copy_ug(version):
    """Copy User Guide from dist to correct location."""
    target = 'robotframework-userguide-{}.zip'.format(version)
    source = os.path.join('dist', target)
    print("Copying {} to {} ".format(source, target))
    shutil.copy(source, target)


def extract_ug(version):
    """Extract User Guide package to 'x.y(.z)' directory."""
    basename = 'robotframework-userguide-{}'.format(version)
    source = '{}.zip'.format(basename)
    if os.path.isdir(version):
        print("Removing directory '{}'".format(version))
        shutil.rmtree(version)
    print("Extracting {}".format(source))
    zipfile.ZipFile(source).extractall()
    print("Renaming {} to {}".format(basename, version))
    os.rename(basename, version)


def update_latest(version):
    """Update 'latest' directory to point to now latest 'x.y(.z)' directory."""
    print("Removing 'latest'")
    shutil.rmtree('latest')
    print("Copying '{}' to 'latest'".format(version))
    shutil.copytree(version, 'latest')
    print("Removing 'robotframework-userguide-latest.zip'")
    os.remove('robotframework-userguide-latest.zip')
    print("Copying 'robotframework-userguide-{}.zip' to "
          "'robotframework-userguide-latest.zip'".format(version))
    shutil.copy('robotframework-userguide-{}.zip'.format(version),
                'robotframework-userguide-latest.zip')


def update_index(version):
    """Add information about the new release index.html."""
    preview_matcher = re.compile(r'(\s+)<option class="preview".+')
    latest_matcher = re.compile(r'(\s+)<option value="latest".+')
    preview = is_preview(version)
    with open('index.html', 'r') as original:
        contents = original.readlines()
    with open('index.html', 'w') as out:
        for row in contents:
            if preview_matcher.match(row):
                continue
            match = latest_matcher.match(row)
            if match:
                if preview:
                    out.write('{indent}<option class="preview" value="{version}">{version}</option>\n'
                              .format(indent=match.groups()[0], version=version))
                out.write(row)
                if not preview:
                    out.write('{indent}<option value="{version}">{version}</option>\n'
                              .format(indent=match.groups()[0], version=version))
            else:
                out.write(row)
    print("Updated 'index.html' with links to {}".format(version))


def add_changes(ctx, version):
    """Adds changes to git."""
    print("Staging files to git.")
    ctx.run("git add {0} robotframework-userguide-{0}.zip index.html latest "
            "robotframework-userguide-latest.zip".format(version))


def push_changes(ctx, version):
    """Commit and push changes."""
    print("Pushing changes to gh-pages.")
    ctx.run("git commit -m 'Updated to {}'".format(version))
    ctx.run("git push")
