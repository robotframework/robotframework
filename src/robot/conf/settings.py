#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
from robot.output import LOGGER


class _BaseSettings:
    _cli_opts = { 'Name'             : ('name', None),
                  'Doc'              : ('doc', None),
                  'Metadata'         : ('metadata', []),
                  'TestNames'        : ('test', []),
                  'SuiteNames'       : ('suite', []),
                  'SetTag'           : ('settag', []),
                  'Include'          : ('include', []),
                  'Exclude'          : ('exclude', []),
                  'Critical'         : ('critical', None),
                  'NonCritical'      : ('noncritical', None),
                  'OutputDir'        : ('outputdir', '.'),
                  'Log'              : ('log', 'log.html'),
                  'Report'           : ('report', 'report.html'),
                  'Summary'          : ('summary', 'NONE'),
                  'SplitOutputs'     : ('splitoutputs', -1),
                  'TimestampOutputs' : ('timestampoutputs', False),
                  'LogTitle'         : ('logtitle', None),
                  'ReportTitle'      : ('reporttitle', None),
                  'SummaryTitle'     : ('summarytitle', None),
                  'ReportBackground' : ('reportbackground', None),
                  'SuiteStatLevel'   : ('suitestatlevel', -1),
                  'TagStatInclude'   : ('tagstatinclude', []),
                  'TagStatExclude'   : ('tagstatexclude', []),
                  'TagStatCombine'   : ('tagstatcombine', []),
                  'TagDoc'           : ('tagdoc', []),
                  'TagStatLink'      : ('tagstatlink', []),
                  'MonitorWidth'     : ('monitorwidth', 78),
                  'MonitorColors'    : ('monitorcolors', 'ON') }
    _deprecated = {}

    def __init__(self, options={}, log=True):
        self._opts = {}
        self._cli_opts.update(self._extra_cli_opts)
        self._process_deprecated_cli_opts(options)
        self._process_cli_opts(options)
        if log: LOGGER.info('Settings:\n%s' % self)

    def _process_cli_opts(self, opts):
        for name, (cli_name, default) in self._cli_opts.items():
            try:
                value = opts[cli_name]
                if value in [None, []]:
                    raise KeyError
            except KeyError:
                value = default
            self[name] = value

    def _process_deprecated_cli_opts(self, opts):
        for oldname, newname in self._deprecated.items():
            if oldname not in opts or opts[oldname] in [None, []]:
                continue
            if newname:
                LOGGER.warn("Option '--%s' is deprecated. Use '--%s' instead."
                            % (oldname, newname))
                opts[newname] = opts[oldname]
            else:
                LOGGER.error("Option '--%s' has been removed." % oldname)

    def __setitem__(self, name, value):
        if not self._cli_opts.has_key(name):
            raise KeyError("Non-existing settings '%s'" % name)
        if value:
            value = self._process_value(name, value)
        self._opts[name] = value

    def _process_value(self, name, value):
        if name in ['Name', 'Doc', 'LogTitle', 'ReportTitle', 'SummaryTitle']:
            return value.replace('_', ' ')
        if name in ['Metadata', 'TagDoc']:
            return [v.replace('_', ' ') for v in value]
        if name in ['Include', 'Exclude', 'TagStatCombine']:
            return [item.replace('AND', '&') for item in value]
        if name in self._optional_outputs and utils.eq(value, 'NONE'):
            return 'NONE'
        if name == 'OutputDir':
            return utils.normpath(value)
        if name in ['SplitOutputs', 'SuiteStatLevel', 'MonitorWidth']:
            return self._convert_to_integer(name, value)
        if name in ['Listeners', 'VariableFiles']:
            return [self._split_args_from_name(item) for item in value]
        if name == 'TagStatLink':
            return self._process_tag_stat_link(value)
        if name == 'RemoveKeywords':
            return value.upper()
        if name == 'MonitorColors':
            return (utils.eq(value, 'ON') and os.sep == '/') \
                or utils.eq(value, 'FORCE')
        return value

    def __getitem__(self, name):
        if not self._cli_opts.has_key(name):
            raise KeyError("Non-existing setting '%s'" % name)
        elif name in ['Output', 'Log', 'Report', 'Summary', 'DebugFile']:
            return self._get_output_file(name)
        return self._opts[name]

    def _get_output_file(self, type_):
        """Returns path of the requested ouput file and creates needed dirs.

        Type can be 'Output', 'Log', 'Report' or 'Summary'.
        """
        name = self._opts[type_]
        if name == 'NONE' and type_ in self._optional_outputs:
            return name
        name = self._process_output_name(name, type_)
        path = utils.normpath(os.path.join(self['OutputDir'], name), False)
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
        if type_ == 'Output':
            return '.xml'
        if type_ in ['Log', 'Report', 'Summary']:
            return '.html'
        if type_ == 'DebugFile':
            return '.txt'
        raise FrameworkError("Invalid output file type: %s" % type_)

    def _create_output_dir(self, path, type_):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except:
            raise DataError("Can't create %s file's parent directory '%s': %s"
                            % (type_.lower(), path, utils.get_error_message()))

    def _process_tag_stat_link(self, value):
        ret = []
        for item in value:
            tokens = item.split(':')
            if len(tokens) >= 3:
                ret.append((tokens[0], ':'.join(tokens[1:-1]), tokens[-1]))
            else:
                LOGGER.error("Invalid format for option '--tagstatlink'. "
                             "Expected 'tag:link:title' but got '%s'." % item)
        return ret

    def _convert_to_integer(self, name, value):
        try:
            return int(value)
        except ValueError:
            LOGGER.error("Option '--%s' expected integer value but got '%s'. "
                         "Default value used instead." % (name.lower(), value))
            return self._cli_opts[name][1]

    def _split_args_from_name(self, name):
        if ':' not in name or os.path.exists(name):
            return name, []
        args = name.split(':')
        name = args.pop(0)
        # Handle absolute Windows paths with arguments
        if len(name) == 1 and args[0] and args[0][0] in ['/', '\\']:
            name = name + ':' + args.pop(0)
        return name, args

    def __str__(self):
        return '\n'.join('%s: %s' % (name, self._opts[name])
                         for name in sorted(self._opts))


class RobotSettings(_BaseSettings):
    _extra_cli_opts = { 'Output'        : ('output', 'output.xml'),
                        'LogLevel'      : ('loglevel', 'INFO'),
                        'RunMode'       : ('runmode', []),
                        'Variables'     : ('variable', []),
                        'VariableFiles' : ('variablefile', []),
                        'Listeners'     : ('listener', []),
                        'DebugFile'     : ('debugfile', 'NONE') }
    _optional_outputs = ['Log', 'Report', 'Summary', 'DebugFile']

    def is_rebot_needed(self):
        return not ('NONE' == self['Log'] == self['Report'] == self['Summary'])

    def get_rebot_datasources_and_settings(self):
        datasources = [ self['Output'] ]
        settings = RebotSettings(log=False)
        settings._opts = self._opts.copy()
        for name in ['Variables', 'VariableFiles', 'Listeners']:
            del(settings._opts[name])
        for name in ['Include', 'Exclude', 'TestNames', 'SuiteNames', 'Metadata']:
            settings._opts[name] = []
        for name in ['Output', 'RemoveKeywords']:
            settings._opts[name] = 'NONE'
        for name in ['Name', 'Doc']:
            settings._opts[name] = None
        return datasources, settings


class RebotSettings(_BaseSettings):
    _extra_cli_opts = { 'Output'         : ('output', 'NONE'),
                        'LogLevel'       : ('loglevel', 'TRACE'),
                        'RemoveKeywords' : ('removekeywords', 'NONE'),
                        'StartTime'      : ('starttime', 'N/A'),
                        'EndTime'        : ('endtime', 'N/A')}
    _optional_outputs = ['Output', 'Log', 'Report', 'Summary']
