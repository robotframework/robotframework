class LoggingLibrary:
    """Library for logging messages.

    = Table of contents =

    %TOC%

    = Usage =

    This library has several keyword, for example `Log Message`, for logging
    messages. In reality the library is used only for _Libdoc_ demonstration
    purposes.

    = Valid log levels =

    Valid log levels are ``INFO``, ``DEBUG``, and ``TRACE``. The default log
    level can be set during `importing`.

    = Examples =

    Notice how keywords are linked from examples.

    | `Log Message`      | My message    |                |               |
    | `Log Two Messages` | My message    | Second message | level=DEBUG   |
    | `Log Messages`     | First message | Second message | Third message |
    """
    ROBOT_LIBRARY_VERSION = '0.1'

    def __init__(self, default_level='INFO'):
        """The default log level can be given at library import time.

        See `Valid log levels` section for information about available log
        levels.

        Examples:

        | =Setting= |     =Value=    | =Value= |          =Comment=         |
        | Library   | LoggingLibrary |         | # Use default level (INFO) |
        | Library   | LoggingLibrary | DEBUG   | # Use the given level      |
        """
        self.default_level = self._verify_level(default_level)

    def _verify_level(self, level):
        level = level.upper()
        if level not in ['INFO', 'DEBUG', 'TRACE']:
            raise RuntimeError("Invalid log level'%s'. Valid levels are "
                               "'INFO', 'DEBUG', and 'TRACE'")
        return level

    def log_message(self, message, level=None):
        """Writes given message to the log file using the specified log level.

        The message to log and the log level to use are defined using
        ``message`` and ``level`` arguments, respectively.

        If no log level is given, the default level given during `library
        importing` is used.
        """
        level = self._verify_level(level) if level else self.default_level
        print("*%s* %s" % (level, message))

    def log_two_messages(self, message1, message2, level=None):
        """Writes given messages to the log file using the specified log level.

        See `Log Message` keyword for more information.
        """
        self.log_message(message1, level)
        self.log_message(message2, level)

    def log_messages(self, *messages):
        """Logs given messages using the log level set during `importing`.

        See also `Log Message` and `Log Two Messages`.
        """
        for msg in messages:
            self.log_message(msg)
