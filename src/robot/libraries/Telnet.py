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


import telnetlib
import time
import re
import inspect

from robot.version import get_version
from robot import utils


class Telnet:

    """A test library providing communication over Telnet connections.

    `Telnet` is Robot Framework's standard library that makes it
    possible to connect to Telnet servers and execute commands on the
    opened connections.

    See `Open Connection` and `Switch Connection` for details on how
    to handle multiple simultaneous connections. The responses are
    expected to be ASCII encoded and all non-ASCII characters are
    silently ignored.
    """

    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self, timeout=3.0, newline='CRLF', prompt=None, prompt_is_regexp=False):
        """Telnet library can be imported with optional arguments.

        Initialization parameters are used as default values when new
        connections are opened with `Open Connection` keyword. They can also be
        set after opening the connection using the `Set Timeout`, `Set Newline` and
        `Set Prompt` keywords. See these keywords for more information.

        Examples (use only one of these):

        | *Setting* | *Value* | *Value* | *Value* | *Value* | *Value* | *Comment* |
        | Library | Telnet |     |    |     |    | # default values                |
        | Library | Telnet | 0.5 |    |     |    | # set only timeout              |
        | Library | Telnet |     | LF |     |    | # set only newline              |
        | Library | Telnet | 2.0 | LF |     |    | # set timeout and newline       |
        | Library | Telnet | 2.0 | CRLF | $ |    | # set also prompt               |
        | Library | Telnet | 2.0 | LF | ($|~) | True | # set prompt with simple regexp |
        """
        self._timeout = timeout == '' and 3.0 or timeout
        self._newline = newline == '' and 'CRLF' or newline
        self._prompt = (prompt, prompt_is_regexp)
        self._cache = utils.ConnectionCache()
        self._conn = None
        self._conn_kws = self._lib_kws = None

    def get_keyword_names(self):
        return self._get_library_keywords() + self._get_connection_keywords()

    def _get_library_keywords(self):
        if self._lib_kws is None:
            self._lib_kws = [ name for name in dir(self)
                              if not name.startswith('_') and name != 'get_keyword_names'
                              and inspect.ismethod(getattr(self, name)) ]
        return self._lib_kws

    def _get_connection_keywords(self):
        if self._conn_kws is None:
            conn = self._get_connection()
            excluded = [ name for name in dir(telnetlib.Telnet())
                         if name not in ['write', 'read', 'read_until'] ]
            self._conn_kws = [ name for name in dir(conn)
                               if not name.startswith('_') and name not in excluded
                               and inspect.ismethod(getattr(conn, name)) ]
        return self._conn_kws

    def __getattr__(self, name):
        if name not in self._get_connection_keywords():
            raise AttributeError(name)
        # If no connection is initialized, get attributes from a non-active
        # connection. This makes it possible for Robot to create keyword
        # handlers when it imports the library.
        conn = self._conn is None and self._get_connection() or self._conn
        return getattr(conn, name)

    def open_connection(self, host, alias=None, port=23, timeout=None,
                        newline=None, prompt=None, prompt_is_regexp=False):
        """Opens a new Telnet connection to the given host and port.

        Possible already opened connections are cached.

        Returns the index of this connection, which can be used later
        to switch back to the connection. The index starts from 1 and
        is reset back to it when the `Close All Connections` keyword
        is used.

        The optional `alias` is a name for the connection, and it can
        be used for switching between connections, similarly as the
        index. See `Switch Connection` for more details about that.

        The `timeout`, `newline`, `prompt` and `prompt_is_regexp` arguments get
        default values when the library is taken into use, but setting them
        here overrides those values for this connection. See `importing` for
        more information.
        """
        if timeout is None or timeout == '':
            timeout = self._timeout
        if newline is None:
            newline = self._newline
        if prompt is None:
            prompt, prompt_is_regexp = self._prompt
        print '*INFO* Opening connection to %s:%s with prompt: %s' \
                % (host, port, self._prompt)
        self._conn = self._get_connection(host, port, timeout, newline,
                                          prompt, prompt_is_regexp)
        return self._cache.register(self._conn, alias)

    def _get_connection(self, *args):
        """Can be overridden to use a custom connection."""
        return TelnetConnection(*args)

    def switch_connection(self, index_or_alias):
        """Switches between active connections using an index or alias.

        The index is got from `Open Connection` keyword, and an alias
        can be given to it.

        Returns the index of previously active connection.

        Example:
        | Open Connection   | myhost.net        |          |          |
        | Login             | john              | secret   |          |
        | Write             | some command      |          |          |
        | Open Connection   | yourhost.com      | 2nd conn |          |
        | Login             | root              | password |          |
        | Write             | another cmd       |          |          |
        | ${old index}=     | Switch Connection | 1        | # index  |
        | Write             | something         |          |          |
        | Switch Connection | 2nd conn          | # alias  |          |
        | Write             | whatever          |          |          |
        | Switch Connection | ${old index}      | # back to original again |
        | [Teardown]        | Close All Connections   |            |

        The example above expects that there were no other open
        connections when opening the first one, because it used index
        '1' when switching to the connection later. If you are not
        sure about that, you can store the index into a variable as
        shown below.

        | ${id} =            | Open Connection | myhost.net |
        | # Do something ... |                 |            |
        | Switch Connection  | ${id}           |            |
        """
        old_index = self._cache.current_index
        self._conn = self._cache.switch(index_or_alias)
        return old_index

    def close_all_connections(self):
        """Closes all open connections and empties the connection cache.

        After this keyword, new indexes got from the `Open Connection`
        keyword are reset to 1.

        This keyword should be used in a test or suite teardown to
        make sure all connections are closed.
        """
        self._conn = self._cache.close_all()


class TelnetConnection(telnetlib.Telnet):

    def __init__(self, host=None, port=23, timeout=3.0, newline='CRLF',
                 prompt=None, prompt_is_regexp=False):
        port = port == '' and 23 or int(port)
        telnetlib.Telnet.__init__(self, host, port)
        self.set_timeout(timeout)
        self.set_newline(newline)
        self.set_prompt(prompt, prompt_is_regexp)
        self._default_log_level = 'INFO'
        self.set_option_negotiation_callback(self._negotiate_echo_on)

    def set_timeout(self, timeout):
        """Sets the timeout used in read operations to the given value.

        `timeout` is given in Robot Framework's time format
        (e.g. 1 minute 20 seconds) that is explained in the User Guide.

        Read operations that expect some output to appear (`Read
        Until`, `Read Until Regexp`, `Read Until Prompt`) use this
        timeout and fail if the expected output has not appeared when
        this timeout expires.

        The old timeout is returned and can be used to restore it later.

        Example:
        | ${tout} = | Set Timeout | 2 minute 30 seconds |
        | Do Something |
        | Set Timeout | ${tout} |
        """
        old = getattr(self, '_timeout', 3.0)
        self._timeout = utils.timestr_to_secs(timeout)
        return utils.secs_to_timestr(old)

    def set_newline(self, newline):
        """Sets the newline used by the `Write` keyword.

        Newline can be given either in escaped format using '\\n' and
        '\\r', or with special 'LF' and 'CR' syntax.

        Examples:
        | Set Newline | \\n  |
        | Set Newline | CRLF |

        Correct newline to use depends on the system and the default
        value is 'CRLF'.

        The old newline is returned and can be used to restore it later.
        See `Set Prompt` or `Set Timeout` for an example.
        """
        old = getattr(self, '_newline', 'CRLF')
        self._newline = newline.upper().replace('LF','\n').replace('CR','\r')
        return old

    def close_connection(self, loglevel=None):
        """Closes the current Telnet connection and returns any remaining output.

        See `Read` for more information on `loglevel`.
        """
        telnetlib.Telnet.close(self)
        ret = self.read_all().decode('ASCII', 'ignore')
        self._log(ret, loglevel)
        return ret

    def login(self, username, password, login_prompt='login: ',
              password_prompt='Password: '):
        """Logs in to the Telnet server with the given user information.

        The login keyword reads from the connection until login_prompt
        is encountered and then types the user name. Then it reads
        until password_prompt is encountered and types the
        password. The rest of the output (if any) is also read, and
        all the text that has been read is returned as a single
        string.

        If a prompt has been set to this connection, either with `Open
        Connection` or `Set Prompt`, this keyword reads the output
        until the prompt is found. Otherwise, the keyword sleeps for a
        second and reads everything that is available.
        """
        ret = self.read_until(login_prompt, 'TRACE').decode('ASCII', 'ignore')
        self.write_bare(username + self._newline)
        ret += username + '\n'
        ret += self.read_until(password_prompt, 'TRACE').decode('ASCII', 'ignore')
        self.write_bare(password + self._newline)
        ret += '*' * len(password) + '\n'
        if self._prompt_is_set():
            try:
                ret += self.read_until_prompt('TRACE')
            except AssertionError:
                self._verify_login(ret)
                raise
        else:
            ret += self._verify_login(ret)
        self._log(ret)
        return ret

    def _verify_login(self, ret):
        # It is necessary to wait for the 'login incorrect' message to appear.
        time.sleep(1)
        while True:
            try:
                ret += self.read_until('\n', 'TRACE').decode('ASCII', 'ignore')
            except AssertionError:
                return ret
            else:
                if 'Login incorrect' in ret:
                    self._log(ret)
                    raise AssertionError("Login incorrect")

    def write(self, text, loglevel=None):
        """Writes the given text over the connection and appends a newline.

        Consumes the written text (until the appended newline) from
        the output and returns it. The given text must not contain
        newlines.

        Note: This keyword does not return the possible output of the
        executed command. To get the output, one of the `Read XXX`
        keywords must be used.

        See `Read` for more information on `loglevel`.
        """
        if self._newline in text:
            raise RuntimeError("Write cannot be used with string containing "
                               "newlines. Use 'Write Bare' instead.")
        text += self._newline
        self.write_bare(text)
        # Can't read until 'text' because long lines are cut strangely in the output
        return self.read_until(self._newline, loglevel)

    def write_bare(self, text):
        """Writes the given text over the connection without appending a newline.

        Does not consume the written text.
        """
        try:
            text = str(text)
        except UnicodeError:
            raise ValueError('Only ASCII characters are allowed in Telnet. '
                             'Got: %s' % text)
        telnetlib.Telnet.write(self, text)

    def write_until_expected_output(self, text, expected, timeout,
                                    retry_interval, loglevel=None):
        """Writes the given text repeatedly, until `expected` appears in the output.

        `text` is written without appending a
        newline. `retry_interval` defines the time waited before
        writing `text` again. `text` is consumed from the output
        before `expected` is tried to be read.

        If `expected` does not appear in the output within `timeout`,
        this keyword fails.

        See `Read` for more information on `loglevel`.

        Example:
        | Write Until Expected Output | ps -ef| grep myprocess\\n | myprocess |
        | ...                         | 5s                        | 0.5s      |

        This writes the 'ps -ef | grep myprocess\\n', until
        'myprocess' appears on the output. The command is written
        every 0.5 seconds and the keyword ,fails if 'myprocess' does
        not appear in the output in 5 seconds.
        """
        timeout = utils.timestr_to_secs(timeout)
        retry_interval = utils.timestr_to_secs(retry_interval)
        starttime = time.time()
        while time.time() - starttime < timeout:
            self.write_bare(text)
            self.read_until(text, loglevel)
            ret = telnetlib.Telnet.read_until(self, expected,
                                              retry_interval).decode('ASCII', 'ignore')
            self._log(ret, loglevel)
            if ret.endswith(expected):
                return ret
        raise AssertionError("No match found for '%s' in %s"
                             % (expected, utils.secs_to_timestr(timeout)))

    def read(self, loglevel=None):
        """Reads and returns/logs everything that is currently available in the output.

        The read message is always returned and logged. The default
        log level is either 'INFO', or the level set with `Set Default
        Log Level`.  `loglevel` can be used to override the default
        log level, and the available levels are TRACE, DEBUG, INFO,
        and WARN.
        """
        ret = self.read_very_eager().decode('ASCII', 'ignore')
        self._log(ret, loglevel)
        return ret

    def read_until(self, expected, loglevel=None):
        """Reads from the current output, until expected is encountered.

        Text up to and including the match is returned. If no match is
        found, the keyword fails.

        See `Read` for more information on `loglevel`.
        """
        ret = telnetlib.Telnet.read_until(self, expected,
                                          self._timeout).decode('ASCII', 'ignore')
        self._log(ret, loglevel)
        if not ret.endswith(expected):
            raise AssertionError("No match found for '%s' in %s"
                                 % (expected, utils.secs_to_timestr(self._timeout)))
        return ret

    def read_until_regexp(self, *expected):
        """Reads from the current output, until a match to a regexp in expected.

        Expected is a list of regular expression patterns as strings,
        or compiled regular expressions. The keyword returns the text
        up to and including the first match to any of the regular
        expressions.

        If the last argument in `*expected` is a valid log level, it
        is used as `loglevel` in the keyword `Read`.

        Examples:
        | Read Until Regexp | (#|$) |
        | Read Until Regexp | first_regexp | second_regexp |
        | Read Until Regexp | some regexp  | DEBUG |
        """
        expected = list(expected)
        if self._is_valid_log_level(expected[-1]):
            loglevel = expected[-1]
            expected = expected[:-1]
        else:
            loglevel = 'INFO'
        try:
            index, _, ret = self.expect(expected, self._timeout)
        except TypeError:
            index, ret = -1, ''
        ret = ret.decode('ASCII', 'ignore')
        self._log(ret, loglevel)
        if index == -1:
            expected = [ exp if isinstance(exp, basestring) else exp.pattern
                         for exp in expected ]
            raise AssertionError("No match found for %s in %s"
                                 % (utils.seq2str(expected, lastsep=' or '),
                                    utils.secs_to_timestr(self._timeout)))
        return ret

    def read_until_prompt(self, loglevel=None):
        """Reads from the current output, until a prompt is found.

        The prompt must have been set, either in the library import or
        at login time, or by using the `Set Prompt` keyword.

        See `Read` for more information on `loglevel`.
        """
        if not self._prompt_is_set():
            raise RuntimeError('Prompt is not set')
        prompt, regexp = self._prompt
        if regexp:
            return self.read_until_regexp(prompt, loglevel)
        return self.read_until(prompt, loglevel)

    def execute_command(self, command, loglevel=None):
        """Executes given command and reads and returns everything until prompt.

        This is a convenience keyword; following two are functionally
        identical:

        | ${out} = | Execute Command   | Some command |

        | Write    | Some command      |
        | ${out} = | Read Until Prompt |

        This keyword expects a prompt to be set, see `Read Until
        Prompt` for details.

        See `Read` for more information on `loglevel`.
        """
        self.write(command, loglevel)
        return self.read_until_prompt(loglevel)

    def set_prompt(self, prompt, prompt_is_regexp=False):
        """Sets the prompt used in this connection to `prompt`.

        If `prompt_is_regexp` is a non-empty string, the given prompt is
        considered to be a regular expression.

        The old prompt is returned and can be used to restore it later.

        Example:
        | ${prompt} | ${regexp} = | Set Prompt | $ |
        | Do Something |
        | Set Prompt | ${prompt} | ${regexp} |
        """
        old = hasattr(self, '_prompt') and self._prompt or (None, False)
        if prompt_is_regexp:
            self._prompt = (re.compile(prompt), True)
        else:
            self._prompt = (prompt, False)
        if old[1]:
            return old[0].pattern, True
        return old

    def _prompt_is_set(self):
        return self._prompt[0] is not None

    def set_default_log_level(self, level):
        """Sets the default log level used by all read keywords.

        The possible values are TRACE, DEBUG, INFO and WARN. The default is
        INFO. The old value is returned and can be used to restore it later,
        similarly as with `Set Timeout`.
        """
        self._is_valid_log_level(level, raise_if_invalid=True)
        old = self._default_log_level
        self._default_log_level = level.upper()
        return old

    def _log(self, msg, level=None):
        self._is_valid_log_level(level, raise_if_invalid=True)
        msg = msg.strip()
        if level is None:
            level = self._default_log_level
        if msg != '':
            print '*%s* %s' % (level.upper(), msg)

    def _is_valid_log_level(self, level, raise_if_invalid=False):
        if level is None:
            return True
        if isinstance(level, basestring) and \
                level.upper() in ['TRACE', 'DEBUG', 'INFO', 'WARN']:
            return True
        if not raise_if_invalid:
            return False
        raise AssertionError("Invalid log level '%s'" % level)

    def _negotiate_echo_on(self, sock, cmd, opt):
        # This is supposed to turn server side echoing on and turn other options off.
        if opt == telnetlib.ECHO and cmd in (telnetlib.WILL, telnetlib.WONT):
            self.sock.sendall(telnetlib.IAC + telnetlib.DO + opt)
        elif opt != telnetlib.NOOPT:
            if cmd in (telnetlib.DO, telnetlib.DONT):
                self.sock.sendall(telnetlib.IAC + telnetlib.WONT + opt)
            elif cmd in (telnetlib.WILL, telnetlib.WONT):
                self.sock.sendall(telnetlib.IAC + telnetlib.DONT + opt)
