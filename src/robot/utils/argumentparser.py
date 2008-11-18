#  Copyright 2008 Nokia Siemens Networks Oyj
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
import os.path
import os
import re
import sys
import glob
import string

from robot.errors import DataError, FrameworkError

from misc import seq2str, plural_or_not
from robottypes import is_list, is_boolean

ESCAPES =  { 'space'   : ' ',
             'apos'    : "'",
             'quot'    : '"',
             'lt'      : '<',
             'gt'      : '>',
             'pipe'    : '|',
             'star'    : '*',
             'comma'   : ',',
             'bslash'  : '\\',
             'slash'   : '/',
             'semic'   : ';',
             'colon'   : ':',
             'quest'   : '?',
             'hash'    : '#',
             'amp'     : '&',
             'dollar'  : '$',
             'percent' : '%',
             'at'      : '@',
             'exclam'  : '!',
             'paren1'  : '(',
             'paren2'  : ')',
             'square1' : '[',
             'square2' : ']',
             'curly1'  : '{',
             'curly2'  : '}',
}


def get_escapes():
    names = ESCAPES.keys()
    names.sort()
    return [ '%s (%s)' % (name, ESCAPES[name]) for name in names ] 
                

class ArgumentParser:

    _short_opt_chars = '-?a-zA-Z'
    _long_opt_chars = _short_opt_chars + '_0-9'
    _value_chars = _long_opt_chars + '\.,=:|/<>*+!$@'
    
    _opt_line_re = re.compile('''
    ^([%s ]*?)        # possible short options incl. spaces (group 1)
    --([%s]{2,})      # required long option (group 2)
    ([%s ]*?)         # possible value and/or '*' telling that option is allowed
                      # multiple times (group 3)
    (\s{2,}.*)?$      # rest of the option line
    ''' % (_short_opt_chars, _long_opt_chars, _value_chars), re.VERBOSE)
    
    _usage_line_re = re.compile('''
    ^usage:           # 
    .*                #
    \[options\]       #
    \s+               #
    (.*)              # arguments (group 1)
    \s*$              #
    ''', re.VERBOSE | re.IGNORECASE)
    
    def __init__(self, usage):
        """Initialization is done using a usage doc explaining options.
        
        See for example 'runner.py' and 'rebot.py' for usage examples. 
        """
        self._short_opts = ''
        self._long_opts = []
        self._multi_opts = []
        self._toggle_opts = []
        self._names = []
        self._short_to_long = {}
        self._expected_args = ()
        self._parse_usage(usage)

    def parse_args(self, args_list, unescape=None, argfile=None, pythonpath=None,
                   check_args=False):
        """Parse given arguments and return options and positional arguments.
        
        Arguments must be given as a list and are typically sys.argv[1:].
        
        Options are retuned as a dictionary where long options are keys. Value
        is a string for those options that can be given only one time (if they
        are given multiple times the last value is used) or None if the option
        is not used at all. Value for options that can be given multiple times
        (denoted with '*' in the usage) is a list which contains all the given
        values and is empty if options are not used.  
        
        Positional arguments are returned as a list in the order they are given.
        
        'unescape' option can be used to automatically unescape problematic
        characters given in an escaped format. Given value must be the name of 
        the long option used for escaping. Typically usage is having 
        '--escape name:value *' in usage doc and specifying 'enescape="escape"'
        when calling this method.
        
        'argfile' can be used to automatically read arguments from specified 
        file. Given value must be the name of the long option used for giving 
        the argument file. Typical usage is '--argumentfile path' in usage doc
        and calling this method with 'argfile="argumentfile"'. 
        
        'pythonpath' can be used to specify option(s) containing extra paths to
        be added into 'sys.path'. Value can be either a string containing the
        name of the long option used for this purpose or a list containing
        all such long options (i.e. the latter format allows aliases).
        
        If 'check_args' is True, this method will automatically check that 
        correct number of arguments (as parsed from the usage line) is given.
        If wrong number of arguments is given DataError is risen in that case. 
        """
        if argfile:
            args_list = self._add_args_from_file(args_list, argfile)
        opts, args = self._parse_args(args_list)
        if unescape:
            opts, args = self._unescape_opts_and_args(opts, args, unescape)
        if pythonpath:
            sys.path = self._get_pythonpath(opts[pythonpath]) + sys.path
        if check_args:
            self.check_args(args)
        return opts, args

    def _parse_args(self, args):
        args = [ a.startswith('--') and a.lower() or a for a in args ]
        try:
            opt_tuple, args = getopt.getopt(args, self._short_opts, self._long_opts)
        except getopt.GetoptError, err:
            raise DataError(err)
        opts = self._process_opts(opt_tuple)
        return opts, args

    def check_args(self, args):
        if len(args) == len(self._expected_args):
            return
        elif len(args) < len(self._expected_args):
            msg = 'Required argument%s missing.' % plural_or_not(self._expected_args) 
        else:
            msg = 'Too many arguments.'
        msg += ' Expected %s' % seq2str(self._expected_args)
        if len(args) > 0: 
            msg += ' but got %s' % seq2str(args)
        msg += '.'
        raise DataError(msg)
    
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
        argfile_opts = [ '--'+argfile_opt ]
        for sopt, lopt in self._short_to_long.items():
            if lopt == argfile_opt:
                argfile_opts.append('-'+sopt)
        index = -1
        path = None
        for opt in argfile_opts:
            try:
                index = args.index(opt)
                path = args[index+1]
                break
            except:
                pass
        if path is not None:
            args[index:index+2] = self._get_args_from_file(path)
        return args

    def _get_args_from_file(self, path):
        try:
            argfile = open(path)
        except IOError, err:
            raise DataError("Opening argument file '%s' failed: %s" % (path, err))
        args = []
        for line in argfile.read().splitlines():
            line = line.strip()
            if line == '' or line.startswith('#'): 
                continue
            elif line.startswith('-'):
                args.extend(line.split(' ', 1))
            else:
                args.append(line)
        argfile.close()
        return args
    
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
                av = seq2str(get_escapes(), quote='', lastsep=', ')
                raise DataError("Invalid escape '%s'. Available: %s" % (name, av))
        return escapes

    def _unescape(self, value, escapes):
        if value is None or is_boolean(value):
            return value
        if is_list(value):
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
            line = line.strip()
            if line.startswith('-') and self._opt_line_re.match(line):
                self._parse_opt_line(line)
            elif self._usage_line_re.match(line):
                self._parse_usage_line(line)

    def _parse_usage_line(self, line):
        res = self._usage_line_re.match(line)
        self._expected_args = res.group(1).split()
        
    def _parse_opt_line(self, line):
        res = self._opt_line_re.match(line)
        long_opt = res.group(2).lower()
        if long_opt in self._names:
            self._raise_option_multiple_times_in_usage('--' + long_opt)
        self._names.append(long_opt)
        short_opts = self._parse_short_opts(res.group(1))
        for sopt in short_opts:
            if self._short_to_long.has_key(sopt):
                self._raise_option_multiple_times_in_usage('-' + sopt)
            self._short_to_long[sopt] = long_opt
        _takes_value, _is_multi = self._process_value(res.group(3))
        # options allowed multiple times
        if _is_multi:
            self._multi_opts.append(long_opt)
        # options with arguments
        if _takes_value:
            long_opt += '='
            short_opts = [ sopt + ':' for sopt in short_opts ]
        else:
            self._toggle_opts.append(long_opt)
        self._long_opts.append(long_opt)
        self._short_opts += (''.join(short_opts))

    def _process_value(self, valstr):
        if valstr is None or valstr == '':
            return False, False
        tokens = valstr.split()
        if len(tokens) == 1:
            if tokens[0] == '*': 
                return False, True
            else:
                return True, False
        if len(tokens) == 2:
            if tokens[1] == '*':
                return True, True
        raise FrameworkError("Invalid option value '%s'" % valstr)
        
    def _parse_short_opts(self, optstr):
        if optstr is None: return []
        return [ self._parse_short_opt(opt) for opt in optstr.split() ]

    def _parse_short_opt(self, opt):
        if len(opt) != 2 and opt[0] != '-':
            raise FrameworkError("Invalid short option '%s'" % opt)
        return opt[1]
    
    def _get_pythonpath(self, paths):
        if not is_list(paths):
            paths = [paths]
        temp = []
        for path in self._split_pythonpath(paths):
            temp.extend(glob.glob(path))
        paths = [ os.path.normpath(path) for path in temp if path != '' ]
        return paths

    def _split_pythonpath(self, paths):
        # paths may already contein ':' as separator
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

    def _raise_option_multiple_times_in_usage(self, opt):
        raise FrameworkError("Option '%s' multiple times in usage" % opt)
