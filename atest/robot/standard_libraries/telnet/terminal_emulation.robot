*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/telnet/terminal_emulation.robot
Resource          telnet_resource.robot

*** Test Cases ***
Execute command
    Check Test Case    ${TEST NAME}

Read Until Regex
    Check Test Case    ${TEST NAME}

Read Until Multiple Regexp
    Check Test Case    ${TEST NAME}

Read Until Precompiled Regexp
    Check Test Case    ${TEST NAME}

Read Until Non-ASCII Regexp
    Check Test Case    ${TEST NAME}

Reads Only the Necessary Amount
    Check Test Case    ${TEST NAME}

Reads Only the Necessary Amount with rewrites
    Check Test Case    ${TEST NAME}

Empties buffer on not found read until
    Check Test Case    ${TEST NAME}

Empties buffer on not found read until regexp
    Check Test Case    ${TEST NAME}

Read
    Check Test Case    ${TEST NAME}

Read Until Reads Using Internal Update Frequency
    Check Test Case    ${TEST NAME}

Read Until Regexp Using Internal Update Frequency
    Check Test Case    ${TEST NAME}

Window Size
    Check Test Case    ${TEST NAME}

Override terminal emulation and type
    Check Test Case    ${TEST NAME}

Pagination
    Check Test Case    ${TEST NAME}

Lots and lots of pages
    Check Test Case    ${TEST NAME}

Write & Read Non-ASCII
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    echo Hyvää yötä    WARN
    Check Log Message    ${tc.kws[1].msgs[0]}    Hyvää yötä\n${FULL PROMPT}    DEBUG

Write & Read non-ISO-LATIN-1
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    echo \u2603    WARN
    Check Log Message    ${tc.kws[1].msgs[0]}    \u2603\n${FULL PROMPT}    DEBUG

Write ASCII-Only Unicode When Encoding Is ASCII
    Check Test Case    ${TEST NAME}

Encoding can not be changed in terminal encoding
    Check Test Case    ${TEST NAME}

Newline can not be changed in terminal encoding
    Check Test Case    ${TEST NAME}
