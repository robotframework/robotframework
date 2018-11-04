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

from contextlib import contextmanager
import inspect
import re
import socket
import struct
import telnetlib
import time

try:
    import pyte
except ImportError:
    pyte = None

from robot.api import logger
from robot.api.deco import keyword
from robot.utils import (ConnectionCache, is_bytes, is_string, is_truthy,
                         is_unicode, secs_to_timestr, seq2str, timestr_to_secs)
from robot.version import get_version


class Telnet(object):
    """A test library providing communication over Telnet connections.

    ``Telnet`` is Robot Framework's standard library that makes it possible to
    connect to Telnet servers and execute commands on the opened connections.

    == Table of contents ==

    - `Connections`
    - `Writing and reading`
    - `Configuration`
    - `Terminal emulation`
    - `Logging`
    - `Time string format`
    - `Boolean arguments`
    - `Importing`
    - `Shortcuts`
    - `Keywords`

    = Connections =

    The first step of using ``Telnet`` is opening a connection with `Open
    Connection` keyword. Typically the next step is logging in with `Login`
    keyword, and in the end the opened connection can be closed with `Close
    Connection`.

    It is possible to open multiple connections and switch the active one
    using `Switch Connection`. `Close All Connections` can be used to close
    all the connections, which is especially useful in suite teardowns to
    guarantee that all connections are always closed.

    = Writing and reading =

    After opening a connection and possibly logging in, commands can be
    executed or text written to the connection for other reasons using `Write`
    and `Write Bare` keywords. The main difference between these two is that
    the former adds a [#Configuration|configurable newline] after the text
    automatically.

    After writing something to the connection, the resulting output can be
    read using `Read`, `Read Until`, `Read Until Regexp`, and `Read Until
    Prompt` keywords. Which one to use depends on the context, but the latest
    one is often the most convenient.

    As a convenience when running a command, it is possible to use `Execute
    Command` that simply uses `Write` and `Read Until Prompt` internally.
    `Write Until Expected Output` is useful if you need to wait until writing
    something produces a desired output.

    Written and read text is automatically encoded/decoded using a
    [#Configuration|configured encoding].

    The ANSI escape codes, like cursor movement and color codes, are
    normally returned as part of the read operation. If an escape code occurs
    in middle of a search pattern it may also prevent finding the searched
    string. `Terminal emulation` can be used to process these
    escape codes as they would be if a real terminal would be in use.

    = Configuration =

    Many aspects related the connections can be easily configured either
    globally or per connection basis. Global configuration is done when
    [#Importing|library is imported], and these values can be overridden per
    connection by `Open Connection` or with setting specific keywords
    `Set Timeout`, `Set Newline`, `Set Prompt`, `Set Encoding`,
    `Set Default Log Level` and `Set Telnetlib Log Level`.

    Values of ``environ_user``, ``window_size``, ``terminal_emulation``, and
    ``terminal_type`` can not be changed after opening the connection.

    == Timeout ==

    Timeout defines how long is the maximum time to wait when reading
    output. It is used internally by `Read Until`, `Read Until Regexp`,
    `Read Until Prompt`, and `Login` keywords. The default value is 3 seconds.

    == Connection Timeout ==

    Connection Timeout defines how long is the maximum time to wait when
    opening the telnet connection. It is used internally by `Open Connection`.
    The default value is the system global default timeout.

    New in Robot Framework 2.9.2.

    == Newline ==

    Newline defines which line separator `Write` keyword should use. The
    default value is ``CRLF`` that is typically used by Telnet connections.

    Newline can be given either in escaped format using ``\\n`` and ``\\r`` or
    with special ``LF`` and ``CR`` syntax.

    Examples:
    | `Set Newline` | \\n  |
    | `Set Newline` | CRLF |

    == Prompt ==

    Often the easiest way to read the output of a command is reading all
    the output until the next prompt with `Read Until Prompt`. It also makes
    it easier, and faster, to verify did `Login` succeed.

    Prompt can be specified either as a normal string or a regular expression.
    The latter is especially useful if the prompt changes as a result of
    the executed commands. Prompt can be set to be a regular expression
    by giving ``prompt_is_regexp`` argument a true value (see `Boolean
    arguments`).

    Examples:
    | `Open Connection` | lolcathost | prompt=$              |
    | `Set Prompt`      | (> |# )    | prompt_is_regexp=true |

    == Encoding ==

    To ease handling text containing non-ASCII characters, all written text is
    encoded and read text decoded by default. The default encoding is UTF-8
    that works also with ASCII. Encoding can be disabled by using a special
    encoding value ``NONE``. This is mainly useful if you need to get the bytes
    received from the connection as-is.

    Notice that when writing to the connection, only Unicode strings are
    encoded using the defined encoding. Byte strings are expected to be already
    encoded correctly. Notice also that normal text in test data is passed to
    the library as Unicode and you need to use variables to use bytes.

    It is also possible to configure the error handler to use if encoding or
    decoding characters fails. Accepted values are the same that encode/decode
    functions in Python strings accept. In practice the following values are
    the most useful:

    - ``ignore``: ignore characters that cannot be encoded (default)
    - ``strict``: fail if characters cannot be encoded
    - ``replace``: replace characters that cannot be encoded with a replacement
      character

    Examples:
    | `Open Connection` | lolcathost | encoding=Latin1 | encoding_errors=strict |
    | `Set Encoding` | ISO-8859-15 |
    | `Set Encoding` | errors=ignore |

    == Default log level ==

    Default log level specifies the log level keywords use for `logging` unless
    they are given an explicit log level. The default value is ``INFO``, and
    changing it, for example, to ``DEBUG`` can be a good idea if there is lot
    of unnecessary output that makes log files big.

    == Terminal type ==

    By default the Telnet library does not negotiate any specific terminal type
    with the server. If a specific terminal type, for example ``vt100``, is
    desired, the terminal type can be configured in `importing` and with
    `Open Connection`.

    == Window size ==

    Window size for negotiation with the server can be configured when
    `importing` the library and with `Open Connection`.

    == USER environment variable ==

    Telnet protocol allows the ``USER`` environment variable to be sent when
    connecting to the server. On some servers it may happen that there is no
    login prompt, and on those cases this configuration option will allow still
    to define the desired username. The option ``environ_user`` can be used in
    `importing` and with `Open Connection`.

    = Terminal emulation =

    Telnet library supports terminal
    emulation with [http://pyte.readthedocs.io|Pyte]. Terminal emulation
    will process the output in a virtual screen. This means that ANSI escape
    codes, like cursor movements, and also control characters, like
    carriage returns and backspaces, have the same effect on the result as they
    would have on a normal terminal screen. For example the sequence
    ``acdc\\x1b[3Dbba`` will result in output ``abba``.

    Terminal emulation is taken into use by giving ``terminal_emulation``
    argument a true value (see `Boolean arguments`) either in the library
    initialization or with `Open Connection`.

    As Pyte approximates vt-style terminal, you may also want to set the
    terminal type as ``vt100``. We also recommend that you increase the window
    size, as the terminal emulation will break all lines that are longer than
    the window row length.

    When terminal emulation is used, the `newline` and `encoding` can not be
    changed anymore after opening the connection.

    Examples:
    | `Open Connection` | lolcathost | terminal_emulation=True | terminal_type=vt100 | window_size=400x100 |

    As a prerequisite for using terminal emulation, you need to have Pyte
    installed. Due to backwards incompatible changes in Pyte, different
    Robot Framework versions support different Pyte versions:

    - Pyte 0.6 and newer are supported by Robot Framework 3.0.3.
      Latest Pyte version can be installed (or upgraded) with
      ``pip install --upgrade pyte``.
    - Pyte 0.5.2 and older are supported by Robot Framework 3.0.2 and earlier.
      Pyte 0.5.2 can be installed with ``pip install pyte==0.5.2``.

    = Logging =

    All keywords that read something log the output. These keywords take the
    log level to use as an optional argument, and if no log level is specified
    they use the [#Configuration|configured] default value.

    The valid log levels to use are ``TRACE``, ``DEBUG``, ``INFO`` (default),
    and ``WARN``. Levels below ``INFO`` are not shown in log files by default
    whereas warnings are shown more prominently.

    The [http://docs.python.org/library/telnetlib.html|telnetlib module]
    used by this library has a custom logging system for logging content it
    sends and receives. By default these messages are written using ``TRACE``
    level, but the level is configurable with the ``telnetlib_log_level``
    option either in the library initialization, to the `Open Connection`
    or by using the `Set Telnetlib Log Level` keyword to the active
    connection. Special level ``NONE`` con be used to disable the logging
    altogether.

    = Time string format =

    Timeouts and other times used must be given as a time string using format
    like ``15 seconds`` or ``1min 10s``. If the timeout is given as just
    a number, for example, ``10`` or ``1.5``, it is considered to be seconds.
    The time string format is described in more detail in an appendix of
    [http://robotframework.org/robotframework/#user-guide|Robot Framework User Guide].

    = Boolean arguments =

    Some keywords accept arguments that are handled as Boolean values true or
    false. If such an argument is given as a string, it is considered false if
    it is an empty string or equal to ``FALSE``, ``NONE``, ``NO``, ``OFF`` or
    ``0``, case-insensitively. Other strings are considered true regardless
    their value, and other argument types are tested using the same
    [http://docs.python.org/library/stdtypes.html#truth|rules as in Python].

    True examples:
    | `Open Connection` | lolcathost | terminal_emulation=True    | # Strings are generally true.    |
    | `Open Connection` | lolcathost | terminal_emulation=yes     | # Same as the above.             |
    | `Open Connection` | lolcathost | terminal_emulation=${TRUE} | # Python ``True`` is true.       |
    | `Open Connection` | lolcathost | terminal_emulation=${42}   | # Numbers other than 0 are true. |

    False examples:
    | `Open Connection` | lolcathost | terminal_emulation=False    | # String ``false`` is false.   |
    | `Open Connection` | lolcathost | terminal_emulation=no       | # Also string ``no`` is false. |
    | `Open Connection` | lolcathost | terminal_emulation=${EMPTY} | # Empty string is false.       |
    | `Open Connection` | lolcathost | terminal_emulation=${FALSE} | # Python ``False`` is false.   |

    Considering string ``NONE`` false is new in Robot Framework 3.0.3 and
    considering also ``OFF`` and ``0`` false is new in Robot Framework 3.1.
    """
    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self, timeout='3 seconds', newline='CRLF',
                 prompt=None, prompt_is_regexp=False,
                 encoding='UTF-8', encoding_errors='ignore',
                 default_log_level='INFO', window_size=None,
                 environ_user=None, terminal_emulation=False,
                 terminal_type=None, telnetlib_log_level='TRACE',
                 connection_timeout=None):
        """Telnet library can be imported with optional configuration parameters.

        Configuration parameters are used as default values when new
        connections are opened with `Open Connection` keyword. They can also be
        overridden after opening the connection using the `Set ...` `keywords`.
        See these keywords as well as `Configuration`, `Terminal emulation` and
        `Logging` sections above for more information about these parameters
        and their possible values.

        See `Time string format` and `Boolean arguments` sections for
        information about using arguments accepting times and Boolean values,
        respectively.

        Examples (use only one of these):
        | = Setting = | = Value = | = Value =                | = Value =            | = Value =           | = Comment = |
        | Library     | Telnet    |                          |                      |                     | # default values |
        | Library     | Telnet    | 5 seconds                |                      |                     | # set only timeout |
        | Library     | Telnet    | newline=LF               | encoding=ISO-8859-1  |                     | # set newline and encoding using named arguments |
        | Library     | Telnet    | prompt=$                 |                      |                     | # set prompt |
        | Library     | Telnet    | prompt=(> |# )           | prompt_is_regexp=yes |                     | # set prompt as a regular expression |
        | Library     | Telnet    | terminal_emulation=True  | terminal_type=vt100  | window_size=400x100 | # use terminal emulation with defined window size and terminal type |
        | Library     | Telnet    | telnetlib_log_level=NONE |                      |                     | # disable logging messages from the underlying telnetlib |
        """
        self._timeout = timeout or 3.0
        self._set_connection_timeout(connection_timeout)
        self._newline = newline or 'CRLF'
        self._prompt = (prompt, prompt_is_regexp)
        self._encoding = encoding
        self._encoding_errors = encoding_errors
        self._default_log_level = default_log_level
        self._window_size = window_size
        self._environ_user = environ_user
        self._terminal_emulation = terminal_emulation
        self._terminal_type = terminal_type
        self._telnetlib_log_level = telnetlib_log_level
        self._cache = ConnectionCache()
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

    @keyword(types=None)
    def open_connection(self, host, alias=None, port=23, timeout=None,
                        newline=None, prompt=None, prompt_is_regexp=False,
                        encoding=None, encoding_errors=None,
                        default_log_level=None, window_size=None,
                        environ_user=None, terminal_emulation=None,
                        terminal_type=None, telnetlib_log_level=None,
                        connection_timeout=None):
        """Opens a new Telnet connection to the given host and port.

        The ``timeout``, ``newline``, ``prompt``, ``prompt_is_regexp``,
        ``encoding``, ``default_log_level``, ``window_size``, ``environ_user``,
        ``terminal_emulation``, ``terminal_type`` and ``telnetlib_log_level``
        arguments get default values when the library is [#Importing|imported].
        Setting them here overrides those values for the opened connection.
        See `Configuration`, `Terminal emulation` and `Logging` sections for
        more information about these parameters and their possible values.

        Possible already opened connections are cached and it is possible to
        switch back to them using `Switch Connection` keyword. It is possible to
        switch either using explicitly given ``alias`` or using index returned
        by this keyword. Indexing starts from 1 and is reset back to it by
        `Close All Connections` keyword.
        """
        timeout = timeout or self._timeout
        connection_timeout = (timestr_to_secs(connection_timeout)
                              if connection_timeout
                              else self._connection_timeout)
        newline = newline or self._newline
        encoding = encoding or self._encoding
        encoding_errors = encoding_errors or self._encoding_errors
        default_log_level = default_log_level or self._default_log_level
        window_size = self._parse_window_size(window_size or self._window_size)
        environ_user = environ_user or self._environ_user
        if terminal_emulation is None:
            terminal_emulation = self._terminal_emulation
        terminal_type = terminal_type or self._terminal_type
        telnetlib_log_level = telnetlib_log_level or self._telnetlib_log_level
        if not prompt:
            prompt, prompt_is_regexp = self._prompt
        logger.info('Opening connection to %s:%s with prompt: %s%s'
                    % (host, port, prompt, ' (regexp)' if prompt_is_regexp else ''))
        self._conn = self._get_connection(host, port, timeout, newline,
                                          prompt, is_truthy(prompt_is_regexp),
                                          encoding, encoding_errors,
                                          default_log_level,
                                          window_size,
                                          environ_user,
                                          is_truthy(terminal_emulation),
                                          terminal_type,
                                          telnetlib_log_level,
                                          connection_timeout)
        return self._cache.register(self._conn, alias)

    def _parse_window_size(self, window_size):
        if not window_size:
            return None
        try:
            cols, rows = window_size.split('x', 1)
            return int(cols), int(rows)
        except ValueError:
            raise ValueError("Invalid window size '%s'. Should be "
                             "<rows>x<columns>." % window_size)

    def _get_connection(self, *args):
        """Can be overridden to use a custom connection."""
        return TelnetConnection(*args)

    def _set_connection_timeout(self, connection_timeout):
        self._connection_timeout = connection_timeout
        if self._connection_timeout:
            self._connection_timeout = timestr_to_secs(connection_timeout)

    def switch_connection(self, index_or_alias):
        """Switches between active connections using an index or an alias.

        Aliases can be given to `Open Connection` keyword which also always
        returns the connection index.

        This keyword returns the index of previous active connection.

        Example:
        | `Open Connection`   | myhost.net              |          |           |
        | `Login`             | john                    | secret   |           |
        | `Write`             | some command            |          |           |
        | `Open Connection`   | yourhost.com            | 2nd conn |           |
        | `Login`             | root                    | password |           |
        | `Write`             | another cmd             |          |           |
        | ${old index}=       | `Switch Connection`     | 1        | # index   |
        | `Write`             | something               |          |           |
        | `Switch Connection` | 2nd conn                |          | # alias   |
        | `Write`             | whatever                |          |           |
        | `Switch Connection` | ${old index}            | | # back to original |
        | [Teardown]          | `Close All Connections` |          |           |

        The example above expects that there were no other open
        connections when opening the first one, because it used index
        ``1`` when switching to the connection later. If you are not
        sure about that, you can store the index into a variable as
        shown below.

        | ${index} =          | `Open Connection` | myhost.net |
        | `Do Something`      |                   |            |
        | `Switch Connection` | ${index}          |            |
        """
        old_index = self._cache.current_index
        self._conn = self._cache.switch(index_or_alias)
        return old_index

    def close_all_connections(self):
        """Closes all open connections and empties the connection cache.

        If multiple connections are opened, this keyword should be used in
        a test or suite teardown to make sure that all connections are closed.
        It is not an error is some of the connections have already been closed
        by `Close Connection`.

        After this keyword, new indexes returned by `Open Connection`
        keyword are reset to 1.
        """
        self._conn = self._cache.close_all()


class TelnetConnection(telnetlib.Telnet):
    NEW_ENVIRON_IS = b'\x00'
    NEW_ENVIRON_VAR = b'\x00'
    NEW_ENVIRON_VALUE = b'\x01'
    INTERNAL_UPDATE_FREQUENCY = 0.03

    def __init__(self, host=None, port=23, timeout=3.0, newline='CRLF',
                 prompt=None, prompt_is_regexp=False,
                 encoding='UTF-8', encoding_errors='ignore',
                 default_log_level='INFO', window_size=None, environ_user=None,
                 terminal_emulation=False, terminal_type=None,
                 telnetlib_log_level='TRACE', connection_timeout=None):
        if connection_timeout is None:
            telnetlib.Telnet.__init__(self, host, int(port) if port else 23)
        else:
            telnetlib.Telnet.__init__(self, host, int(port) if port else 23,
                                      connection_timeout)
        self._set_timeout(timeout)
        self._set_newline(newline)
        self._set_prompt(prompt, prompt_is_regexp)
        self._set_encoding(encoding, encoding_errors)
        self._set_default_log_level(default_log_level)
        self._window_size = window_size
        self._environ_user = self._encode(environ_user) if environ_user else None
        self._terminal_emulator = self._check_terminal_emulation(terminal_emulation)
        self._terminal_type = self._encode(terminal_type) if terminal_type else None
        self.set_option_negotiation_callback(self._negotiate_options)
        self._set_telnetlib_log_level(telnetlib_log_level)
        self._opt_responses = list()

    def set_timeout(self, timeout):
        """Sets the timeout used for waiting output in the current connection.

        Read operations that expect some output to appear (`Read Until`, `Read
        Until Regexp`, `Read Until Prompt`, `Login`) use this timeout and fail
        if the expected output does not appear before this timeout expires.

        The ``timeout`` must be given in `time string format`. The old timeout
        is returned and can be used to restore the timeout later.

        Example:
        | ${old} =       | `Set Timeout` | 2 minute 30 seconds |
        | `Do Something` |
        | `Set Timeout`  | ${old}  |

        See `Configuration` section for more information about global and
        connection specific configuration.
        """
        self._verify_connection()
        old = self._timeout
        self._set_timeout(timeout)
        return secs_to_timestr(old)

    def _set_timeout(self, timeout):
        self._timeout = timestr_to_secs(timeout)

    def set_newline(self, newline):
        """Sets the newline used by `Write` keyword in the current connection.

        The old newline is returned and can be used to restore the newline later.
        See `Set Timeout` for a similar example.

        If terminal emulation is used, the newline can not be changed on an open
        connection.

        See `Configuration` section for more information about global and
        connection specific configuration.
        """
        self._verify_connection()
        if self._terminal_emulator:
            raise AssertionError("Newline can not be changed when terminal emulation is used.")
        old = self._newline
        self._set_newline(newline)
        return old

    def _set_newline(self, newline):
        newline = str(newline).upper()
        self._newline = newline.replace('LF', '\n').replace('CR', '\r')

    def set_prompt(self, prompt, prompt_is_regexp=False):
        """Sets the prompt used by `Read Until Prompt` and `Login` in the current connection.

        If ``prompt_is_regexp`` is given a true value (see `Boolean arguments`),
        the given ``prompt`` is considered to be a regular expression.

        The old prompt is returned and can be used to restore the prompt later.

        Example:
        | ${prompt} | ${regexp} = | `Set Prompt` | $ |
        | `Do Something` |
        | `Set Prompt` | ${prompt} | ${regexp} |

        See the documentation of
        [http://docs.python.org/library/re.html|Python re module]
        for more information about the supported regular expression syntax.
        Notice that possible backslashes need to be escaped in Robot Framework
        test data.

        See `Configuration` section for more information about global and
        connection specific configuration.
        """
        self._verify_connection()
        old = self._prompt
        self._set_prompt(prompt, prompt_is_regexp)
        if old[1]:
            return old[0].pattern, True
        return old

    def _set_prompt(self, prompt, prompt_is_regexp):
        if is_truthy(prompt_is_regexp):
            self._prompt = (re.compile(prompt), True)
        else:
            self._prompt = (prompt, False)

    def _prompt_is_set(self):
        return self._prompt[0] is not None

    @keyword(types=None)
    def set_encoding(self, encoding=None, errors=None):
        """Sets the encoding to use for `writing and reading` in the current connection.

        The given ``encoding`` specifies the encoding to use when written/read
        text is encoded/decoded, and ``errors`` specifies the error handler to
        use if encoding/decoding fails. Either of these can be omitted and in
        that case the old value is not affected. Use string ``NONE`` to disable
        encoding altogether.

        See `Configuration` section for more information about encoding and
        error handlers, as well as global and connection specific configuration
        in general.

        The old values are returned and can be used to restore the encoding
        and the error handler later. See `Set Prompt` for a similar example.

        If terminal emulation is used, the encoding can not be changed on an open
        connection.
        """
        self._verify_connection()
        if self._terminal_emulator:
            raise AssertionError("Encoding can not be changed when terminal emulation is used.")
        old = self._encoding
        self._set_encoding(encoding or old[0], errors or old[1])
        return old

    def _set_encoding(self, encoding, errors):
        self._encoding = (encoding.upper(), errors)

    def _encode(self, text):
        if is_bytes(text):
            return text
        if self._encoding[0] == 'NONE':
            return text.encode('ASCII')
        return text.encode(*self._encoding)

    def _decode(self, bytes):
        if self._encoding[0] == 'NONE':
            return bytes
        return bytes.decode(*self._encoding)

    def set_telnetlib_log_level(self, level):
        """Sets the log level used for `logging` in the underlying ``telnetlib``.

        Note that ``telnetlib`` can be very noisy thus using the level ``NONE``
        can shutdown the messages generated by this library.
        """
        self._verify_connection()
        old = self._telnetlib_log_level
        self._set_telnetlib_log_level(level)
        return old

    def _set_telnetlib_log_level(self, level):
        if level.upper() == 'NONE':
            self._telnetlib_log_level = 'NONE'
        elif self._is_valid_log_level(level) is False:
            raise AssertionError("Invalid log level '%s'" % level)
        self._telnetlib_log_level = level.upper()

    def set_default_log_level(self, level):
        """Sets the default log level used for `logging` in the current connection.

        The old default log level is returned and can be used to restore the
        log level later.

        See `Configuration` section for more information about global and
        connection specific configuration.
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
        if level is None:
            return True
        if not is_string(level):
            return False
        return level.upper() in ('TRACE', 'DEBUG', 'INFO', 'WARN')

    def close_connection(self, loglevel=None):
        """Closes the current Telnet connection.

        Remaining output in the connection is read, logged, and returned.
        It is not an error to close an already closed connection.

        Use `Close All Connections` if you want to make sure all opened
        connections are closed.

        See `Logging` section for more information about log levels.
        """
        if self.sock:
            self.sock.shutdown(socket.SHUT_RDWR)
        self.close()
        output = self._decode(self.read_all())
        self._log(output, loglevel)
        return output

    def login(self, username, password, login_prompt='login: ',
              password_prompt='Password: ', login_timeout='1 second',
              login_incorrect='Login incorrect'):
        """Logs in to the Telnet server with the given user information.

        This keyword reads from the connection until the ``login_prompt`` is
        encountered and then types the given ``username``. Then it reads until
        the ``password_prompt`` and types the given ``password``. In both cases
        a newline is appended automatically and the connection specific
        timeout used when waiting for outputs.

        How logging status is verified depends on whether a prompt is set for
        this connection or not:

        1) If the prompt is set, this keyword reads the output until the prompt
        is found using the normal timeout. If no prompt is found, login is
        considered failed and also this keyword fails. Note that in this case
        both ``login_timeout`` and ``login_incorrect`` arguments are ignored.

        2) If the prompt is not set, this keywords sleeps until ``login_timeout``
        and then reads all the output available on the connection. If the
        output contains ``login_incorrect`` text, login is considered failed
        and also this keyword fails.

        See `Configuration` section for more information about setting
        newline, timeout, and prompt.
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
        # Using write_bare here instead of write because don't want to wait for
        # newline: https://github.com/robotframework/robotframework/issues/1371
        output = self.read_until(login_prompt, 'TRACE')
        self.write_bare(username + self._newline)
        output += self.read_until(password_prompt, 'TRACE')
        self.write_bare(password + self._newline)
        return output

    def _verify_login_without_prompt(self, delay, incorrect):
        time.sleep(timestr_to_secs(delay))
        output = self.read('TRACE')
        success = incorrect not in output
        return success, output

    def write(self, text, loglevel=None):
        """Writes the given text plus a newline into the connection.

        The newline character sequence to use can be [#Configuration|configured]
        both globally and per connection basis. The default value is ``CRLF``.

        This keyword consumes the written text, until the added newline, from
        the output and logs and returns it. The given text itself must not
        contain newlines. Use `Write Bare` instead if either of these features
        causes a problem.

        *Note:* This keyword does not return the possible output of the executed
        command. To get the output, one of the `Read ...` `keywords` must be
        used. See `Writing and reading` section for more details.

        See `Logging` section for more information about log levels.
        """
        newline = self._get_newline_for(text)
        if newline in text:
            raise RuntimeError("'Write' keyword cannot be used with strings "
                               "containing newlines. Use 'Write Bare' instead.")
        self.write_bare(text + newline)
        # Can't read until 'text' because long lines are cut strangely in the output
        return self.read_until(self._newline, loglevel)

    def _get_newline_for(self, text):
        if is_bytes(text):
            return self._encode(self._newline)
        return self._newline

    def write_bare(self, text):
        """Writes the given text, and nothing else, into the connection.

        This keyword does not append a newline nor consume the written text.
        Use `Write` if these features are needed.
        """
        self._verify_connection()
        telnetlib.Telnet.write(self, self._encode(text))

    def write_until_expected_output(self, text, expected, timeout,
                                    retry_interval, loglevel=None):
        """Writes the given ``text`` repeatedly, until ``expected`` appears in the output.

        ``text`` is written without appending a newline and it is consumed from
        the output before trying to find ``expected``. If ``expected`` does not
        appear in the output within ``timeout``, this keyword fails.

        ``retry_interval`` defines the time to wait ``expected`` to appear before
        writing the ``text`` again. Consuming the written ``text`` is subject to
        the normal [#Configuration|configured timeout].

        Both ``timeout`` and ``retry_interval`` must be given in `time string
        format`. See `Logging` section for more information about log levels.

        Example:
        | Write Until Expected Output | ps -ef| grep myprocess\\r\\n | myprocess |
        | ...                         | 5 s                          | 0.5 s     |

        The above example writes command ``ps -ef | grep myprocess\\r\\n`` until
        ``myprocess`` appears in the output. The command is written every 0.5
        seconds and the keyword fails if ``myprocess`` does not appear in
        the output in 5 seconds.
        """
        timeout = timestr_to_secs(timeout)
        retry_interval = timestr_to_secs(retry_interval)
        maxtime = time.time() + timeout
        while time.time() < maxtime:
            self.write_bare(text)
            self.read_until(text, loglevel)
            try:
                with self._custom_timeout(retry_interval):
                    return self.read_until(expected, loglevel)
            except AssertionError:
                pass
        raise NoMatchError(expected, timeout)

    def write_control_character(self, character):
        """Writes the given control character into the connection.

        The control character is prepended with an IAC (interpret as command)
        character.

        The following control character names are supported: BRK, IP, AO, AYT,
        EC, EL, NOP. Additionally, you can use arbitrary numbers to send any
        control character.

        Example:
        | Write Control Character | BRK | # Send Break command |
        | Write Control Character | 241 | # Send No operation command |
        """
        self._verify_connection()
        self.sock.sendall(telnetlib.IAC + self._get_control_character(character))

    def _get_control_character(self, int_or_name):
        try:
            ordinal = int(int_or_name)
            return bytes(bytearray([ordinal]))
        except ValueError:
            return self._convert_control_code_name_to_character(int_or_name)

    def _convert_control_code_name_to_character(self, name):
        code_names = {
                'BRK' : telnetlib.BRK,
                'IP' : telnetlib.IP,
                'AO' : telnetlib.AO,
                'AYT' : telnetlib.AYT,
                'EC' : telnetlib.EC,
                'EL' : telnetlib.EL,
                'NOP' : telnetlib.NOP
        }
        try:
            return code_names[name]
        except KeyError:
            raise RuntimeError("Unsupported control character '%s'." % name)

    def read(self, loglevel=None):
        """Reads everything that is currently available in the output.

        Read output is both returned and logged. See `Logging` section for more
        information about log levels.
        """
        self._verify_connection()
        output = self._decode(self.read_very_eager())
        if self._terminal_emulator:
            self._terminal_emulator.feed(output)
            output = self._terminal_emulator.read()
        self._log(output, loglevel)
        return output

    def read_until(self, expected, loglevel=None):
        """Reads output until ``expected`` text is encountered.

        Text up to and including the match is returned and logged. If no match
        is found, this keyword fails. How much to wait for the output depends
        on the [#Configuration|configured timeout].

        See `Logging` section for more information about log levels. Use
        `Read Until Regexp` if more complex matching is needed.
        """
        success, output = self._read_until(expected)
        self._log(output, loglevel)
        if not success:
            raise NoMatchError(expected, self._timeout, output)
        return output

    def _read_until(self, expected):
        self._verify_connection()
        if self._terminal_emulator:
            return self._terminal_read_until(expected)
        expected = self._encode(expected)
        output = telnetlib.Telnet.read_until(self, expected, self._timeout)
        return output.endswith(expected), self._decode(output)

    @property
    def _terminal_frequency(self):
        return min(self.INTERNAL_UPDATE_FREQUENCY, self._timeout)

    def _terminal_read_until(self, expected):
        max_time = time.time() + self._timeout
        output = self._terminal_emulator.read_until(expected)
        if output:
            return True, output
        while time.time() < max_time:
            output = telnetlib.Telnet.read_until(self, self._encode(expected),
                                                 self._terminal_frequency)
            self._terminal_emulator.feed(self._decode(output))
            output = self._terminal_emulator.read_until(expected)
            if output:
                return True, output
        return False, self._terminal_emulator.read()

    def _read_until_regexp(self, *expected):
        self._verify_connection()
        if self._terminal_emulator:
            return self._terminal_read_until_regexp(expected)
        expected = [self._encode(exp) if is_unicode(exp) else exp
                    for exp in expected]
        return self._telnet_read_until_regexp(expected)

    def _terminal_read_until_regexp(self, expected_list):
        max_time = time.time() + self._timeout
        regexps_bytes = [self._to_byte_regexp(rgx) for rgx in expected_list]
        regexps_unicode = [re.compile(self._decode(rgx.pattern))
                               for rgx in regexps_bytes]
        out = self._terminal_emulator.read_until_regexp(regexps_unicode)
        if out:
            return True, out
        while time.time() < max_time:
            output = self.expect(regexps_bytes, self._terminal_frequency)[-1]
            self._terminal_emulator.feed(self._decode(output))
            out = self._terminal_emulator.read_until_regexp(regexps_unicode)
            if out:
                return True, out
        return False, self._terminal_emulator.read()

    def _telnet_read_until_regexp(self, expected_list):
        expected = [self._to_byte_regexp(exp) for exp in expected_list]
        try:
            index, _, output = self.expect(expected, self._timeout)
        except TypeError:
            index, output = -1, b''
        return index != -1, self._decode(output)

    def _to_byte_regexp(self, exp):
        if is_bytes(exp):
            return re.compile(exp)
        if is_string(exp):
            return re.compile(self._encode(exp))
        pattern = exp.pattern
        if is_bytes(pattern):
            return exp
        return re.compile(self._encode(pattern))

    def read_until_regexp(self, *expected):
        """Reads output until any of the ``expected`` regular expressions match.

        This keyword accepts any number of regular expressions patterns or
        compiled Python regular expression objects as arguments. Text up to
        and including the first match to any of the regular expressions is
        returned and logged. If no match is found, this keyword fails. How much
        to wait for the output depends on the [#Configuration|configured timeout].

        If the last given argument is a [#Logging|valid log level], it is used
        as ``loglevel`` similarly as with `Read Until` keyword.

        See the documentation of
        [http://docs.python.org/library/re.html|Python re module]
        for more information about the supported regular expression syntax.
        Notice that possible backslashes need to be escaped in Robot Framework
        test data.

        Examples:
        | `Read Until Regexp` | (#|$) |
        | `Read Until Regexp` | first_regexp | second_regexp |
        | `Read Until Regexp` | \\\\d{4}-\\\\d{2}-\\\\d{2} | DEBUG |
        """
        if not expected:
            raise RuntimeError('At least one pattern required')
        if self._is_valid_log_level(expected[-1]):
            loglevel = expected[-1]
            expected = expected[:-1]
        else:
            loglevel = None
        success, output = self._read_until_regexp(*expected)
        self._log(output, loglevel)
        if not success:
            expected = [exp if is_string(exp) else exp.pattern
                        for exp in expected]
            raise NoMatchError(expected, self._timeout, output)
        return output

    def read_until_prompt(self, loglevel=None, strip_prompt=False):
        """Reads output until the prompt is encountered.

        This keyword requires the prompt to be [#Configuration|configured]
        either in `importing` or with `Open Connection` or `Set Prompt` keyword.

        By default, text up to and including the prompt is returned and logged.
        If no prompt is found, this keyword fails. How much to wait for the
        output depends on the [#Configuration|configured timeout].

        If you want to exclude the prompt from the returned output, set
        ``strip_prompt`` to a true value (see `Boolean arguments`). If your
        prompt is a regular expression, make sure that the expression spans the
        whole prompt, because only the part of the output that matches the
        regular expression is stripped away.

        See `Logging` section for more information about log levels.
        """
        if not self._prompt_is_set():
            raise RuntimeError('Prompt is not set.')
        success, output = self._read_until_prompt()
        self._log(output, loglevel)
        if not success:
            prompt, regexp = self._prompt
            raise AssertionError("Prompt '%s' not found in %s."
                                 % (prompt if not regexp else prompt.pattern,
                                    secs_to_timestr(self._timeout)))
        if is_truthy(strip_prompt):
            output = self._strip_prompt(output)
        return output

    def _read_until_prompt(self):
        prompt, regexp = self._prompt
        read_until = self._read_until_regexp if regexp else self._read_until
        return read_until(prompt)

    def _strip_prompt(self, output):
        prompt, regexp = self._prompt
        if not regexp:
            length = len(prompt)
        else:
            match = prompt.search(output)
            length = match.end() - match.start()
        return output[:-length]

    def execute_command(self, command, loglevel=None, strip_prompt=False):
        """Executes the given ``command`` and reads, logs, and returns everything until the prompt.

        This keyword requires the prompt to be [#Configuration|configured]
        either in `importing` or with `Open Connection` or `Set Prompt` keyword.

        This is a convenience keyword that uses `Write` and `Read Until Prompt`
        internally. Following two examples are thus functionally identical:

        | ${out} = | `Execute Command`   | pwd |

        | `Write`  | pwd                 |
        | ${out} = | `Read Until Prompt` |

        See `Logging` section for more information about log levels and `Read
        Until Prompt` for more information about the ``strip_prompt`` parameter.
        """
        self.write(command, loglevel)
        return self.read_until_prompt(loglevel, strip_prompt)

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

    def _negotiate_options(self, sock, cmd, opt):
        # We don't have state changes in our accepted telnet options.
        # Therefore, we just track if we've already responded to an option. If
        # this is the case, we must not send any response.
        if cmd in (telnetlib.DO, telnetlib.DONT, telnetlib.WILL, telnetlib.WONT):
            if (cmd, opt) in self._opt_responses:
                return
            else:
                self._opt_responses.append((cmd, opt))

        # This is supposed to turn server side echoing on and turn other options off.
        if opt == telnetlib.ECHO and cmd in (telnetlib.WILL, telnetlib.WONT):
            self._opt_echo_on(opt)
        elif cmd == telnetlib.DO and opt == telnetlib.TTYPE and self._terminal_type:
            self._opt_terminal_type(opt, self._terminal_type)
        elif cmd == telnetlib.DO and opt == telnetlib.NEW_ENVIRON and self._environ_user:
            self._opt_environ_user(opt, self._environ_user)
        elif cmd == telnetlib.DO and opt == telnetlib.NAWS and self._window_size:
            self._opt_window_size(opt, *self._window_size)
        elif opt != telnetlib.NOOPT:
            self._opt_dont_and_wont(cmd, opt)

    def _opt_echo_on(self, opt):
        return self.sock.sendall(telnetlib.IAC + telnetlib.DO + opt)

    def _opt_terminal_type(self, opt, terminal_type):
        self.sock.sendall(telnetlib.IAC + telnetlib.WILL + opt)
        self.sock.sendall(telnetlib.IAC + telnetlib.SB + telnetlib.TTYPE
                          + self.NEW_ENVIRON_IS + terminal_type
                          + telnetlib.IAC + telnetlib.SE)

    def _opt_environ_user(self, opt, environ_user):
        self.sock.sendall(telnetlib.IAC + telnetlib.WILL + opt)
        self.sock.sendall(telnetlib.IAC + telnetlib.SB + telnetlib.NEW_ENVIRON
                          + self.NEW_ENVIRON_IS + self.NEW_ENVIRON_VAR
                          + b"USER" + self.NEW_ENVIRON_VALUE + environ_user
                          + telnetlib.IAC + telnetlib.SE)

    def _opt_window_size(self, opt, window_x, window_y):
        self.sock.sendall(telnetlib.IAC + telnetlib.WILL + opt)
        self.sock.sendall(telnetlib.IAC + telnetlib.SB + telnetlib.NAWS
                          + struct.pack('!HH', window_x, window_y)
                          + telnetlib.IAC + telnetlib.SE)

    def _opt_dont_and_wont(self, cmd, opt):
        if cmd in (telnetlib.DO, telnetlib.DONT):
            self.sock.sendall(telnetlib.IAC + telnetlib.WONT + opt)
        elif cmd in (telnetlib.WILL, telnetlib.WONT):
            self.sock.sendall(telnetlib.IAC + telnetlib.DONT + opt)

    def msg(self, msg, *args):
        # Forward telnetlib's debug messages to log
        if self._telnetlib_log_level != 'NONE':
            logger.write(msg % args, self._telnetlib_log_level)

    def _check_terminal_emulation(self, terminal_emulation):
        if not terminal_emulation:
            return False
        if not pyte:
            raise RuntimeError("Terminal emulation requires pyte module!\n"
                               "http://pypi.python.org/pypi/pyte/")
        return TerminalEmulator(window_size=self._window_size,
                                newline=self._newline)


class TerminalEmulator(object):

    def __init__(self, window_size=None, newline="\r\n"):
        self._rows, self._columns = window_size or (200, 200)
        self._newline = newline
        self._stream = pyte.Stream()
        self._screen = pyte.HistoryScreen(self._rows,
                                          self._columns,
                                          history=100000)
        self._stream.attach(self._screen)
        self._buffer = ''
        self._whitespace_after_last_feed = ''

    @property
    def current_output(self):
        return self._buffer + self._dump_screen()

    def _dump_screen(self):
        return self._get_history(self._screen) + \
               self._get_screen(self._screen) + \
               self._whitespace_after_last_feed

    def _get_history(self, screen):
        if not screen.history.top:
            return ''
        rows = []
        for row in screen.history.top:
            # Newer pyte versions store row data in mappings
            data = (char.data for _, char in sorted(row.items()))
            rows.append(''.join(data).rstrip())
        return self._newline.join(rows).rstrip(self._newline) + self._newline

    def _get_screen(self, screen):
        rows = (row.rstrip() for row in screen.display)
        return self._newline.join(rows).rstrip(self._newline)

    def feed(self, text):
        self._stream.feed(text)
        self._whitespace_after_last_feed = text[len(text.rstrip()):]

    def read(self):
        current_out = self.current_output
        self._update_buffer('')
        return current_out

    def read_until(self, expected):
        current_out = self.current_output
        exp_index = current_out.find(expected)
        if exp_index != -1:
            self._update_buffer(current_out[exp_index+len(expected):])
            return current_out[:exp_index+len(expected)]
        return None

    def read_until_regexp(self, regexp_list):
        current_out = self.current_output
        for rgx in regexp_list:
            match = rgx.search(current_out)
            if match:
                self._update_buffer(current_out[match.end():])
                return current_out[:match.end()]
        return None

    def _update_buffer(self, terminal_buffer):
        self._buffer = terminal_buffer
        self._whitespace_after_last_feed = ''
        self._screen.reset()


class NoMatchError(AssertionError):
    ROBOT_SUPPRESS_NAME = True

    def __init__(self, expected, timeout, output=None):
        self.expected = expected
        self.timeout = secs_to_timestr(timeout)
        self.output = output
        AssertionError.__init__(self, self._get_message())

    def _get_message(self):
        expected = "'%s'" % self.expected \
                   if is_string(self.expected) \
                   else seq2str(self.expected, lastsep=' or ')
        msg = "No match found for %s in %s." % (expected, self.timeout)
        if self.output is not None:
            msg += ' Output:\n%s' % self.output
        return msg
