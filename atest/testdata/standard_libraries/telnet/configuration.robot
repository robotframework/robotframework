*** Setting ***
Test Setup        Open Connection    ${HOST}
Test Teardown     Close All Connections
Library           Telnet    3.142    CRLF    $    REGEXP    ASCII    strict    DeBuG     window_size=95x95   terminal_emulation=NO
Library           String
Resource          telnet_resource.robot

*** Test Cases ***
Library Default Window Size
    [setup]    Login and set prompt
    Set Timeout    0.3 seconds    # Must set after login to give login time to succeed
    Window Size Should Be    95    95

Set Window Size
    [setup]    Open Connection    ${HOST}    prompt=${PROMPT}    window_size=100x100
    Login    ${USERNAME}    ${PASSWORD}
    Set Timeout    0.3 seconds    # Must set after login to give login time to succeed
    Window Size Should Be    100    100

Set Invalid Window Size
    [Documentation]    FAIL ValueError: Invalid window size '100yx100'. Should be <rows>x<columns>.
    [setup]
    Open Connection    ${HOST}    prompt=${PROMPT}    window_size=100yx100

Set User Environ Option
    [setup]     Open Connection    ${HOST}    prompt=${PROMPT}    environ_user=${USERNAME}
    Verify Successful Login With User Option

Default terminal type is network
    [setup]     Login and set prompt
    Environment variable should be    $TERM    network

Set terminal type
    [setup]   Login and set prompt    terminal_type=vt100   terminal_emulation=True
    Environment variable should be    $TERM    vt100

Prompt Set In Init
    Prompt Should Be    $    ${TRUE}

Prompt Set In Open Connection
    [setup]    Open Connection    ${HOST}    prompt=xxx
    Prompt Should Be    xxx    ${FALSE}
    Open Connection    ${HOST}    ${EMPTY}    ${EMPTY}    ${EMPTY}    ${EMPTY}
    ...    prompt    regexp
    Prompt Should Be    prompt    ${TRUE}

Set Prompt Keyword
    Set Prompt    >-<
    Prompt Should Be    >-<    ${FALSE}
    Set Prompt    >\\s+    regexp
    Prompt Should Be    >\\s+    ${TRUE}

Timeout Set In Init
    Timeout Should Be    3 seconds 142 milliseconds

Timeout Set In Open Connection
    [setup]    Open Connection    ${HOST}    timeout=0.5s
    Timeout Should Be    500 milliseconds
    Open Connection    ${HOST}    ${EMPTY}    ${EMPTY}    61
    Timeout Should Be    1 minute 1 second

Set Timeout Keyword
    [Documentation]    FAIL STARTS: No match found for 'Not found' in 42 milliseconds. Output:\n
    Set Timeout    1 h 2 min 3 secs
    Timeout Should Be    1 hour 2 minutes 3 seconds
    Set Timeout    0.042
    Read Until    Not found

Newline Set In Init
    Newline Should Be    \r\n

Newline Set In Open Connection
    [setup]    Open Connection    ${HOST}    newline=LF
    Newline Should Be    \n
    Open Connection    ${HOST}    ${EMPTY}    ${EMPTY}    ${EMPTY}    CR
    Newline Should Be    \r

Set Newline Keyword
    Set Newline    LF\rFOO
    Newline Should Be    \n\rFOO

Encoding Set In Init
    Encoding Should Be    ASCII    strict

Encoding Set In Open Connection
    [setup]    Open Connection    ${HOST}    encoding=ISO-8859-15    encoding_errors=xxx
    Encoding Should Be    ISO-8859-15    xxx
    Open Connection    ${HOST}    encoding=Latin1
    Encoding Should Be    LATIN1    strict

Set Encoding Keyword
    Set Encoding    us-ascii
    Encoding Should Be    US-ASCII    strict
    Set Encoding    xXx    yYy
    Encoding Should Be    XXX   yYy
    Set Encoding    encoding=ASCII
    Encoding Should Be    ASCII   yYy
    Set Encoding    errors=ignore
    Encoding Should Be    ASCII   ignore

Use Configured Encoding
    [setup]   Login and set prompt
    Run Keyword And Expect Error    UnicodeEncodeError:*    Write    echo päivää
    Set Encoding    errors=ignore
    Write    echo hyvää päivää
    Read Until    hyv piv
    Set Encoding    UTF-8
    Write    echo hyvää päivää
    Read Until    hyvää päivää

Disable Encoding
    [setup]   Login and set prompt
    Set Encoding    none    whatever
    Encoding Should Be    NONE    whatever
    Write    hello
    Set Timeout    0.6 seconds    # this specific test is flickering sometimes
    ${out} =    Read Until Prompt
    Should Be Byte String    ${out}

Default Log Level In Init
    Default Log Level Should Be    DEBUG

Default Log Level In Open Connection
    [setup]   Open Connection    ${HOST}    default_log_level=trace
    Default Log Level Should Be    TRACE

Set Default Log Level Keyword
    [Documentation]    FAIL Invalid log level 'Invalid'
    [Setup]    Login And Set Prompt
    Set Default Log Level    debug
    Default Log Level Should Be    DEBUG
    Write    pwd
    Set Default Log Level    WARN
    Default Log Level Should Be    WARN
    Read Until Prompt
    Set Default log Level    Invalid

Default Telnetlib Log Level In Init
    Telnetlib Log Level Should Be    TRACE
    Write    pwd
    Read Until Prompt

Default Telnetlib Log Level In Open Connection
    [setup]   Open Connection    ${HOST}
    Telnetlib Log Level Should Be    TRACE
    Write    pwd
    Read Until Prompt

Telnetlib Log Level NONE In Open Connection
    [setup]   Open Connection    ${HOST}  telnetlib_log_level=NONE
    Telnetlib Log Level Should Be    NONE
    Write    pwd
    Read Until Prompt

Telnetlib Log Level DEBUG In Open Connection
    [setup]   Open Connection    ${HOST}  telnetlib_log_level=DEBUG
    Telnetlib Log Level Should Be    DEBUG
    Write    pwd
    Read Until Prompt

Set Telnetlib Log Level Keyword
    [Documentation]    FAIL Invalid log level 'Invalid'
    [Setup]    Login And Set Prompt
    Set Telnetlib Log Level    TRACE
    Write    pwd
    Read Until Prompt
    Set Telnetlib Log Level    NONE
    Write    pwd
    Read Until Prompt
    Set Telnetlib Log Level    DEBUG
    Write    pwd
    Read Until Prompt
    Set Telnetlib log Level    Invalid

Configuration fails if there is no connection
    [Setup]    NONE
    [Template]    Should fail because no connection
    Set Prompt    $
    Set Timeout    1s
    Set Newline    LF
    Set Encoding    ASCII
    Set Default Log Level    DEBUG
    Set Telnetlib Log Level    DEBUG

Default configuration
    [Setup]    NONE
    Import Library    Telnet    WITH NAME    Default
    Set Library Search Order    Default
    Open Connection    ${HOST}
    Prompt Should Be    ${NONE}    ${FALSE}
    Timeout Should Be    3 seconds
    Newline Should Be    \r\n
    Encoding Should Be    UTF-8    ignore
    Default Log Level Should Be    INFO
    [Teardown]    Set Library Search Order    Telnet

Telnetlib's Debug Messages Are Logged On Trace Level
    [Setup]    Login And Set Prompt    encoding=UTF-8
    Set Log Level    TRACE
    Write    echo hyvä
    ${out} =    Read Until Prompt
    Should Start With    ${out}    hyvä
    [Teardown]    Set Log Level    DEBUG

Telnetlib's Debug Messages Are Not Logged On Log Level None
    [Setup]    Login And Set Prompt    encoding=UTF-8
    Set Telnetlib Log Level    NONE
    Write    echo hyvä
    ${out} =    Read Until Prompt
    Should Start With    ${out}    hyvä
    [Teardown]    Set Telnetlib Log Level    TRACE

*** Keywords ***
Prompt Should Be
    [Arguments]    ${expected prompt}    ${expected regexp}
    ${prompt}    ${regexp} =    Set Prompt    prompt
    Should Be Equal    ${prompt}    ${expected prompt}
    Should Be Equal    ${regexp}    ${expected regexp}
    ${prompt}    ${regexp} =    Set Prompt    ${prompt}    ${regexp}
    Should Be Equal    ${prompt}    prompt
    Should Be Equal    ${regexp}    ${FALSE}

Timeout Should Be
    [Arguments]    ${expected}
    ${timeout} =    Set Timeout    61.5
    Should Be Equal    ${timeout}    ${expected}
    ${timeout} =    Set Timeout    ${timeout}
    Should Be Equal    ${timeout}    1 minute 1 second 500 milliseconds

Newline Should Be
    [Arguments]    ${expected}
    ${newline} =    Set Newline    CRLF
    Should Be Equal    ${newline}    ${expected}
    ${newline} =    Set Newline    ${newline}
    Should Be Equal    ${newline}    \r\n

Encoding Should Be
    [Arguments]    ${expected encoding}    ${expected errors}
    ${encoding}    ${errors} =    Set Encoding    ASCII    ignore
    Should Be Equal    ${encoding}    ${expected encoding}
    Should Be Equal    ${errors}    ${expected errors}
    ${encoding}    ${errors} =    Set Encoding    ${encoding}    ${errors}
    Should Be Equal    ${encoding}    ASCII
    Should Be Equal    ${errors}    ignore

Default Log Level Should Be
    [Arguments]    ${expected}
    ${level} =    Set Default Log Level    WARN
    Should Be Equal    ${level}    ${expected}
    ${level} =    Set Default Log Level    ${level}
    Should Be Equal    ${level}    WARN

Telnetlib Log Level Should Be
    [Arguments]    ${expected}
    ${level} =    Set Telnetlib Log Level    WARN
    Should Be Equal    ${level}    ${expected}
    ${level} =    Set Telnetlib Log Level    ${level}
    Should Be Equal    ${level}    WARN

Window Size Should Be
    [Arguments]    ${expected rows}    ${expected columns}
    ${output}=   Execute Command    stty -a
    Should Contain    ${output}    rows ${expected rows}; columns ${expected columns}    Window size does not match!

Verify Successful Login With User Option
    Read Until    Password:
    Write   ${PASSWORD}
    Read Until Prompt
