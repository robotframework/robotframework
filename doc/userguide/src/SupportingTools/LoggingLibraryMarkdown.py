class LoggingLibraryMarkdown:
    """Library for logging messages.

    This documentation is formatted using Markdown.

    %TOC%

    # Usage

    This library has several keyword, for example [Log Message], for logging
    messages. In reality the library is used only for *Libdoc* demonstration
    purposes.

    # Valid log levels

    Valid log levels are `INFO`, `DEBUG` and `TRACE`. The default log level
    can be set during [importing].

    # Example

    ```robotframework
    *** Settings ***
    Library        LoggingLibrary

    *** Test Cases ***
    Use default level
        Log Message    My message

    Use custom level
        Log Message    My message    level=DEBUG

    Log multiple messages
        Log Messages    First message    Second message    Third message
    ```

    !!! note
        Internal linking does not work in examples when using Markdown code blocks.
        Syntax highlighting works, though.
    """

    ROBOT_LIBRARY_DOC_FORMAT = "Markdown"
    ROBOT_LIBRARY_VERSION = "0.2"

    def __init__(self, default_level: str = "INFO"):
        """The default log level can be given at the library import time.

        Args:

            default_level: Default log level. See the [Valid log levels]
                section for more information about available log levels.

        Examples:

        ```robotframework
        *** Settings ***
        Library        LoggingLibrary             # Use the default level (INFO)
        Library        LoggingLibrary    DEBUG    # Use the given level
        ```
        """
        self.default_level = self._verify_level(default_level)

    def _verify_level(self, level: str) -> str:
        level = level.upper()
        if level not in ("INFO", "DEBUG", "TRACE"):
            raise RuntimeError(
                f"Level must be 'INFO', 'DEBUG' or 'TRACE', got '{level}'."
            )
        return level

    def log_message(self, message: str, level: str | None = None):
        """Writes given message to the log file using the specified log level.

        Args:
            message: The message to log.
            level: The log level to use. If not given, the default level given
                during [library importing] is used.

        Use the [Log Messages] keyword if you want to log multiple messages at
        the same time.
        """
        level = self._verify_level(level) if level else self.default_level
        print(f"*{level}* {message}")

    def log_messages(self, *messages):
        """Logs given messages using the log level set during `importing`.

        Args:
            *messages: The messages to log.

        Use the [Log Message] keyword if you want to control the log level.
        """
        for msg in messages:
            self.log_message(msg)
