#!/usr/bin/env python

"""Create release notes template based on issues on GitHub.

Usage: ./generate.py version [login] [password]

Template is written to the standard output. Redirect it to a file if needed.

Requires PyGithub <https://github.com/jacquev6/PyGithub>.
"""

import re
import sys
import time

from fnmatch import fnmatchcase

try:
    from github import Github
except ImportError:
    raise ImportError('Required PyGitHub module missing: pip install PyGithub')


VERSION_RE = re.compile('^((2\.\d+)(\.\d+)?)((a|b|rc|.dev)(\d+))?$')


class ReleaseNoteGenerator(object):
    repository = 'robotframework/robotframework'

    def __init__(self, stream=sys.stdout):
        self._stream = stream

    def generate(self, version, login=None, password=None):
        milestone, preview, preview_number = self._split_version(version)
        issues = self._get_issues(milestone, preview, preview_number, login,
                                  password)
        self._write_intro(version, milestone)
        self._write_most_important_enhancements(issues)
        self._write_backwards_incompatible_changes(issues)
        self._write_deprecated_features(issues)
        self._write_acknowledgements(issues)
        self._write_issue_table(issues, milestone, preview)
        self._write_targets(issues)

    def _split_version(self, version):
        match = VERSION_RE.match(version)
        if not match:
            raise ValueError("Invalid version '{}'.".format(version))
        milestone, _, _, _, preview, preview_number = match.groups()
        return milestone, preview, preview_number

    def _get_issues(self, milestone, preview, preview_number, login=None,
                    password=None):
        repo = Github(login_or_token=login,
                      password=password).get_repo(self.repository)
        milestone = self._get_milestone(repo, milestone)
        issues = [Issue(issue) for issue in repo.get_issues(milestone=milestone, state='all')]
        preview_matcher = PreviewMatcher(preview, preview_number)
        if preview_matcher:
            issues = [issue for issue in issues if preview_matcher.matches(issue.labels)]
        return sorted(issues)

    def _get_milestone(self, repo, milestone):
        for m in repo.get_milestones(state='all'):
            if m.title == milestone:
                return m
        raise ValueError("Milestone '{}' not found from repository '{}'!"
                         .format(milestone, repo.name))

    def _write_intro(self, version, milestone):
        self._write_header("Robot Framework {}".format(version), level=1)
        intro = '''
.. default-role:: code

Robot Framework {version} is a new release with **UPDATE** enhancements and bug
fixes. All issues targeted for RF {milestone} can be found from the `issue tracker
<https://github.com/robotframework/robotframework/issues?q=milestone%3A{milestone}>`_.

Questions and comments related to the release can be sent to the
`robotframework-users <http://groups.google.com/group/robotframework-users>`_
and possible bugs `submitted to the issue tracker
<https://github.com/robotframework/robotframework/issues>`__.

If you have `pip <http://pip-installer.org>`_ installed, just run
`pip install --upgrade robotframework` to install or upgrade to the latest
version or use `pip install robotframework=={version}` to install exactly
this version.  For more details and other installation approaches, see
`installation instructions <../../INSTALL.rst>`_.

Robot Framework {version} was released on **CHECK** {date}.

.. contents::
   :depth: 2
   :local:
'''.strip()
        self._write(intro, version=version, milestone=milestone,
                    date=time.strftime("%A %B %d, %Y"))

    def _write_most_important_enhancements(self, issues):
        self._write_issues_with_label('Most important enhancements',
                                      issues, 'prio-critical', 'prio-high')

    def _write_backwards_incompatible_changes(self, issues):
        self._write_issues_with_label('Backwards incompatible changes',
                                      issues, 'bwic')

    def _write_deprecated_features(self, issues):
        self._write_issues_with_label('Deprecated features', issues, 'depr')

    def _write_acknowledgements(self, issues):
        self._write_header('Acknowledgements')
        self._write('**UPDATE** based on AUTHORS.txt.')

    def _write_issue_table(self, issues, milestone, preview):
        self._write_header('Full list of fixes and enhancements')
        self._write('''
.. list-table::
    :header-rows: 1

    * - ID
      - Type
      - Priority
      - Summary
'''.strip())
        prefix1 = '    * - '
        prefix2 = '      - '
        if preview:
            self._write('      - Added')
        for issue in issues:
            self._write(prefix1 + issue.id)
            for item in (issue.type, issue.priority, issue.summary):
                self._write(prefix2 + item)
            if preview:
                self._write(prefix2 + issue.preview)
        self._write()
        self._write('Altogether {} issues. View on `issue tracker '
                    '<https://github.com/{}/issues?q=milestone%3A{}>`__.',
                    len(issues), self.repository, milestone)

    def _write_targets(self, issues):
        self._write()
        self._write('.. _User Guide: http://robotframework.org/robotframework/#user-guide')
        for issue in issues:
            self._write('.. _{}: https://github.com/robotframework/robotframework/issues/{}',
                        issue.id, issue.id[1:], link_issues=False)

    def _write_header(self, header, level=2):
        if level > 1:
            self._write()
        underline = {1: '=', 2: '=', 3: '-', 4: "~"}[level] * len(header)
        if level == 1:
            self._write(underline)
        self._write(header)
        self._write(underline, newlines=2)

    def _write_issues_with_label(self, header, issues, *labels):
        issues = [issue for issue in issues
                  if any(label in issue.labels for label in labels)]
        if not issues:
            return
        self._write_header(header)
        self._write('**EXPLAIN** or remove these.', newlines=2)
        for issue in issues:
            self._write('- {} {}', issue.id, issue.summary, newlines=0)
            if issue.preview:
                self._write(' ({})', issue.preview)
            else:
                self._write()

    def _write(self, message='', *args, **kwargs):
        message += ('\n' * kwargs.pop('newlines', 1))
        link_issues = kwargs.pop('link_issues', True)
        if args or kwargs:
            message = message.format(*args, **kwargs)
        if link_issues:
            message = re.sub(r'(#\d+)', r'`\1`_', message)
        self._stream.write(message)


class Issue(object):
    PRIORITIES = ['critical', 'high', 'medium', 'low', '']

    def __init__(self, issue):
        self.id = '#{}'.format(issue.number)
        self.summary = issue.title
        self.labels = [label.name for label in issue.get_labels()]
        self.type = self._get_label('bug', 'enhancement')
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
        return '%s [%s]' % (name, ''.join(str(i+1) for i in range(int(number))))

    def matches(self, labels):
        return any(fnmatchcase(l, p) for p in self._patterns for l in labels)

    def __nonzero__(self):
        return bool(self._patterns)


if __name__ == '__main__':
    generator = ReleaseNoteGenerator()
    try:
        generator.generate(*sys.argv[1:])
    except TypeError:
        sys.exit(__doc__)
