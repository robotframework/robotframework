#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

from robot import utils
from robot.errors import DataError, FrameworkError
from robot.output import LOGGER, loggerhelper


class _BaseSettings(object):
    _cli_opts = {'Name'             : ('name', None),
                 'Doc'              : ('doc', None),
                 'Metadata'         : ('metadata', []),
                 'TestNames'        : ('test', []),
                 'SuiteNames'       : ('suite', []),
                 'SetTag'           : ('settag', []),
                 'Include'          : ('include', []),
                 'Exclude'          : ('exclude', []),
                 'Critical'         : ('critical', None),
                 'NonCritical'      : ('noncritical', None),
                 'OutputDir'        : ('outputdir', utils.abspath('.')),
                 'Log'              : ('log', 'log.html'),
                 'Report'           : ('report', 'report.html'),
                 'XUnitFile'        : ('xunitfile', 'NONE'),
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
                 'NoStatusRC'       : ('nostatusrc', False),
                 'MonitorColors'    : ('monitorcolors', 'AUTO'),
                 'StdOut'           : ('stdout', None),
                 'StdErr'           : ('stderr', None)}
    _output_opts = ['Output', 'Log', 'Report', 'DebugFile', 'XUnitFile']

    def __init__(self, options=None, log=True):
        self._opts = {}
        self._cli_opts = self._cli_opts.copy()
        self._cli_opts.update(self._extra_cli_opts)
        self._process_cli_opts(options or {}, log)
        if log: LOGGER.info('Settings:\n%s' % unicode(self))

    def _process_cli_opts(self, opts, log):
        for name, (cli_name, default) in self._cli_opts.items():
            value = opts.get(cli_name, default)
            if value in [None, []]:
                value = default
            elif default == [] and isinstance(value, basestring):
                value = [value]
            self[name] = self._process_value(name, value, log)

    def __setitem__(self, name, value):
        if name not in self._cli_opts:
            raise KeyError("Non-existing settings '%s'" % name)
        self._opts[name] = value

    def _process_value(self, name, value, log):
        if name == 'LogLevel':
            return self._process_log_level(value)
        if value == self._get_default_value(name):
            return value
        if name in ['Name', 'Doc', 'LogTitle', 'ReportTitle']:
            if name == 'Doc': value = self._escape(value)
            return value.replace('_', ' ')
        if name in ['Metadata', 'TagDoc']:
            if name == 'Metadata': value = [self._escape(v) for v in value]
            return [self._process_metadata_or_tagdoc(v) for v in value]
        if name in ['Include', 'Exclude']:
            return [v.replace('AND', '&').replace('_', ' ') for v in value]
        if name in self._output_opts and utils.eq(value, 'NONE'):
            return 'NONE'
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
        if name == 'RemoveKeywords':
            return [v.upper() for v in value]
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

    def __getitem__(self, name):
        if name not in self._opts:
            raise KeyError("Non-existing setting '%s'" % name)
        if name in self._output_opts:
            return self._get_output_file(name)
        return self._opts[name]

    def _get_output_file(self, type_):
        """Returns path of the requested output file and creates needed dirs.

        `type_` can be 'Output', 'Log', 'Report', 'DebugFile' or 'XUnitFile'.
        """
        name = self._opts[type_]
        if self._outputfile_disabled(type_, name):
            return 'NONE'
        name = self._process_output_name(name, type_)
        path = utils.abspath(os.path.join(self['OutputDir'], name))
        self._create_output_dir(os.path.dirname(path), type_)
        return path

    def _process_output_name(self, name, type_):
        base, ext = os.path.splitext(name)
        if self['TimestampOutputs']:
            base = '%s-%s' % (base, utils.get_start_timestamp('', '-', ''))
        ext = self._get_output_extension(ext, type_)
        return base + ext

    def _get_output_extension(self, ext, type_):
        if ext != '':
            return ext
        if type_ in ['Output', 'XUnitFile']:
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
            LOGGER.error("Invalid report background colors '%s'." % colors)
            return self._get_default_value('ReportBackground')
        colors = colors.split(':')
        if len(colors) == 2:
            return colors[0], colors[0], colors[1]
        return tuple(colors)

    def _process_tag_stat_combine(self, value):
        for replwhat, replwith in [('&', 'AND'), ('AND', ' AND '), ('NOT', ' NOT ')]:
            value = value.replace(replwhat, replwith)
        if ':' not in value:
            return value, ''
        pattern, title = value.rsplit(':', 1)
        return pattern, title.replace('_', ' ')

    def _process_tag_stat_link(self, value):
        tokens = value.split(':')
        if len(tokens) >= 3:
            return tokens[0], ':'.join(tokens[1:-1]), tokens[-1]
        LOGGER.error("Invalid format for option '--tagstatlink'. "
                     "Expected 'tag:link:title' but got '%s'." % value)
        return None

    def _convert_to_positive_integer_or_default(self, name, value):
        value = self._convert_to_integer(name, value)
        return value if value > 0 else self._get_default_value(name)

    def _convert_to_integer(self, name, value):
        try:
            return int(value)
        except ValueError:
            LOGGER.error("Option '--%s' expected integer value but got '%s'. "
                         "Default value used instead." % (name.lower(), value))
            return self._get_default_value(name)

    def _get_default_value(self, name):
        return self._cli_opts[name][1]

    def _split_args_from_name_or_path(self, name):
        if ':' not in name or os.path.exists(name):
            args = []
        else:
            args = name.split(':')
            name = args.pop(0)
            # Handle absolute Windows paths with arguments
            if len(name) == 1 and args[0].startswith(('/', '\\')):
                name = name + ':' + args.pop(0)
        if os.path.exists(name):
            name = os.path.abspath(name)
        return name, args

    def __contains__(self, setting):
        return setting in self._cli_opts

    def __unicode__(self):
        return '\n'.join('%s: %s' % (name, self._opts[name])
                         for name in sorted(self._opts))

    @property
    def output(self):
        return self._get_file('Output')

    @property
    def log(self):
        return self._get_file('Log')

    @property
    def report(self):
        return self._get_file('Report')

    @property
    def xunit(self):
        return self._get_file('XUnitFile')

    def _get_file(self, name):
        value = self[name]
        return value if value != 'NONE' else None

    @property
    def split_log(self):
        return self['SplitLog']

    @property
    def status_rc(self):
        return not self['NoStatusRC']


class RobotSettings(_BaseSettings):
    _extra_cli_opts = {'Output'        : ('output', 'output.xml'),
                       'LogLevel'      : ('loglevel', 'INFO'),
                       'RunMode'       : ('runmode', []),
                       'RunEmptySuite' : ('runemptysuite', False),
                       'WarnOnSkipped' : ('warnonskippedfiles', False),
                       'Variables'     : ('variable', []),
                       'VariableFiles' : ('variablefile', []),
                       'Listeners'     : ('listener', []),
                       'MonitorWidth'  : ('monitorwidth', 78),
                       'MonitorMarkers': ('monitormarkers', 'AUTO'),
                       'DebugFile'     : ('debugfile', 'NONE')}

    def is_rebot_needed(self):
        return not ('NONE' == self['Log'] == self['Report'] == self['XUnitFile'])

    def get_rebot_datasource_and_settings(self):
        datasource = self['Output']
        settings = RebotSettings(log=False)
        settings._opts.update(self._opts)
        for name in ['Variables', 'VariableFiles', 'Listeners']:
            del(settings._opts[name])
        for name in ['Include', 'Exclude', 'TestNames', 'SuiteNames', 'Metadata']:
            settings._opts[name] = []
        for name in ['Name', 'Doc']:
            settings._opts[name] = None
        settings._opts['Output'] = 'NONE'
        settings._opts['LogLevel'] = 'TRACE'
        settings._opts['ProcessEmptySuite'] = self['RunEmptySuite']
        return datasource, settings

    def _outputfile_disabled(self, type_, name):
        if name == 'NONE':
            return True
        return self._opts['Output'] == 'NONE' and type_ != 'DebugFile'

    def _escape(self, value):
        return utils.escape(value)


class RebotSettings(_BaseSettings):
    _extra_cli_opts = {'Output'            : ('output', 'NONE'),
                       'LogLevel'          : ('loglevel', 'TRACE'),
                       'ProcessEmptySuite' : ('processemptysuite', False),
                       'StartTime'         : ('starttime', None),
                       'EndTime'           : ('endtime', None)}

    def _outputfile_disabled(self, type_, name):
        return name == 'NONE'

    def _escape(self, value):
        return value

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
            'process_empty_suite': self['ProcessEmptySuite'],
            'remove_keywords': self['RemoveKeywords'],
            'log_level': self['LogLevel'],
            'critical': self['Critical'],
            'noncritical': self['NonCritical'],
            'starttime': self['StartTime'],
            'endtime': self['EndTime']
        }

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
