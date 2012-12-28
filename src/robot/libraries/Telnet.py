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

from __future__ import with_statement
from contextlib import contextmanager
import telnetlib
import time
import re
import inspect

from robot.api import logger
from robot.version import get_version
from robot import utils


class Telnet:
    """A test library providing communication over Telnet connections.

    `Telnet` is Robot Framework's standard library that makes it possible to
    connect to Telnet servers and execute commands on the opened connections.

    == Table of contents ==

    - `Connections`
    - `Reading and writing`
    - `Configuration`
    - `Importing`
    - `Shortcuts`
    - `Keywords`

    = Connections =

    The first step of using `Telnet` is opening a connection with `Open
    Connection` keyword. Typically the next step is logging in with `Login`
    keyword. In the end connection can be closed with `Close Connection`.

    It is possible to open multiple connections and switch the active one
    using `Switch Connection`. `Close All Connections` can be used to close
    all the connections. That is especially useful in suite teardowns to
    guarantee that all connections are always closed.

    = Reading and writing =

    After opening a connection and possibly logging in, commands can be
    executed or text written to the connection for other reasons using `Write`
    and `Write Bare` keywords. The main difference between these two is that
    the former appends a [#Configuration|newline] automatically and also
    consumes the written text from the output.

    After writing something to the connection, the resulting output can be
    read using `Read`, `Read Until`, `Read Until Regexp`, and `Read Until
    Prompt` keywords. Which one to use depends on the context, but the latest
    one is often the most convenient.

    As a convenience when running a command, it is possible to use `Execute
    Command` that simply uses `Write` and `Read Until Prompt` internally.
    `Write Until Expected Output` is useful if you need to wait until writing
    something produces a desired output.

    = Configuration =

    Many aspects related the connections can be easily configured either
    globally or per connection basis. Global configuration is done when
    [#Importing|library is imported], and these values can be overridden per
    connection by `Open Connection` or with setting specific keywords
    `Set Timeout`, `Set Newline`, `Set Prompt`, `Set Encoding`, and
    `Set Default Log Level`. All the setting specific keywords return the
    old value of the setting that can be later used for resetting the value.

    == Timeout ==

    Timeout defines how long is the maximum time to wait when reading
    output. It is used internally by `Read Until`, `Read Until Regexp`,
    `Read Until Prompt`, and `Login` keywords. The default value is 3 seconds.

    == Newline ==

    Newline defines which line separator `Write` keyword should use. The
    default value is `CRLF` that is typically used by Telnet connections.

    == Prompt ==

    Often the easiest way to read the output of a command is reading all
    the output until the next prompt with `Read Until Prompt`. It also makes
    it easier, and faster, to verify did `Login` succeed.

    Prompt can be specified either as a normal string or a regular expression.
    The latter is especially useful if the prompt changes as a result of
    the executed commands.

    == Encoding ==

    Encoding is needed when written or read text contains non-ASCII characters.
    The default encoding is UTF-8 that works also with ASCII.

    Using UTF-8 encoding by default and being able to configure encoding are
    new features in Robot Framework 2.7.6. In earlier versions only ASCII was
    supported.

    == Default log level ==

    All keywords that read something log the output. These keywords take the
    log level to use as an optional argument, and if no log level is specified
    they use the default value.

    The default value for default log level is `INFO`. Changing it, fo example,
    to `DEBUG` can be a good idea if there is lot of unnecessary output that
    makes log files big.

    Configuring default log level in `importing` and with `Open Connection`
    are new features in Robot Framework 2.7.6. In earlier versions only
    `Set Default Log Level` could be used.
    """
    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self, timeout='3 seconds', newline='CRLF', prompt=None,
                 prompt_is_regexp=False, encoding='UTF-8', default_log_level='INFO'):
        """Telnet library can be imported with optional arguments.

        Initialization parameters are used as default values when new
        connections are opened with `Open Connection` keyword. They can also be
        set after opening the connection using the `Set Timeout`, `Set Newline`,
        `Set Prompt`, and `Set Encoding` keywords. See these keywords for more
        information.

        Examples (use only one of these):

        | *Setting* | *Value* | *Value* | *Value* | *Value* | *Value* | *Comment* |
        | Library | Telnet |     |    |     |    | # default values                |
        | Library | Telnet | 0.5 |    |     |    | # set only timeout              |
        | Library | Telnet |     | LF |     |    | # set only newline              |
        | Library | Telnet | newline=LF | encoding=ISO-8859-1 | | | # set newline and encoding using named arguments |
        | Library | Telnet | 2.0 | LF |     |    | # set timeout and newline       |
        | Library | Telnet | 2.0 | CRLF | $ |    | # set also prompt               |
        | Library | Telnet | 2.0 | LF | ($|~) | True | # set prompt with simple regexp |
        """
        self._timeout = timeout or 3.0
        self._newline = newline or 'CRLF'
        self._prompt = (prompt, bool(prompt_is_regexp))
        self._encoding = encoding
        self._default_log_level = default_log_level
        self._cache = utils.ConnectionCache()
        self._conn = None
        self._conn_kws = self._lib_kws = None

    def get_keyword_names(self):
        return self._get_library_keywords() + self._get_connection_keywords()

    def _get_library_keywords(self):
        if self._lib_kws is None:
            self._lib_kws = self._get_keywords(self, ['get_keyword_names'])
        return self._lib_kws

    def _get_keywords(self, source, excluded):
        return [name for name in dir(source)
                if self._is_keyword(name, source, excluded)]

    def _is_keyword(self, name, source, excluded):
        return (name not in excluded and
                not name.startswith('_') and
                name != 'get_keyword_names' and
                inspect.ismethod(getattr(source, name)))

    def _get_connection_keywords(self):
        if self._conn_kws is None:
            conn = self._get_connection()
            excluded = [name for name in dir(telnetlib.Telnet())
                        if name not in ['write', 'read', 'read_until']]
            self._conn_kws = self._get_keywords(conn, excluded)
        return self._conn_kws

    def __getattr__(self, name):
        if name not in self._get_connection_keywords():
            raise AttributeError(name)
        # If no connection is initialized, get attributes from a non-active
        # connection. This makes it possible for Robot to create keyword
        # handlers when it imports the library.
        return getattr(self._conn or self._get_connection(), name)

    def open_connection(self, host, alias=None, port=23, timeout=None,
                        newline=None, prompt=None, prompt_is_regexp=False,
                        encoding=None, default_log_level=None):
        """Opens a new Telnet connection to the given host and port.

        Possible already opened connections are cached.

        Returns the index of this connection, which can be used later
        to switch back to the connection. The index starts from 1 and
        is reset back to it when the `Close All Connections` keyword
        is used.

        The optional `alias` is a name for the connection, and it can
        be used for switching between connections, similarly as the
        index. See `Switch Connection` for more details about that.

        The `timeout`, `newline`, `prompt`, `prompt_is_regexp`, and `encoding`
        arguments get default values when the library is taken into use, but
        setting them here overrides those values for this connection. See
        `importing` for more information.
        """
        timeout = timeout or self._timeout
        newline = newline or self._newline
        encoding = encoding or self._encoding
        default_log_level = default_log_level or self._default_log_level
        if not prompt:
            prompt, prompt_is_regexp = self._prompt
        logger.info('Opening connection to %s:%s with prompt: %s'
                    % (host, port, prompt))
        self._conn = self._get_connection(host, port, timeout, newline,
                                          prompt, prompt_is_regexp,
                                          encoding, default_log_level)
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
                 prompt=None, prompt_is_regexp=False, encoding='UTF-8',
                 default_log_level='INFO'):
        telnetlib.Telnet.__init__(self, host, int(port) if port else 23)
        self._set_timeout(timeout)
        self._set_newline(newline)
        self._set_prompt(prompt, prompt_is_regexp)
        self._set_encoding(encoding)
        self._set_default_log_level(default_log_level)
        self.set_option_negotiation_callback(self._negotiate_echo_on)

    def set_timeout(self, timeout):
        """Sets the timeout used in read operations to the given value.

        `timeout` is given in Robot Framework's time format
        (e.g. 1 minute 20 seconds) that is explained in the User Guide.

        Read operations that expect some output to appear (`Read
        Until`, `Read Until Regexp`, `Read Until Prompt`) use this
        timeout and fail if the expected output has not appeared when
        this timeout expires.

        The old timeout is returned and can be used to restore the timeout
        later.

        Example:
        | ${timeout} = | Set Timeout | 2 minute 30 seconds |
        | Do Something |
        | Set Timeout  | ${timeout}  |
        """
        self._verify_connection()
        old = self._timeout
        self._set_timeout(timeout)
        return utils.secs_to_timestr(old)

    def _set_timeout(self, timeout):
        self._timeout = utils.timestr_to_secs(timeout)

    def set_newline(self, newline):
        """Sets the newline used by the `Write` keyword.

        Newline can be given either in escaped format using '\\n' and
        '\\r', or with special 'LF' and 'CR' syntax.

        Examples:
        | Set Newline | \\n  |
        | Set Newline | CRLF |

        Correct newline to use depends on the system and network configuration.
        The default value is 'CRLF'.

        The old newline is returned and can be used to restore the newline
        later similarly as with `Set Timeout`.
        """
        self._verify_connection()
        old = self._newline
        self._set_newline(newline)
        return old

    def _set_newline(self, newline):
        self._newline = newline.upper().replace('LF','\n').replace('CR','\r')

    def set_prompt(self, prompt, prompt_is_regexp=False):
        """Sets the prompt used in this connection to `prompt`.

        If `prompt_is_regexp` is any non-empty string, the given prompt is
        considered to be a regular expression.

        The old prompt is returned and can be used to restore the prompt later.

        Example:
        | ${prompt} | ${regexp} = | Set Prompt | $ |
        | Do Something |
        | Set Prompt | ${prompt} | ${regexp} |
        """
        self._verify_connection()
        old = self._prompt
        self._set_prompt(prompt, prompt_is_regexp)
        if old[1]:
            return old[0].pattern, True
        return old

    def _set_prompt(self, prompt, prompt_is_regexp):
        if prompt_is_regexp:
            self._prompt = (re.compile(prompt), True)
        else:
            self._prompt = (prompt, False)

    def _prompt_is_set(self):
        return self._prompt[0] is not None

    def set_encoding(self, encoding):
        """Sets the encoding to use in this connection when writing and reading.

        The default encoding can be set during `importing` or using `Open
        Connection` keyword. The default value is 'UTF-8' and it works fine
        also with ASCII data.

        Setting encoding is a new feature in Robot Framework 2.7.6. Earlier
        versions only supported ASCII.
        """
        self._verify_connection()
        old = self._encoding
        self._set_encoding(encoding)
        return old

    def _set_encoding(self, encoding):
        self._encoding = encoding

    def _encode(self, text):
        if isinstance(text, str):
            return text
        return text.encode(self._encoding)

    def _decode(self, bytes):
        return bytes.decode(self._encoding)

    def set_default_log_level(self, level):
        """Sets the default log level used by all read keywords.

        The possible values are TRACE, DEBUG, INFO and WARN. The default is
        INFO.

        The old value is returned and can be used to restore the log level
        later similarly as with `Set Timeout`.
        """
        self._verify_connection()
        old = self._default_log_level
        self._set_default_log_level(level)
        return old

    def _set_default_log_level(self, level):
        if level is None or not self._is_valid_log_level(level):
            raise AssertionError("Invalid log level '%s'" % level)
        self._default_log_level = level.upper()

    def _is_valid_log_level(self, level):
        return level is None or level.upper() in ('TRACE', 'DEBUG', 'INFO', 'WARN')

    def close_connection(self, loglevel=None):
        """Closes the current Telnet connection and returns any remaining output.

        See `Read` for more information on `loglevel`.
        """
        telnetlib.Telnet.close(self)
        output = self._decode(self.read_all())
        self._log(output, loglevel)
        return output

    def login(self, username, password, login_prompt='login: ',
              password_prompt='Password: ', login_timeout='1 second',
              login_incorrect='Login incorrect'):
        """Logs in to the Telnet server with the given user information.

        This keyword reads from the connection until `login_prompt` is
        encountered and then types the given `username`. Then it reads
        until `password_prompt` is encountered and types the given
        `password`. In both cases a newline is appended automatically
        and the connection specific timeout used when waiting for outputs.

        How logging status is verified depends on whether prompt is set for
        this connection or not:

        1) If prompt is set, this keyword reads the output until the prompt
        is found using the normal timeout. If no prompt is found, login is
        considered failed and also this keyword fails. Note that in this case
        both `login_timeout` and `login_incorrect` arguments are ignored.

        2) If prompt is not set, this keywords sleeps until `login_timeout`
        and then reads all the output available on the connection. If the
        output contains `login_incorrect` text, login is considered failed
        and also this keyword fails. Both of these configuration parameters
        were added in Robot Framework 2.7.6. In earlier versions they were
        hard coded.
        """
        output = self._submit_credentials(username, password, login_prompt,
                                          password_prompt)
        if self._prompt_is_set():
            success, output2 = self._read_until_prompt()
        else:
            success, output2 = self._verify_login_without_prompt(
                    login_timeout, login_incorrect)
        output += output2
        self._log(output)
        if not success:
            raise AssertionError('Login incorrect')
        return output

    def _submit_credentials(self, username, password, login_prompt, password_prompt):
        output = self.read_until(login_prompt, 'TRACE')
        output += self.write(username, 'TRACE')
        output += self.read_until(password_prompt, 'TRACE')
        output += self.write(password, 'TRACE')
        return output

    def _verify_login_without_prompt(self, delay, incorrect):
        time.sleep(utils.timestr_to_secs(delay))
        output = self.read('TRACE')
        success = incorrect not in output
        return success, output

    def write(self, text, loglevel=None):
        """Writes the given text over the connection and appends a newline.

        Consumes the written text (until the appended newline) from
        the output and logs and returns it. The given text must not contain
        newlines. Use `Write Bare` instead if either of these features
        causes a problem.

        Note: This keyword does not return the possible output of the
        executed command. To get the output, one of the `Read XXX`
        keywords must be used.

        See `Read` for more information on `loglevel`.
        """
        if self._newline in text:
            raise RuntimeError("'Write' keyword cannot be used with strings "
                               "containing newlines. Use 'Write Bare' instead.")
        self.write_bare(text + self._newline)
        # Can't read until 'text' because long lines are cut strangely in the output
        return self.read_until(self._newline, loglevel)

    def write_bare(self, text):
        """Writes the given text over the connection without appending a newline.

        Does not consume the written text.

        Use `Write` to both append a newline and to consume the written text
        automatically.
        """
        self._verify_connection()
        telnetlib.Telnet.write(self, self._encode(text))

    def write_until_expected_output(self, text, expected, timeout,
                                    retry_interval, loglevel=None):
        """Writes the given `text` repeatedly, until `expected` appears in the output.

        `text` is written without appending a newline and it is consumed from
        the output before trying to find `expected`. If `expected` does not
        appear in the output within `timeout`, this keyword fails.

        `retry_interval` defines the time to wait `expected` to appear before
        writing the `text` again. Consuming the written `text` is subject to
        the read timeout set in `library importing` or with with `Set Timeout`
        keyword.

        Both `timeout` and `retry_interval` are given in Robot Framework's
        time format (e.g. 1 minute 20 seconds) that is explained in the User
        Guide.

        See `Read` for more information on `loglevel`.

        Example:
        | Write Until Expected Output | ps -ef| grep myprocess\\r\\n | myprocess |
        | ...                         | 5 s                          | 0.5 s     |

        The above example writes command `ps -ef | grep myprocess\\r\\n` until
        `myprocess` appears in the output. The command is written every 0.5
        seconds and the keyword fails if `myprocess` does not appear in
        the output in 5 seconds.
        """
        timeout = utils.timestr_to_secs(timeout)
        retry_interval = utils.timestr_to_secs(retry_interval)
        maxtime = time.time() + timeout
        while time.time() < maxtime:
            self.write_bare(text)
            self.read_until(text, loglevel)
            try:
                with self._custom_timeout(retry_interval):
                    return self.read_until(expected, loglevel)
            except AssertionError:
                pass
        self._raise_no_match_found(expected, timeout)

    def read(self, loglevel=None):
        """Reads and returns/logs everything that is currently available in the output.

        The read message is always returned and logged. The default
        log level is either 'INFO', or the level set with `Set Default
        Log Level`.  `loglevel` can be used to override the default
        log level, and the available levels are TRACE, DEBUG, INFO,
        and WARN.
        """
        self._verify_connection()
        output = self._decode(self.read_very_eager())
        self._log(output, loglevel)
        return output

    def read_until(self, expected, loglevel=None):
        """Reads from the current output, until expected is encountered.

        Text up to and including the match is returned. If no match is
        found, the keyword fails.

        See `Read` for more information on `loglevel`.
        """
        output = self._read_until(expected)
        self._log(output, loglevel)
        if not output.endswith(expected):
            self._raise_no_match_found(expected)
        return output

    def _read_until(self, expected):
        self._verify_connection()
        expected = self._encode(expected)
        output = telnetlib.Telnet.read_until(self, expected, self._timeout)
        return self._decode(output)

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
        if not expected:
            raise RuntimeError('At least one pattern required')
        if self._is_valid_log_level(expected[-1]):
            loglevel = expected[-1]
            expected = expected[:-1]
        else:
            loglevel = None
        index, output = self._read_until_regexp(*expected)
        self._log(output, loglevel)
        if index == -1:
            expected = [exp if isinstance(exp, basestring) else exp.pattern
                        for exp in expected]
            self._raise_no_match_found(expected)
        return output

    def _read_until_regexp(self, *expected):
        self._verify_connection()
        expected = [self._encode(exp) if isinstance(exp, unicode) else exp
                    for exp in expected]
        try:
            index, _, output = self.expect(expected, self._timeout)
        except TypeError:
            index, output = -1, ''
        return index, self._decode(output)

    def read_until_prompt(self, loglevel=None):
        """Reads from the current output, until a prompt is found.

        The prompt must have been set, either in the library import or
        at login time, or by using the `Set Prompt` keyword.

        See `Read` for more information on `loglevel`.
        """
        if not self._prompt_is_set():
            raise RuntimeError('Prompt is not set')
        success, output = self._read_until_prompt()
        self._log(output, loglevel)
        if not success:
            prompt, regexp = self._prompt
            raise AssertionError("Prompt '%s' not found in %s"
                    % (prompt if not regexp else prompt.pattern,
                       utils.secs_to_timestr(self._timeout)))
        return output

    def _read_until_prompt(self):
        prompt, regexp = self._prompt
        if regexp:
            index, output = self._read_until_regexp(prompt)
            success = index != -1
        else:
            output = self._read_until(prompt)
            success = output.endswith(prompt)
        return success, output

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

    @contextmanager
    def _custom_timeout(self, timeout):
        old = self.set_timeout(timeout)
        try:
            yield
        finally:
            self.set_timeout(old)

    def _verify_connection(self):
        if not self.sock:
            raise RuntimeError('No connection open')

    def _log(self, msg, level=None):
        msg = msg.strip()
        if msg:
            logger.write(msg, level or self._default_log_level)

    def _raise_no_match_found(self, expected, timeout=None):
        timeout = utils.secs_to_timestr(timeout or self._timeout)
        expected = "'%s'" % expected if isinstance(expected, basestring) \
            else utils.seq2str(expected, lastsep=' or ')
        raise AssertionError("No match found for %s in %s" % (expected, timeout))

    def _negotiate_echo_on(self, sock, cmd, opt):
        # This is supposed to turn server side echoing on and turn other options off.
        if opt == telnetlib.ECHO and cmd in (telnetlib.WILL, telnetlib.WONT):
            self.sock.sendall(telnetlib.IAC + telnetlib.DO + opt)
        elif opt != telnetlib.NOOPT:
            if cmd in (telnetlib.DO, telnetlib.DONT):
                self.sock.sendall(telnetlib.IAC + telnetlib.WONT + opt)
            elif cmd in (telnetlib.WILL, telnetlib.WONT):
                self.sock.sendall(telnetlib.IAC + telnetlib.DONT + opt)
