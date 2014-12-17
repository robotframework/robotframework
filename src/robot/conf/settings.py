#  Copyright 2008-2014 Nokia Solutions and Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import random
import sys
import time

from robot import utils
from robot.errors import DataError, FrameworkError
from robot.output import LOGGER, loggerhelper
from robot.result.keywordremover import KeywordRemover
from robot.result.flattenkeywordmatcher import FlattenKeywordMatcher

from .gatherfailed import gather_failed_tests


class _BaseSettings(object):
    _cli_opts = {'Name'             : ('name', None),
                 'Doc'              : ('doc', None),
                 'Metadata'         : ('metadata', []),
                 'TestNames'        : ('test', []),
                 'ReRunFailed'      : ('rerunfailed', 'NONE'),
                 'DeprecatedRunFailed': ('runfailed', 'NONE'),
                 'SuiteNames'       : ('suite', []),
                 'SetTag'           : ('settag', []),
                 'Include'          : ('include', []),
                 'Exclude'          : ('exclude', []),
                 'Critical'         : ('critical', None),
                 'NonCritical'      : ('noncritical', None),
                 'OutputDir'        : ('outputdir', utils.abspath('.')),
                 'Log'              : ('log', 'log.html'),
                 'Report'           : ('report', 'report.html'),
                 'XUnit'            : ('xunit', None),
                 'DeprecatedXUnit'  : ('xunitfile', None),
                 'SplitLog'         : ('splitlog', False),
                 'TimestampOutputs' : ('timestampoutputs', False),
                 'LogTitle'         : ('logtitle', None),
                 'ReportTitle'      : ('reporttitle', None),
                 'ReportBackground' : ('reportbackground',
                                       ('#99FF66', '#99FF66', '#FF3333')),
                 'SuiteStatLevel'   : ('suitestatlevel', -1),
                 'TagStatInclude'   : ('tagstatinclude', []),
                 'TagStatExclude'   : ('tagstatexclude', []),
                 'TagStatCombine'   : ('tagstatcombine', []),
                 'TagDoc'           : ('tagdoc', []),
                 'TagStatLink'      : ('tagstatlink', []),
                 'RemoveKeywords'   : ('removekeywords', []),
                 'FlattenKeywords'  : ('flattenkeywords', []),
                 'NoStatusRC'       : ('nostatusrc', False),
                 'MonitorColors'    : ('monitorcolors', 'AUTO'),
                 'StdOut'           : ('stdout', None),
                 'StdErr'           : ('stderr', None),
                 'XUnitSkipNonCritical' : ('xunitskipnoncritical', False)}
    _output_opts = ['Output', 'Log', 'Report', 'XUnit', 'DebugFile']

    def __init__(self, options=None, **extra_options):
        self.start_timestamp = utils.format_time(time.time(), '', '-', '')
        self._opts = {}
        self._cli_opts = self._cli_opts.copy()
        self._cli_opts.update(self._extra_cli_opts)
        self._process_cli_opts(dict(options or {}, **extra_options))

    def _process_cli_opts(self, opts):
        for name, (cli_name, default) in self._cli_opts.items():
            value = opts[cli_name] if cli_name in opts else default
            if default == [] and isinstance(value, basestring):
                value = [value]
            self[name] = self._process_value(name, value)
        self['TestNames'] += self['ReRunFailed'] or self['DeprecatedRunFailed']
        if self['DeprecatedXUnit']:
            self['XUnit'] = self['DeprecatedXUnit']

    def __setitem__(self, name, value):
        if name not in self._cli_opts:
            raise KeyError("Non-existing settings '%s'" % name)
        self._opts[name] = value

    def _process_value(self, name, value):
        if name in ['ReRunFailed', 'DeprecatedRunFailed']:
            return gather_failed_tests(value)
        if name == 'LogLevel':
            return self._process_log_level(value)
        if value == self._get_default_value(name):
            return value
        if name in ['Name', 'Doc', 'LogTitle', 'ReportTitle']:
            if name == 'Doc':
                value = self._escape_as_data(value)
            return value.replace('_', ' ')
        if name in ['Metadata', 'TagDoc']:
            if name == 'Metadata':
                value = [self._escape_as_data(v) for v in value]
            return [self._process_metadata_or_tagdoc(v) for v in value]
        if name in ['Include', 'Exclude']:
            return [self._format_tag_patterns(v) for v in value]
        if name in self._output_opts and (not value or value.upper() == 'NONE'):
            return None
        if name == 'DeprecatedXUnit':
            LOGGER.warn('Option --xunitfile is deprecated. Use --xunit instead.')
            return self._process_value('XUnit', value)
        if name == 'OutputDir':
            return utils.abspath(value)
        if name in ['SuiteStatLevel', 'MonitorWidth']:
            return self._convert_to_positive_integer_or_default(name, value)
        if name in ['Listeners', 'VariableFiles']:
            return [self._split_args_from_name_or_path(item) for item in value]
        if name == 'ReportBackground':
            return self._process_report_background(value)
        if name == 'TagStatCombine':
            return [self._process_tag_stat_combine(v) for v in value]
        if name == 'TagStatLink':
            return [v for v in [self._process_tag_stat_link(v) for v in value] if v]
        if name == 'Randomize':
            return self._process_randomize_value(value)
        if name == 'RunMode':
            LOGGER.warn('Option --runmode is deprecated in Robot Framework 2.8 '
                        'and will be removed in the future.')
            return [self._process_runmode_value(v) for v in value]
        if name == 'RemoveKeywords':
            self._validate_remove_keywords(value)
        if name == 'FlattenKeywords':
            self._validate_flatten_keywords(value)
        return value

    def _escape_as_data(self, value):
        return value

    def _process_log_level(self, level):
        level, visible_level = self._split_log_level(level.upper())
        self._opts['VisibleLogLevel'] = visible_level
        return level

    def _split_log_level(self, level):
        if ':' in level:
            level, visible_level = level.split(':', 1)
        else:
            visible_level = level
        self._validate_log_level_and_default(level, visible_level)
        return level, visible_level

    def _validate_log_level_and_default(self, log_level, default):
        if log_level not in loggerhelper.LEVELS:
            raise DataError("Invalid log level '%s'" % log_level)
        if default not in loggerhelper.LEVELS:
            raise DataError("Invalid log level '%s'" % default)
        if not loggerhelper.IsLogged(log_level)(default):
            raise DataError("Default visible log level '%s' is lower than "
                            "log level '%s'" % (default, log_level))

    def _process_randomize_value(self, original):
        value = original.lower()
        if ':' in value:
            value, seed = value.split(':', 1)
        else:
            seed = random.randint(0, sys.maxint)
        if value in ('test', 'suite'):
            value += 's'
        if value not in ('tests', 'suites', 'none', 'all'):
            self._raise_invalid_option_value('--randomize', original)
        try:
            seed = int(seed)
        except ValueError:
            self._raise_invalid_option_value('--randomize', original)
        return value, seed

    def _raise_invalid_option_value(self, option_name, given_value):
        raise DataError("Option '%s' does not support value '%s'."
                        % (option_name, given_value))

    def _process_runmode_value(self, original_value):
        formatted_value = original_value.lower()
        if formatted_value not in ('exitonfailure', 'skipteardownonexit',
                                   'dryrun', 'random:test', 'random:suite',
                                   'random:all'):
            self._raise_invalid_option_value('--runmode', original_value)
        return formatted_value

    def __getitem__(self, name):
        if name not in self._opts:
            raise KeyError("Non-existing setting '%s'" % name)
        if name in self._output_opts:
            return self._get_output_file(name)
        return self._opts[name]

    def _get_output_file(self, option):
        """Returns path of the requested output file and creates needed dirs.

        `option` can be 'Output', 'Log', 'Report', 'XUnit' or 'DebugFile'.
        """
        name = self._opts[option]
        if not name:
            return None
        if option == 'Log' and self._output_disabled():
            self['Log'] = None
            LOGGER.error('Log file is not created if output.xml is disabled.')
            return None
        name = self._process_output_name(option, name)
        path = utils.abspath(os.path.join(self['OutputDir'], name))
        self._create_output_dir(os.path.dirname(path), option)
        return path

    def _process_output_name(self, option, name):
        base, ext = os.path.splitext(name)
        if self['TimestampOutputs']:
            base = '%s-%s' % (base, self.start_timestamp)
        ext = self._get_output_extension(ext, option)
        return base + ext

    def _get_output_extension(self, ext, type_):
        if ext != '':
            return ext
        if type_ in ['Output', 'XUnit']:
            return '.xml'
        if type_ in ['Log', 'Report']:
            return '.html'
        if type_ == 'DebugFile':
            return '.txt'
        raise FrameworkError("Invalid output file type: %s" % type_)

    def _create_output_dir(self, path, type_):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except EnvironmentError, err:
            raise DataError("Creating %s file directory '%s' failed: %s"
                            % (type_.lower(), path, err.strerror))

    def _process_metadata_or_tagdoc(self, value):
        value = value.replace('_', ' ')
        if ':' in value:
            return value.split(':', 1)
        return value, ''

    def _process_report_background(self, colors):
        if colors.count(':') not in [1, 2]:
            raise DataError("Invalid report background colors '%s'." % colors)
        colors = colors.split(':')
        if len(colors) == 2:
            return colors[0], colors[0], colors[1]
        return tuple(colors)

    def _process_tag_stat_combine(self, pattern):
        if ':' in pattern:
            pattern, title = pattern.rsplit(':', 1)
        else:
            title = ''
        return self._format_tag_patterns(pattern), title.replace('_', ' ')

    def _format_tag_patterns(self, pattern):
        for search, replace in [('&', 'AND'), ('AND', ' AND '), ('OR', ' OR '),
                                ('NOT', ' NOT '), ('_', ' ')]:
            if search in pattern:
                pattern = pattern.replace(search, replace)
        while '  ' in pattern:
            pattern = pattern.replace('  ', ' ')
        return pattern

    def _process_tag_stat_link(self, value):
        tokens = value.split(':')
        if len(tokens) >= 3:
            return tokens[0], ':'.join(tokens[1:-1]), tokens[-1]
        raise DataError("Invalid format for option '--tagstatlink'. "
                        "Expected 'tag:link:title' but got '%s'." % value)

    def _convert_to_positive_integer_or_default(self, name, value):
        value = self._convert_to_integer(name, value)
        return value if value > 0 else self._get_default_value(name)

    def _convert_to_integer(self, name, value):
        try:
            return int(value)
        except ValueError:
            raise DataError("Option '--%s' expected integer value but got '%s'."
                            % (name.lower(), value))

    def _get_default_value(self, name):
        return self._cli_opts[name][1]

    def _split_args_from_name_or_path(self, name):
        if os.path.exists(name):
            return os.path.abspath(name), []
        index = self._get_arg_separator_index_from_name_or_path(name)
        if index == -1:
            return name, []
        args = name[index+1:].split(name[index])
        name = name[:index]
        if os.path.exists(name):
            name = os.path.abspath(name)
        return name, args

    def _get_arg_separator_index_from_name_or_path(self, name):
        colon_index = name.find(':')
        # Handle absolute Windows paths
        if colon_index == 1 and name[2:3] in ('/', '\\'):
            colon_index = name.find(':', colon_index+1)
        semicolon_index = name.find(';')
        if colon_index == -1:
            return semicolon_index
        if semicolon_index == -1:
            return colon_index
        return min(colon_index, semicolon_index)

    def _validate_remove_keywords(self, values):
        for value in values:
            try:
                KeywordRemover(value)
            except DataError, err:
                raise DataError("Invalid value for option '--removekeywords'. %s" % err)

    def _validate_flatten_keywords(self, values):
        for value in values:
            try:
                FlattenKeywordMatcher(value)
            except DataError, err:
                raise DataError("Invalid value for option '--flattenkeywords'. %s" % err)

    def __contains__(self, setting):
        return setting in self._cli_opts

    def __unicode__(self):
        return '\n'.join('%s: %s' % (name, self._opts[name])
                         for name in sorted(self._opts))

    @property
    def output(self):
        return self['Output']

    @property
    def log(self):
        return self['Log']

    @property
    def report(self):
        return self['Report']

    @property
    def xunit(self):
        return self['XUnit']

    @property
    def split_log(self):
        return self['SplitLog']

    @property
    def status_rc(self):
        return not self['NoStatusRC']

    @property
    def xunit_skip_noncritical(self):
        return self['XUnitSkipNonCritical']

    @property
    def statistics_config(self):
        return {
            'suite_stat_level': self['SuiteStatLevel'],
            'tag_stat_include': self['TagStatInclude'],
            'tag_stat_exclude': self['TagStatExclude'],
            'tag_stat_combine': self['TagStatCombine'],
            'tag_stat_link': self['TagStatLink'],
            'tag_doc': self['TagDoc'],
        }

    @property
    def critical_tags(self):
        return self['Critical']

    @property
    def non_critical_tags(self):
        return self['NonCritical']

    @property
    def remove_keywords(self):
        return self['RemoveKeywords']

    @property
    def flatten_keywords(self):
        return self['FlattenKeywords']


class RobotSettings(_BaseSettings):
    _extra_cli_opts = {'Output'             : ('output', 'output.xml'),
                       'LogLevel'           : ('loglevel', 'INFO'),
                       'DryRun'             : ('dryrun', False),
                       'ExitOnFailure'      : ('exitonfailure', False),
                       'ExitOnError'        : ('exitonerror', False),
                       'SkipTeardownOnExit' : ('skipteardownonexit', False),
                       'Randomize'          : ('randomize', 'NONE'),
                       'RunMode'            : ('runmode', []),
                       'RunEmptySuite'      : ('runemptysuite', False),
                       'WarnOnSkipped'      : ('warnonskippedfiles', False),
                       'Variables'          : ('variable', []),
                       'VariableFiles'      : ('variablefile', []),
                       'Listeners'          : ('listener', []),
                       'MonitorWidth'       : ('monitorwidth', 78),
                       'MonitorMarkers'     : ('monitormarkers', 'AUTO'),
                       'DebugFile'          : ('debugfile', None)}

    def get_rebot_settings(self):
        settings = RebotSettings()
        settings._opts.update(self._opts)
        for name in ['Variables', 'VariableFiles', 'Listeners']:
            del(settings._opts[name])
        for name in ['Include', 'Exclude', 'TestNames', 'SuiteNames', 'Metadata']:
            settings._opts[name] = []
        for name in ['Name', 'Doc']:
            settings._opts[name] = None
        settings._opts['Output'] = None
        settings._opts['LogLevel'] = 'TRACE'
        settings._opts['ProcessEmptySuite'] = self['RunEmptySuite']
        return settings

    def _output_disabled(self):
        return self.output is None

    def _escape_as_data(self, value):
        return utils.escape(value)

    @property
    def suite_config(self):
        return {
            'name': self['Name'],
            'doc': self['Doc'],
            'metadata': dict(self['Metadata']),
            'set_tags': self['SetTag'],
            'include_tags': self['Include'],
            'exclude_tags': self['Exclude'],
            'include_suites': self['SuiteNames'],
            'include_tests': self['TestNames'],
            'empty_suite_ok': self['RunEmptySuite'],
            'randomize_suites': self.randomize_suites,
            'randomize_tests': self.randomize_tests,
            'randomize_seed': self.randomize_seed,
        }

    @property
    def randomize_seed(self):
        return self['Randomize'][1]

    @property
    def randomize_suites(self):
        return (self['Randomize'][0] in ('suites', 'all') or
                any(mode in ('random:suite', 'random:all') for mode in self['RunMode']))

    @property
    def randomize_tests(self):
        return (self['Randomize'][0] in ('tests', 'all') or
                any(mode in ('random:test', 'random:all') for mode in self['RunMode']))

    @property
    def dry_run(self):
        return (self['DryRun'] or
                any(mode == 'dryrun' for mode in self['RunMode']))

    @property
    def exit_on_failure(self):
        return (self['ExitOnFailure'] or
                any(mode == 'exitonfailure' for mode in self['RunMode']))

    @property
    def exit_on_error(self):
        return self['ExitOnError']

    @property
    def skip_teardown_on_exit(self):
        return (self['SkipTeardownOnExit'] or
                any(mode == 'skipteardownonexit' for mode in self['RunMode']))

    @property
    def log_level(self):
        return self['LogLevel']

    @property
    def console_logger_config(self):
        return {
            'width':   self['MonitorWidth'],
            'colors':  self['MonitorColors'],
            'markers': self['MonitorMarkers'],
            'stdout':  self['StdOut'],
            'stderr':  self['StdErr']
        }


class RebotSettings(_BaseSettings):
    _extra_cli_opts = {'Output'            : ('output', None),
                       'LogLevel'          : ('loglevel', 'TRACE'),
                       'ProcessEmptySuite' : ('processemptysuite', False),
                       'StartTime'         : ('starttime', None),
                       'EndTime'           : ('endtime', None),
                       'ReRunMerge'        : ('rerunmerge', False),
                       'Merge'             : ('merge', False)}

    def _output_disabled(self):
        return False

    @property
    def suite_config(self):
        return {
            'name': self['Name'],
            'doc': self['Doc'],
            'metadata': dict(self['Metadata']),
            'set_tags': self['SetTag'],
            'include_tags': self['Include'],
            'exclude_tags': self['Exclude'],
            'include_suites': self['SuiteNames'],
            'include_tests': self['TestNames'],
            'empty_suite_ok': self['ProcessEmptySuite'],
            'remove_keywords': self.remove_keywords,
            'log_level': self['LogLevel'],
            'critical_tags': self.critical_tags,
            'non_critical_tags': self.non_critical_tags,
            'start_time': self['StartTime'],
            'end_time': self['EndTime']
        }

    @property
    def log_config(self):
        if not self.log:
            return {}
        return {
            'title': utils.html_escape(self['LogTitle'] or ''),
            'reportURL': self._url_from_path(self.log, self.report),
            'splitLogBase': os.path.basename(os.path.splitext(self.log)[0]),
            'defaultLevel': self['VisibleLogLevel']
        }

    @property
    def report_config(self):
        if not self.report:
            return {}
        return {
            'title': utils.html_escape(self['ReportTitle'] or ''),
            'logURL': self._url_from_path(self.report, self.log),
            'background' : self._resolve_background_colors(),
        }

    def _url_from_path(self, source, destination):
        if not destination:
            return None
        return utils.get_link_path(destination, os.path.dirname(source))

    def _resolve_background_colors(self):
        colors = self['ReportBackground']
        return {'pass': colors[0], 'nonCriticalFail': colors[1], 'fail': colors[2]}

    @property
    def merge(self):
        return self['Merge'] or self['ReRunMerge']

    @property
    def console_logger_config(self):
        return {
            'colors':  self['MonitorColors'],
            'stdout':  self['StdOut'],
            'stderr':  self['StdErr']
        }
