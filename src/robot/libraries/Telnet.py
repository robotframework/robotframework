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


import telnetlib
import time
import re
from types import MethodType, StringTypes

from robot import utils


class Telnet:

    """Test library providing Telnet connections and communicating with them.

    This library takes optional arguments timeout, newline, regexp and 
    regexp_is_prompt. These are default values used when a new connection is
    opened with keyword 'Open', and can be overridden. The meaning of these 
    parameters can be found from the documentation of 'Open'.  
    
    Examples (use only one of these):

    | Library | Telnet |     |    |     |    | # default values                |
    | Library | Telnet | 0.5 |    |     |    | # set only timeout              |
    | Library | Telnet |     | LF |     |    | # set only newline              |
    | Library | Telnet | 2.0 | LF |     |    | # set timeout and newline       |
    | Library | Telnet | 2.0 | LF | $   |    | # set also prompt               |
    | Library | Telnet | 2.0 | LF | ($|~) | True | # set prompt with simple regexp |
    """

    ROBOT_LIBRARY_SCOPE = 'TEST_SUITE'

    def __init__(self, timeout=3.0, newline='CRLF', 
                 prompt=None, prompt_is_regexp=False):
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
                              and type(getattr(self,name)) is MethodType ]
        return self._lib_kws
    
    def _get_connection_keywords(self):
        if self._conn_kws is None:
            conn = self._get_connection()
            excluded = [ name for name in dir(telnetlib.Telnet()) 
                         if name not in ['write', 'read', 'read_until'] ]
            self._conn_kws = [ name for name in dir(conn)
                               if not name.startswith('_') and name not in excluded
                               and type(getattr(conn,name)) is MethodType ]
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
        """Opens a new Telnet connection to given host and port.

        Possible already opened connections are cached.

        Returns the index of this connection which can be used later to switch
        back to it. Index starts from 1 and is reset back to it when Close All
        keyword is used.

        Optional alias is a name for the connection and it can be used for
        switching between connections similarly as the index. See Switch
        Connection for more details about that.

        Timeout newline and prompt attributes got default values when the 
        library was taken into use but they can be overridden for each opened 
        connection and also set after opening the connection using 
        Set Timeout, Set Newline and Set Prompt keywords.
        
        Timeout is used with keywords that start 'Read Until'. If the text they
        are looking for is not found within timeout, the keywords will fail.
        
        Newline is the newline character in the target system.
        
        Prompt is the prompt character of the taget system, and can be given
        as a regular expression when promp_is_regexp is set to True.
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
        """Switches between active connections using index or alias.

        Index is got from Open keywords and alias can be given to it.

        Example:

        | Open              | myhost.net   |          |
        | Login             | john         | secret   |
        | Write             | some command |          |
        | Open              | yourhost.com | 2nd conn |
        | Login             | root         | password |
        | Write             | another cmd  |          |
        | Switch Connection | 1            | # index  |
        | Write             | something    |          |
        | Switch Connection | 2nd conn     | # alias  |
        | Write             | whatever     |          |
        | Close All         |              |          |

        Above example expects that there was no other open connections when
        opening the first one because it used index '1' when switching to it
        later. If you are not sure about that, you can store the index into
        a variable as shown below.

        | ${id} =           | Open         | myhost.net |
        | # Do something ... |
        | Switch Connection | ${id}        |            |
        """
        self._conn = self._cache.switch(index_or_alias)

    def close_all_connections(self):
        """Closes all open connections and empties the connection cache.

        After this keyword new indexes get from Open keyword are reset to 1.

        This keyword ought to be used in test or suite teardown to make sure
        all connections are closed.
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

    def set_timeout(self, timeout):
        """Sets the timeout used in read operations to given value.

        'timeout' is given in Robot's time format (e.g. 1 minute 20 seconds).

        The read operations will wait for this time before starting to read 
        from the output. To run operations that take a long time to generate 
        their complete output, this timeout must be set accordingly.
        
        Old timeout is returned and it can be used to restore it later.
        
        Example:
        | ${tout} = | Set Timeout | 2 minute 30 seconds |
        | Do Something |
        | Set Timeout | ${tout} |
        """
        old = hasattr(self, '_timeout') and self._timeout or 3.0
        self._timeout = utils.timestr_to_secs(timeout)
        return utils.secs_to_timestr(old)

    def set_newline(self, newline):
        """Sets the newline used by 'Write' keyword.
        
        Old newline is returned and it can be used to restore it later.
        See 'Set Timeout' for an example. 
        """
        old = hasattr(self, '_newline') and self._newline or 'CRLF'
        self._newline = newline.upper().replace('LF','\n').replace('CR','\r')
        return old

    def close_connection(self, loglevel=None):
        """Closes current Telnet connection and returns any remaining output.

        See 'Read' for more information on 'loglevel'.
        """
        telnetlib.Telnet.close(self)
        ret = self.read_all().decode('ASCII', 'replace')
        self._log(ret, loglevel)
        return ret

    def login(self, username, password, login_prompt='login: ',
              password_prompt='Password: '):
        """Logs in to Telnet server with given user information.

        The login keyword reads from the connection until login_prompt is
        encountered and then types the username. Then it reads until
        password_prompt is encountered and types the password. The rest of the
        output (if any) is also read and all text that has been read is
        returned as a single string.
        
        If prompt has been set to this connection, either with 'Open Connection'
        or 'Set Prompt', this keyword reads output until the prompt is found.
        Otherwise, keyword sleeps for a second and reads everything that is
        available.
        """
        ret = self.read_until(login_prompt, 'TRACE')
        self.write_bare(username + self._newline)
        ret += username + '\n'
        ret += self.read_until(password_prompt, 'TRACE')
        self.write_bare(password + self._newline)
        ret += '*' * len(password) + '\n'
        if self._prompt_is_set():
            ret += self.read_until_prompt('TRACE')
        else:
            time.sleep(1)
            ret += self.read('TRACE')
        self._log(ret)
        return ret

    def write(self, text, loglevel=None):
        """Writes given text over the connection and appends newline.
        
        Consumes the written text (until the appended newline) from output 
        and returns it. Given text must not contain newlines.
        
        Note: This keyword does not return the possible output of the executed 
        command. To get the output, one of the 'Read XXX' keywords must be 
        used.
        """
        if self._newline in text:
            raise RuntimeError("Write cannot be used with string containing " 
                               "newlines. Use 'Write Bare' instead.")
        text += self._newline
        self.write_bare(text)
        # Can't read until 'text' because long lines are cut strangely in the output
        return self.read_until(self._newline, loglevel)

    def write_bare(self, text):
        """Writes given text over the connection without appending newline.
        
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
        """Writes given text repeatedly until 'expected' appears in output.
        
        'text' is written without appending newline. 'retry_interval' defines
        the time that is waited before writing 'text' again. 'text' will be
        consumed from the output before 'expected' is tried to be read. 
        
        If 'expected' does not appear on output within 'timeout', this keyword
        fails. 
        
        See 'Read' for more information on 'loglevel'.
        
        Example:
        | Write Until Expected Output | ps -ef| grep myprocess\\n | myprocess |
        | ... | 5s | 0.5s |
        
        This will write the 'ps -ef | grep myprocess\\n' until 'myprocess' 
        appears on the output. The command is written every 0.5 seconds and 
        the keyword will fail if 'myprocess' does not appear on the output in
        5 seconds.
        
        New in Robot 1.8.2.
        """
        timeout = utils.timestr_to_secs(timeout)
        retry_interval = utils.timestr_to_secs(retry_interval)
        starttime = time.time()
        while time.time() - starttime < timeout:
            self.write_bare(text)
            self.read_until(text, loglevel)
            ret = telnetlib.Telnet.read_until(self, expected, 
                                              retry_interval).decode('ASCII', 'replace')
            self._log(ret, loglevel)
            if ret.endswith(expected):
                return ret
        raise AssertionError("No match found for '%s' in %s" 
                             % (expected, utils.secs_to_timestr(timeout)))

    def read(self, loglevel=None):
        """Reads and returns/logs everything currently available on the output.

        Read message is always returned and logged. Default log level is 
        either 'INFO', or the level set with 'Set Default Log Level'.
        'loglevel' can be used to override the default log level, and available
        levels are TRACE, DEBUG, INFO and WARN.
        """
        ret = self.read_very_eager().decode('ASCII', 'replace')
        self._log(ret, loglevel)
        return ret

    def read_until(self, expected, loglevel=None):
        """Reads from the current output until expected is encountered.

        Text up until and including the match will be returned, If no match is
        found, the keyword fails.
        
        See 'Read' for more information on 'loglevel'.
        """
        ret = telnetlib.Telnet.read_until(self, expected, 
                                          self._timeout).decode('ASCII', 'replace')
        self._log(ret, loglevel)
        if not ret.endswith(expected):
            raise AssertionError("No match found for '%s' in %s" 
                                 % (expected, utils.secs_to_timestr(self._timeout)))
        return ret

    def read_until_regexp(self, *expected):
        """Reads from the current output until a match to a regexp in expected.

        Expected is a list of regular expressions, and keyword returns the text
        up until and including the first match to any of the regular
        expressions.
        
        If the last argument in *excpected is a valid log level, it is used
        as 'loglevel' in keyword 'Read'.
        
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
        ret = ret.decode('ASCII', 'replace')
        self._log(ret, loglevel)
        if index == -1:
            expected = [ type(exp) in StringTypes and exp or exp.pattern 
                         for exp in expected ]
            raise AssertionError("No match found for %s in %s"
                                 % (utils.seq2str(expected, lastsep=' or '),
                                    utils.secs_to_timestr(self._timeout)))
        return ret

    def read_until_prompt(self, loglevel=None):
        """Reads from the current output until prompt is found.
        
        Prompt must have been set, either in Library import or at login time, 
        or by using 'Set Prompt' -keyword.
        
        See 'Read' for more information on 'loglevel'.
        """
        if not self._prompt_is_set():
            raise RuntimeError('Prompt is not set')
        prompt, regexp = self._prompt
        if regexp:
            return self.read_until_regexp(prompt, loglevel)
        return self.read_until(prompt, loglevel)

    def set_prompt(self, prompt, prompt_is_regexp=False):
        """Sets the prompt used in this connection to 'prompt'.
        
        If 'prompt_is_regexp' is any non-empty string, the given prompt is 
        considered to be a regular expression.
        
        Old prompt is returned and it can be used to restore it later.
        
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
        """Sets the default log loglevel used by all read keywords.
        
        Possible values are TRACE, DEBUG, INFO and WARN. Default is INFO.
        Old value is returned and it can be used to restore it later, similarly
        as with 'Set Timeout'.
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
        if type(level) in StringTypes and \
                level.upper() in ['TRACE', 'DEBUG', 'INFO', 'WARN']:
            return True
        if not raise_if_invalid:
            return False
        raise AssertionError("Invalid log level '%s'" % level)
