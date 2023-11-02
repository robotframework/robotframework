*** Settings ***
Library           LogLevels.py

*** Test Cases ***
Log messages are collected on INFO level by default
    Keyword
    Logged messages should be
    ...    INFO: Message
    ...    WARN: Warning

Log messages are collected on level set using '--loglevel'
    Keyword
    Logged messages should be
    ...    WARN: Warning

Log messages are collected on level set using 'Set Log Level'
    ${old} =    Set Log Level    DEBUG
    Keyword
    Logged messages should be
    ...    DEBUG: Log level changed from ${old} to DEBUG.
    ...    INFO: \${old} = ${old}
    ...    INFO: Message
    ...    DEBUG: Debug message
    ...    WARN: Warning

*** Keywords ***
Keyword
    Log    Message
    Log    Debug message   level=DEBUG
    Log    Trace message   level=TRACE
    Log    Warning    level=WARN
