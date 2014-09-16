*** Setting ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/telnet/configuration.robot
Force Tags        jybot    pybot
Resource          telnet_resource.robot

*** Test Case ***
Library Default Window Size
    Check Test Case    ${TEST NAME}

Set Window Size
    Check Test Case    ${TEST NAME}

Set Invalid Window Size
    Check Test Case    ${TEST NAME}

Set User Environ Option
    Check Test Case    ${TEST NAME}

Default terminal type is network
    Check Test Case    ${TEST NAME}

Set terminal type
    Check Test Case    ${TEST NAME}

Prompt Set In Init
    Check Test Case    ${TEST NAME}

Prompt Set In Open Connection
    Check Test Case    ${TEST NAME}

Set Prompt Keyword
    Check Test Case    ${TEST NAME}

Timeout Set In Init
    Check Test Case    ${TEST NAME}

Timeout Set In Open Connection
    Check Test Case    ${TEST NAME}

Set Timeout Keyword
    Check Test Case    ${TEST NAME}

Newline Set In Init
    Check Test Case    ${TEST NAME}

Newline Set In Open Connection
    Check Test Case    ${TEST NAME}

Set Newline Keyword
    Check Test Case    ${TEST NAME}

Encoding Set In Init
    Check Test Case    ${TEST NAME}

Encoding Set In Open Connection
    Check Test Case    ${TEST NAME}

Set Encoding Keyword
    Check Test Case    ${TEST NAME}

Use Configured Encoding
    Check Test Case    ${TEST NAME}

Disable Encoding
    Check Test Case    ${TEST NAME}

Default Log Level In Init
    Check Test Case    ${TEST NAME}

Default Log Level In Open Connection
    Check Test Case    ${TEST NAME}

Set Default Log Level Keyword
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[2].msgs[0]}    pwd    DEBUG
    Check Log Message    ${tc.kws[5].msgs[0]}    ${HOME}\n${FULL PROMPT}    WARN

Configuration fails if there is no connection
    Check Test Case    ${TEST NAME}

Default configuration
    Check Test Case    ${TEST NAME}

Telnetlib's Debug Messages Are Logged On Trace Level
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].msgs[1]}    send 'echo hyv\\xc3\\xa4\\r\\n'    TRACE
    Check Log Message    ${tc.kws[1].msgs[2]}    recv 'e*'    TRACE    pattern=yep
