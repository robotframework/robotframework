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


import getopt     # optparse not supported by Jython 2.2
import os
import re
import sys
import glob
import string
import codecs
import textwrap

from robot.errors import DataError, Information, FrameworkError

from misc import plural_or_not
from unic import unic


ESCAPES = { 'space'   : ' ', 'apos'    : "'", 'quot'    : '"', 'lt'      : '<',
            'gt'      : '>', 'pipe'    : '|', 'star'    : '*', 'comma'   : ',',
            'slash'   : '/', 'semic'   : ';', 'colon'   : ':', 'quest'   : '?',
            'hash'    : '#', 'amp'     : '&', 'dollar'  : '$', 'percent' : '%',
            'at'      : '@', 'exclam'  : '!', 'paren1'  : '(', 'paren2'  : ')',
            'square1' : '[', 'square2' : ']', 'curly1'  : '{', 'curly2'  : '}',
            'bslash'  : '\\' }


class ArgumentParser:

    _opt_line_re = re.compile('''
    ^\s{,4}       # max 4 spaces in the beginning of the line
    ((-\S\s)*)    # all possible short options incl. spaces (group 1)
    --(\S{2,})    # required long option (group 3)
    (\s\S+)?      # optional value (group 4)
    (\s\*)?       # optional '*' telling option allowed multiple times (group 5)
    ''', re.VERBOSE)

    _usage_line_re = re.compile('''
    ^usage:.*
    \[options\]\s*
    (.*?)         # arguments (group 1)
    \s*$
    ''', re.VERBOSE | re.IGNORECASE)

    def __init__(self, usage, version=None, arg_limits=None):
        """Available options and tool name are read from the usage.

        Tool name is got from the first row of the usage. It is either the
        whole row or anything before first ' -- '.

        See for example 'runner.py' and 'rebot.py' for examples.
        """
        if not usage:
            raise FrameworkError('Usage cannot be empty')
        self._usage = usage
        self._name = usage.splitlines()[0].split(' -- ')[0].strip()
        self._version = version
        self._arg_limits = arg_limits
        self._short_opts = ''
        self._long_opts = []
        self._multi_opts = []
        self._toggle_opts = []
        self._names = []
        self._short_to_long = {}
        self._expected_args = ()
        self._parse_usage(usage)

    def parse_args(self, args_list, unescape=None, argfile=None, pythonpath=None,
                   help=None, version=None, check_args=False):
        """Parse given arguments and return options and positional arguments.

        Arguments must be given as a list and are typically sys.argv[1:].

        Options are retuned as a dictionary where long options are keys. Value
        is a string for those options that can be given only one time (if they
        are given multiple times the last value is used) or None if the option
        is not used at all. Value for options that can be given multiple times
        (denoted with '*' in the usage) is a list which contains all the given
        values and is empty if options are not used. Options not taken
        arguments have value False when they are not set and True otherwise.

        Positional arguments are returned as a list in the order they are given.

        'unescape' option can be used to automatically unescape problematic
        characters given in an escaped format. Given value must be the name of
        the long option used for escaping. Typically usage is having
        '--escape name:value *' in usage doc and specifying 'enescape="escape"'
        when calling this method.

        'argfile' can be used to automatically read arguments from specified
        file. Given value must be the name of the long option used for giving
        the argument file. Typical usage is '--argumentfile path *' in usage doc
        and calling this method with 'argfile="argumentfile"'. If 'argfile' is
        used, it can always be given multiple times and thus it is recommended
        to use '*' to denote that.

        'pythonpath' can be used to specify option(s) containing extra paths to
        be added into 'sys.path'. Value can be either a string containing the
        name of the long option used for this purpose or a list containing
        all such long options (i.e. the latter format allows aliases).

        'help' and 'version' make it possible to automatically generate help
        and version messages. Version is generated based on the tool name
        and version -- see __init__ for information how to set them. Help
        contains the whole usage given to __init__. Possible <VERSION> text
        in the usage is replaced with the given version. Possible <--ESCAPES-->
        is replaced with available escapes so that they are wrapped to multiple
        lines but take the same amount of horizontal space as <---ESCAPES--->.
        The numer of hyphens can be used to contrl the horizontal space. Both
        help and version are wrapped to Information exception.

        If 'check_args' is True, this method will automatically check that
        correct number of arguments, as parsed from the usage line, are given.
        If the last argument in the usage line ends with the character 's',
        the maximum number of arguments is infinite.

        Possible errors in processing arguments are reported using DataError.
        """
        args_list = [ self._decode_from_file_system(a) for a in args_list ]
        if argfile:
            args_list = self._add_args_from_file(args_list, argfile)
        opts, args = self._parse_args(args_list)
        if unescape:
            opts, args = self._unescape_opts_and_args(opts, args, unescape)
        if help and opts[help]:
            self._raise_help()
        if version and opts[version]:
            self._raise_version()
        if pythonpath:
            sys.path = self._get_pythonpath(opts[pythonpath]) + sys.path
        if check_args:
            self._check_args(args)
        return opts, args

    def _decode_from_file_system(self, arg):
        encoding = sys.getfilesystemencoding()
        if sys.platform.startswith('java'):
            # http://bugs.jython.org/issue1592
            from java.lang import String
            arg = String(arg)
        return unic(arg, encoding) if encoding else unic(arg)

    def _parse_args(self, args):
        args = [ self._lowercase_long_option(a) for a in args ]
        try:
            opts, args = getopt.getopt(args, self._short_opts, self._long_opts)
        except getopt.GetoptError, err:
            raise DataError(err.args[0])
        return self._process_opts(opts), self._glob_args(args)

    def _lowercase_long_option(self, opt):
        if not opt.startswith('--'):
            return opt
        if '=' not in opt:
            return opt.lower()
        opt, value = opt.split('=', 1)
        return '%s=%s' % (opt.lower(), value)

    def _check_args(self, args):
        if not self._arg_limits:
            raise FrameworkError('No argument information specified.')
        minargs, maxargs = self._arg_limits
        if minargs <= len(args) <= maxargs:
            return
        minend = plural_or_not(minargs)
        if minargs == maxargs:
            exptxt = "%d argument%s" % (minargs, minend)
        elif maxargs != sys.maxint:
            exptxt = "%d to %d arguments" % (minargs, maxargs)
        else:
            exptxt = "at least %d argument%s" % (minargs, minend)
        raise DataError("Expected %s, got %d." % (exptxt, len(args)))

    def _unescape_opts_and_args(self, opts, args, escape_opt):
        try:
            escape_strings = opts[escape_opt]
        except KeyError:
            raise FrameworkError("No escape option '%s' in given options")
        escapes = self._get_escapes(escape_strings)
        for name, value in opts.items():
            if name != escape_opt:
                opts[name] = self._unescape(value, escapes)
        args = [ self._unescape(arg, escapes) for arg in args ]
        return opts, args

    def _add_args_from_file(self, args, argfile_opt):
        argfile_opts = ['--'+argfile_opt]
        for sopt, lopt in self._short_to_long.items():
            if lopt == argfile_opt:
                argfile_opts.append('-'+sopt)
        while True:
            try:
                index = self._get_argfile_index(args, argfile_opts)
                path = args[index+1]
            except IndexError:
                break
            args[index:index+2] = self._get_args_from_file(path)
        return args

    def _get_argfile_index(self, args, argfile_opts):
        for opt in argfile_opts:
            if opt in args:
                return args.index(opt)
        raise IndexError

    def _get_args_from_file(self, path):
        args = []
        for line in self._read_argfile(path).splitlines():
            line = line.strip()
            if line.startswith('-'):
                args.extend(line.split(' ', 1))
            elif line and not line.startswith('#'):
                args.append(line)
        return args
    
    def _read_argfile(self, path):
        try:
            f = codecs.open(path, encoding='UTF-8')
            content = f.read()
        except (IOError, UnicodeError), err:
            raise DataError("Opening argument file '%s' failed: %s" % (path, err))
        finally:
            f.close()
        if content.startswith(codecs.BOM_UTF8.decode('UTF-8')):
            content = content[1:]
        return content

    def _get_escapes(self, escape_strings):
        escapes = {}
        for estr in escape_strings:
            try:
                name, value = estr.split(':', 1)
            except ValueError:
                raise DataError("Invalid escape string syntax '%s'. Expected: %s"
                                % (estr, 'what:with'))
            try:
                escapes[value] = ESCAPES[name.lower()]
            except KeyError:
                raise DataError("Invalid escape '%s'. Available: %s"
                                % (name, self._get_available_escapes()))
        return escapes

    def _unescape(self, value, escapes):
        if value in [None, True, False]:
            return value
        if isinstance(value, list):
            return [ self._unescape(item, escapes) for item in value ]
        for esc_name, esc_value in escapes.items():
            value = value.replace(esc_name, esc_value)
        return value

    def _process_opts(self, opt_tuple):
        opts = self._init_opts()
        for name, value in opt_tuple:
            name = self._get_name(name)
            if name in self._multi_opts:
                opts[name].append(value)
            elif name in self._toggle_opts:
                opts[name] = not opts[name]
            else:
                opts[name] = value
        return opts

    def _glob_args(self, args):
        temp = []
        for path in args:
            paths = glob.glob(path)
            if paths:
                temp.extend(paths)
            else:
                temp.append(path)
        return temp

    def _init_opts(self):
        opts = {}
        for name in self._names:
            if name in self._multi_opts:
                opts[name] = []
            elif name in self._toggle_opts:
                opts[name] = False
            else:
                opts[name] = None
        return opts

    def _get_name(self, name):
        name = name.lstrip('-')
        try:
            return self._short_to_long[name]
        except KeyError:
            return name

    def _parse_usage(self, usage):
        for line in usage.splitlines():
            if not self._parse_opt_line(line) and not self._arg_limits:
                self._parse_usage_line(line)

    def _parse_usage_line(self, line):
        res = self._usage_line_re.match(line)
        if res:
            args = res.group(1).split()
            if not args:
                self._arg_limits = (0, 0)
            else:
                maxargs = args[-1].endswith('s') and sys.maxint or len(args)
                self._arg_limits = (len(args), maxargs)

    def _parse_opt_line(self, line):
        res = self._opt_line_re.match(line)
        if not res:
            return False
        long_opt = res.group(3).lower()
        if long_opt in self._names:
            self._raise_option_multiple_times_in_usage('--' + long_opt)
        self._names.append(long_opt)
        short_opts = [ opt[1] for opt in res.group(1).split() ]
        for sopt in short_opts:
            if self._short_to_long.has_key(sopt):
                self._raise_option_multiple_times_in_usage('-' + sopt)
            self._short_to_long[sopt] = long_opt
        # options allowed multiple times
        if res.group(5):
            self._multi_opts.append(long_opt)
        # options with arguments
        if res.group(4):
            long_opt += '='
            short_opts = [ sopt + ':' for sopt in short_opts ]
        else:
            self._toggle_opts.append(long_opt)
        self._long_opts.append(long_opt)
        self._short_opts += (''.join(short_opts))
        return True

    def _get_pythonpath(self, paths):
        if isinstance(paths, basestring):
            paths = [paths]
        temp = []
        for path in self._split_pythonpath(paths):
            temp.extend(glob.glob(path))
        paths = [ os.path.normpath(path) for path in temp if path != '' ]
        return paths

    def _split_pythonpath(self, paths):
        # paths may already contain ':' as separator
        tokens = ':'.join(paths).split(':')
        if os.sep == '/':
            return tokens
        # Fix paths split like 'c:\temp' -> 'c', '\temp'
        ret = []
        drive = ''
        for item in tokens:
            item = item.replace('/', '\\')
            if drive and item.startswith('\\'):
                ret.append('%s:%s' % (drive, item))
                drive = ''
                continue
            if drive:
                ret.append(drive)
                drive = ''
            if len(item) == 1 and item in string.letters:
                drive = item
            else:
                ret.append(item)
        if drive:
            ret.append(drive)
        return ret

    def _get_available_escapes(self):
        names = sorted(ESCAPES.keys(), key=str.lower)
        return ', '.join('%s (%s)' % (n, ESCAPES[n]) for n in names)

    def _raise_help(self):
        msg = self._usage
        if self._version:
            msg = msg.replace('<VERSION>', self._version)
        def replace_escapes(res):
            escapes = 'Available escapes: ' + self._get_available_escapes()
            lines = textwrap.wrap(escapes, width=len(res.group(2)))
            indent = ' ' * len(res.group(1))
            return '\n'.join(indent + line for line in lines)
        msg = re.sub('( *)(<-+ESCAPES-+>)', replace_escapes, msg)
        raise Information(msg)

    def _raise_version(self):
        if not self._version:
            raise FrameworkError('Version not set')
        raise Information('%s %s' % (self._name, self._version))

    def _raise_option_multiple_times_in_usage(self, opt):
        raise FrameworkError("Option '%s' multiple times in usage" % opt)
