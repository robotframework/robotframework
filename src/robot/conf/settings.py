#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

import glob
import os
import random
import string
import sys
import time
import warnings

from robot.errors import DataError, FrameworkError
from robot.output import LOGGER, loggerhelper
from robot.result.keywordremover import KeywordRemover
from robot.result.flattenkeywordmatcher import validate_flatten_keyword
from robot.utils import (abspath, create_destination_directory, escape, format_time,
                         get_link_path, html_escape, is_list_like, plural_or_not as s,
                         seq2str, split_args_from_name_or_path)

from .gatherfailed import gather_failed_tests, gather_failed_suites


class _BaseSettings:
    _cli_opts = {'RPA'              : ('rpa', None),
                 'Name'             : ('name', None),
                 'Doc'              : ('doc', None),
                 'Metadata'         : ('metadata', []),
                 'TestNames'        : ('test', []),
                 'TaskNames'        : ('task', []),
                 'ReRunFailed'      : ('rerunfailed', 'NONE'),
                 'ReRunFailedSuites': ('rerunfailedsuites', 'NONE'),
                 'SuiteNames'       : ('suite', []),
                 'SetTag'           : ('settag', []),
                 'Include'          : ('include', []),
                 'Exclude'          : ('exclude', []),
                 'OutputDir'        : ('outputdir', abspath('.')),
                 'Log'              : ('log', 'log.html'),
                 'Report'           : ('report', 'report.html'),
                 'XUnit'            : ('xunit', None),
                 'SplitLog'         : ('splitlog', False),
                 'TimestampOutputs' : ('timestampoutputs', False),
                 'LogTitle'         : ('logtitle', None),
                 'ReportTitle'      : ('reporttitle', None),
                 'ReportBackground' : ('reportbackground',
                                       ('#9e9', '#f66', '#fed84f')),
                 'SuiteStatLevel'   : ('suitestatlevel', -1),
                 'TagStatInclude'   : ('tagstatinclude', []),
                 'TagStatExclude'   : ('tagstatexclude', []),
                 'TagStatCombine'   : ('tagstatcombine', []),
                 'TagDoc'           : ('tagdoc', []),
                 'TagStatLink'      : ('tagstatlink', []),
                 'RemoveKeywords'   : ('removekeywords', []),
                 'ExpandKeywords'   : ('expandkeywords', []),
                 'FlattenKeywords'  : ('flattenkeywords', []),
                 'PreRebotModifiers': ('prerebotmodifier', []),
                 'StatusRC'         : ('statusrc', True),
                 'ConsoleColors'    : ('consolecolors', 'AUTO'),
                 'PythonPath'       : ('pythonpath', []),
                 'StdOut'           : ('stdout', None),
                 'StdErr'           : ('stderr', None)}
    _output_opts = ['Output', 'Log', 'Report', 'XUnit', 'DebugFile']

    def __init__(self, options=None, **extra_options):
        self.start_timestamp = format_time(time.time(), '', '-', '')
        self._opts = {}
        self._cli_opts = self._cli_opts.copy()
        self._cli_opts.update(self._extra_cli_opts)
        self._process_cli_opts(dict(options or {}, **extra_options))

    def _process_cli_opts(self, opts):
        for name, (cli_name, default) in self._cli_opts.items():
            value = opts.pop(cli_name) if cli_name in opts else default
            if isinstance(default, list):
                # Copy mutable values and support list values as scalars.
                value = list(value) if is_list_like(value) else [value]
            self[name] = self._process_value(name, value)
        self['TestNames'] += self['ReRunFailed'] + self['TaskNames']
        self['SuiteNames'] += self['ReRunFailedSuites']
        if opts:
            raise DataError(f'Invalid option{s(opts)} {seq2str(opts)}.')

    def __setitem__(self, name, value):
        if name not in self._cli_opts:
            raise KeyError(f"Non-existing option '{name}'.")
        self._opts[name] = value

    def _process_value(self, name, value):
        if name == 'ReRunFailed':
            return gather_failed_tests(value)
        if name == 'ReRunFailedSuites':
            return gather_failed_suites(value)
        if name == 'LogLevel':
            return self._process_log_level(value)
        if value == self._get_default_value(name):
            return value
        if name == 'Doc':
            return self._process_doc(value)
        if name == 'Metadata':
            return [self._process_metadata(v) for v in value]
        if name == 'TagDoc':
            return [self._process_tagdoc(v) for v in value]
        if name in ['Include', 'Exclude']:
            return [self._format_tag_patterns(v) for v in value]
        if name in self._output_opts and (not value or value.upper() == 'NONE'):
            return None
        if name == 'OutputDir':
            return abspath(value)
        if name in ['SuiteStatLevel', 'ConsoleWidth']:
            return self._convert_to_positive_integer_or_default(name, value)
        if name == 'VariableFiles':
            return [split_args_from_name_or_path(item) for item in value]
        if name == 'ReportBackground':
            return self._process_report_background(value)
        if name == 'TagStatCombine':
            return [self._process_tag_stat_combine(v) for v in value]
        if name == 'TagStatLink':
            return [v for v in [self._process_tag_stat_link(v) for v in value] if v]
        if name == 'Randomize':
            return self._process_randomize_value(value)
        if name == 'MaxErrorLines':
            return self._process_max_error_lines(value)
        if name == 'MaxAssignLength':
            return self._process_max_assign_length(value)
        if name == 'PythonPath':
            return self._process_pythonpath(value)
        if name == 'RemoveKeywords':
            self._validate_remove_keywords(value)
        if name == 'FlattenKeywords':
            self._validate_flatten_keywords(value)
        if name == 'ExpandKeywords':
            self._validate_expandkeywords(value)
        if name == 'Extension':
            return tuple(ext.lower().lstrip('.') for ext in value.split(':'))
        return value

    def _process_doc(self, value):
        if os.path.exists(value) and value.strip() == value:
            try:
                with open(value) as f:
                    value = f.read()
            except (OSError, IOError) as err:
                self._raise_invalid('Doc', f"Reading documentation from '{value}' "
                                           f"failed: {err}")
        return self._escape_doc(value).strip()

    def _escape_doc(self, value):
        return value

    def _process_log_level(self, level):
        level, visible_level = self._split_log_level(level.upper())
        self._opts['VisibleLogLevel'] = visible_level
        return level

    def _split_log_level(self, level):
        if ':' in level:
            log_level, visible_level = level.split(':', 1)
        else:
            log_level = visible_level = level
        for level in log_level, visible_level:
            if level not in loggerhelper.LEVELS:
                self._raise_invalid('LogLevel', f"Invalid level '{level}'.")
        if not loggerhelper.IsLogged(log_level)(visible_level):
            self._raise_invalid('LogLevel', f"Level in log '{visible_level}' is lower "
                                            f"than execution level '{log_level}'.")
        return log_level, visible_level

    def _process_max_error_lines(self, value):
        if not value or value.upper() == 'NONE':
            return None
        value = self._convert_to_integer('MaxErrorLines', value)
        if value < 10:
            self._raise_invalid('MaxErrorLines',
                                f"Expected integer greater than 10, got {value}.")
        return value

    def _process_max_assign_length(self, value):
        value = self._convert_to_integer('MaxAssignLength', value)
        return max(value, 0)

    def _process_randomize_value(self, original):
        value = original.upper()
        if ':' in value:
            value, seed = value.split(':', 1)
        else:
            seed = random.randint(0, sys.maxsize)
        if value in ('TEST', 'SUITE'):
            value += 'S'
        valid = ('TESTS', 'SUITES', 'ALL', 'NONE')
        if value not in valid:
            valid = seq2str(valid, lastsep=' or ')
            self._raise_invalid('Randomize', f"Expected {valid}, got '{value}'.")
        try:
            seed = int(seed)
        except ValueError:
            self._raise_invalid('Randomize', f"Seed should be integer, got '{seed}'.")
        return value, seed

    def __getitem__(self, name):
        if name not in self._opts:
            raise KeyError(f"Non-existing option '{name}'.")
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
            LOGGER.error('Log file cannot be created if output.xml is disabled.')
            return None
        name = self._process_output_name(option, name)
        path = abspath(os.path.join(self['OutputDir'], name))
        create_destination_directory(path, f'{option.lower()} file')
        return path

    def _process_output_name(self, option, name):
        base, ext = os.path.splitext(name)
        if self['TimestampOutputs']:
            base = f'{base}-{self.start_timestamp}'
        ext = self._get_output_extension(ext, option)
        return base + ext

    def _get_output_extension(self, extension, file_type):
        if extension:
            return extension
        if file_type in ['Output', 'XUnit']:
            return '.xml'
        if file_type in ['Log', 'Report']:
            return '.html'
        if file_type == 'DebugFile':
            return '.txt'
        raise FrameworkError(f"Invalid output file type '{file_type}'.")

    def _process_metadata(self, value):
        name, value = self._split_from_colon(value)
        return name, self._process_doc(value)

    def _split_from_colon(self, value):
        if ':' in value:
            return value.split(':', 1)
        return value, ''

    def _process_tagdoc(self, value):
        return self._split_from_colon(value)

    def _process_report_background(self, colors):
        if colors.count(':') not in [1, 2]:
            self._raise_invalid('ReportBackground', f"Expected format 'pass:fail:skip' "
                                                    f"or 'pass:fail', got '{colors}'.")
        colors = colors.split(':')
        if len(colors) == 2:
            return colors[0], colors[1], '#fed84f'
        return tuple(colors)

    def _process_tag_stat_combine(self, pattern):
        if ':' in pattern:
            pattern, title = pattern.rsplit(':', 1)
        else:
            title = ''
        return self._format_tag_patterns(pattern), title

    def _format_tag_patterns(self, pattern):
        for search, replace in [('&', 'AND'), ('AND', ' AND '), ('OR', ' OR '),
                                ('NOT', ' NOT '), ('_', ' ')]:
            if search in pattern:
                pattern = pattern.replace(search, replace)
        while '  ' in pattern:
            pattern = pattern.replace('  ', ' ')
        if pattern.startswith(' NOT'):
            pattern = pattern[1:]
        return pattern

    def _process_tag_stat_link(self, value):
        tokens = value.split(':')
        if len(tokens) >= 3:
            return tokens[0], ':'.join(tokens[1:-1]), tokens[-1]
        self._raise_invalid('TagStatLink',
                            f"Expected format 'tag:link:title', got '{value}'.")

    def _convert_to_positive_integer_or_default(self, name, value):
        value = self._convert_to_integer(name, value)
        return value if value > 0 else self._get_default_value(name)

    def _convert_to_integer(self, name, value):
        try:
            return int(value)
        except ValueError:
            self._raise_invalid(name, f"Expected integer, got '{value}'.")

    def _get_default_value(self, name):
        return self._cli_opts[name][1]

    def _process_pythonpath(self, paths):
        return [os.path.abspath(globbed)
                for path in paths
                for split in self._split_pythonpath(path)
                for globbed in glob.glob(split) or [split]]

    def _split_pythonpath(self, path):
        path = path.replace('/', os.sep)
        if ';' in path:
            yield from path.split(';')
        elif os.sep == '/':
            yield from path.split(':')
        else:
            drive = ''
            for item in path.split(':'):
                if drive:
                    if item.startswith('\\'):
                        yield f'{drive}:{item}'
                        drive = ''
                        continue
                    yield drive
                    drive = ''
                if len(item) == 1 and item in string.ascii_letters:
                    drive = item
                else:
                    yield item
            if drive:
                yield drive

    def _validate_remove_keywords(self, values):
        for value in values:
            try:
                KeywordRemover(value)
            except DataError as err:
                self._raise_invalid('RemoveKeywords', err)

    def _validate_flatten_keywords(self, values):
        try:
            validate_flatten_keyword(values)
        except DataError as err:
            self._raise_invalid('FlattenKeywords', err)

    def _validate_expandkeywords(self, values):
        for opt in values:
            if not opt.lower().startswith(('name:', 'tag:')):
                self._raise_invalid('ExpandKeywords', f"Expected 'TAG:<pattern>' or "
                                                      f"'NAME:<pattern>', got '{opt}'.")

    def _raise_invalid(self, option, error):
        raise DataError(f"Invalid value for option '--{option.lower()}': {error}")

    def __contains__(self, setting):
        return setting in self._opts

    def __str__(self):
        return '\n'.join(f'{name}: {self._opts[name]}' for name in sorted(self._opts))

    @property
    def output_directory(self):
        return self['OutputDir']

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
    def log_level(self):
        return self['LogLevel']

    @property
    def split_log(self):
        return self['SplitLog']

    @property
    def suite_names(self):
        return self['SuiteNames']

    @property
    def include(self):
        return self['Include']

    @property
    def exclude(self):
        return self['Exclude']

    @property
    def pythonpath(self):
        return self['PythonPath']

    @property
    def status_rc(self):
        return self['StatusRC']

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
    def remove_keywords(self):
        return self['RemoveKeywords']

    @property
    def flatten_keywords(self):
        return self['FlattenKeywords']

    @property
    def pre_rebot_modifiers(self):
        return self['PreRebotModifiers']

    @property
    def console_colors(self):
        return self['ConsoleColors']

    @property
    def rpa(self):
        return self['RPA']

    @rpa.setter
    def rpa(self, value):
        self['RPA'] = value


class RobotSettings(_BaseSettings):
    _extra_cli_opts = {'Extension'          : ('extension', ('robot',)),
                       'Output'             : ('output', 'output.xml'),
                       'LogLevel'           : ('loglevel', 'INFO'),
                       'MaxErrorLines'      : ('maxerrorlines', 40),
                       'MaxAssignLength'    : ('maxassignlength', 200),
                       'DryRun'             : ('dryrun', False),
                       'ExitOnFailure'      : ('exitonfailure', False),
                       'ExitOnError'        : ('exitonerror', False),
                       'Skip'               : ('skip', []),
                       'SkipOnFailure'      : ('skiponfailure', []),
                       'SkipTeardownOnExit' : ('skipteardownonexit', False),
                       'Randomize'          : ('randomize', 'NONE'),
                       'RunEmptySuite'      : ('runemptysuite', False),
                       'Variables'          : ('variable', []),
                       'VariableFiles'      : ('variablefile', []),
                       'PreRunModifiers'    : ('prerunmodifier', []),
                       'Listeners'          : ('listener', []),
                       'ConsoleType'        : ('console', 'verbose'),
                       'ConsoleTypeDotted'  : ('dotted', False),
                       'ConsoleTypeQuiet'   : ('quiet', False),
                       'ConsoleWidth'       : ('consolewidth', 78),
                       'ConsoleMarkers'     : ('consolemarkers', 'AUTO'),
                       'DebugFile'          : ('debugfile', None)}

    def get_rebot_settings(self):
        settings = RebotSettings()
        settings.start_timestamp = self.start_timestamp
        not_copied = {'Include', 'Exclude', 'TestNames', 'SuiteNames', 'Name', 'Doc',
                      'Metadata', 'SetTag', 'Output', 'LogLevel', 'TimestampOutputs'}
        for opt in settings._opts:
            if opt in self and opt not in not_copied:
                settings._opts[opt] = self[opt]
        settings._opts['ProcessEmptySuite'] = self['RunEmptySuite']
        return settings

    def _output_disabled(self):
        return self.output is None

    def _escape_doc(self, value):
        return escape(value)

    @property
    def listeners(self):
        return self['Listeners']

    @property
    def debug_file(self):
        return self['DebugFile']

    @property
    def suite_config(self):
        return {
            'name': self['Name'],
            'doc': self['Doc'],
            'metadata': dict(self['Metadata']),
            'set_tags': self['SetTag'],
            'include_tags': self.include,
            'exclude_tags': self.exclude,
            'include_suites': self['SuiteNames'],
            'include_tests': self['TestNames'],
            'empty_suite_ok': self.run_empty_suite,
            'randomize_suites': self.randomize_suites,
            'randomize_tests': self.randomize_tests,
            'randomize_seed': self.randomize_seed,
        }

    @property
    def randomize_seed(self):
        return self['Randomize'][1]

    @property
    def randomize_suites(self):
        return self['Randomize'][0] in ('SUITES', 'ALL')

    @property
    def randomize_tests(self):
        return self['Randomize'][0] in ('TESTS', 'ALL')

    @property
    def dry_run(self):
        return self['DryRun']

    @property
    def exit_on_failure(self):
        return self['ExitOnFailure']

    @property
    def exit_on_error(self):
        return self['ExitOnError']

    @property
    def skip(self):
        return self['Skip']

    @property
    def skipped_tags(self):
        warnings.warn("'RobotSettings.skipped_tags' is deprecated. Use 'skip' instead.")
        return self.skip

    @property
    def skip_on_failure(self):
        return self['SkipOnFailure']

    @property
    def skip_teardown_on_exit(self):
        return self['SkipTeardownOnExit']

    @property
    def console_output_config(self):
        return {
            'type':    self.console_type,
            'width':   self.console_width,
            'colors':  self.console_colors,
            'markers': self.console_markers,
            'stdout':  self['StdOut'],
            'stderr':  self['StdErr']
        }

    @property
    def console_type(self):
        if self['ConsoleTypeQuiet']:
            return 'quiet'
        if self['ConsoleTypeDotted']:
            return 'dotted'
        return self['ConsoleType']

    @property
    def console_width(self):
        return self['ConsoleWidth']

    @property
    def console_markers(self):
        return self['ConsoleMarkers']

    @property
    def max_error_lines(self):
        return self['MaxErrorLines']

    @property
    def max_assign_length(self):
        return self['MaxAssignLength']

    @property
    def pre_run_modifiers(self):
        return self['PreRunModifiers']

    @property
    def run_empty_suite(self):
        return self['RunEmptySuite']

    @property
    def variables(self):
        return self['Variables']

    @property
    def variable_files(self):
        return self['VariableFiles']

    @property
    def extension(self):
        return self['Extension']


class RebotSettings(_BaseSettings):
    _extra_cli_opts = {'Output'            : ('output', None),
                       'LogLevel'          : ('loglevel', 'TRACE'),
                       'ProcessEmptySuite' : ('processemptysuite', False),
                       'StartTime'         : ('starttime', None),
                       'EndTime'           : ('endtime', None),
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
            'include_tags': self.include,
            'exclude_tags': self.exclude,
            'include_suites': self['SuiteNames'],
            'include_tests': self['TestNames'],
            'empty_suite_ok': self.process_empty_suite,
            'remove_keywords': self.remove_keywords,
            'log_level': self['LogLevel'],
            'start_time': self['StartTime'],
            'end_time': self['EndTime']
        }

    @property
    def log_config(self):
        if not self.log:
            return {}
        return {
            'rpa': self.rpa,
            'title': html_escape(self['LogTitle'] or ''),
            'reportURL': self._url_from_path(self.log, self.report),
            'splitLogBase': os.path.basename(os.path.splitext(self.log)[0]),
            'defaultLevel': self['VisibleLogLevel']
        }

    @property
    def report_config(self):
        if not self.report:
            return {}
        return {
            'rpa': self.rpa,
            'title': html_escape(self['ReportTitle'] or ''),
            'logURL': self._url_from_path(self.report, self.log),
            'background' : self._resolve_background_colors()
        }

    def _url_from_path(self, source, destination):
        if not destination:
            return None
        return get_link_path(destination, os.path.dirname(source))

    def _resolve_background_colors(self):
        colors = self['ReportBackground']
        return {'pass': colors[0], 'fail': colors[1], 'skip': colors[2]}

    @property
    def merge(self):
        return self['Merge']

    @property
    def console_output_config(self):
        return {
            'colors':  self.console_colors,
            'stdout':  self['StdOut'],
            'stderr':  self['StdErr']
        }

    @property
    def process_empty_suite(self):
        return self['ProcessEmptySuite']

    @property
    def expand_keywords(self):
        return self['ExpandKeywords']
