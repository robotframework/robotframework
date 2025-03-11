*** Settings ***
Suite Setup       Run Tests    --loglevel DEBUG    standard_libraries/telnet/read_and_write.robot
Resource          telnet_resource.robot

*** Test Cases ***
Write & Read
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}    pwd
    Check Log Message    ${tc[3, 0]}    ${HOME}\n${FULL PROMPT}

Write & Read Non-ASCII
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}    echo Hyvää yötä    WARN
    Check Log Message    ${tc[2, 0]}    Hyvää yötä\n${FULL PROMPT}    DEBUG

Write & Read Non-ASCII Bytes
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[2, 0]}    echo Hyv\\xc3\\xa4\\xc3\\xa4 y\\xc3\\xb6t\\xc3\\xa4
    Check Log Message    ${tc[3, 0]}    Hyv\\xc3\\xa4\\xc3\\xa4 y\\xc3\\xb6t\\xc3\\xa4\n${FULL PROMPT}

Write ASCII-Only Unicode When Encoding Is Disabled
    Check Test Case    ${TEST NAME}

Write Does Not Allow Newlines
    Check Test Case    ${TEST NAME}

Write Bare
    Check Test Case    ${TEST NAME}

Write Bare With Newlines
    Check Test Case    ${TEST NAME}

Write control character using name
    Check Test Case    ${TEST NAME}

Write control character using number
    Check Test Case    ${TEST NAME}

Read Until
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 0]}    /
    Check Log Message    ${tc[3, 0]}    home/    DEBUG

Read Until Non-ASCII
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 0]}    Hyvää yötä

Read Until Fails
    Check Test Case    ${TEST NAME}

Read Until Regexp
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 0]}    ${HOME}
    Check Log Message    ${tc[3, 0]}    ${PROMPT START}    DEBUG

Read Until Regexp With Compiled Regexp
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[2, 0]}    ${HOME}
    Check Log Message    ${tc[5, 0]}    ${PROMPT START}    DEBUG

Read Until Regexp Non-ASCII
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 0]}    Päivää    DEBUG

Read Until Regexp Fails
    Check Test Case    ${TEST NAME}

Read Until Regexp Requires At Least One Pattern
    Check Test Case    ${TEST NAME}

Read Until Prompt
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 0]}    ${HOME}\n${FULL PROMPT}
    Check Log Message    ${tc[4, 0]}    ${HOME}\n${FULL PROMPT}    DEBUG

Read Until Prompt And Strip Prompt
    ${tc}=     Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[2, 0]}    ${HOME}\n${FULL PROMPT}
    Check Log Message    ${tc[5, 0]}    ${HOME}\n${FULL PROMPT}    DEBUG

Read Until Regexp Prompt
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[2, 0]}    ${HOME}\n${FULL PROMPT}

Read Until Regexp Prompt And Strip Prompt
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[2, 0]}    ${HOME}\n${FULL PROMPT}

Write Until Expected Output
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 0]}    ${FULL PROMPT}a=$(($a - 1)); if (($a == 0)); then echo BLAST; fi
    Check Log Message    ${tc[1, 1]}    ${FULL PROMPT}
    Check Log Message    ${tc[1, 2]}    a=$(($a - 1)); if (($a == 0)); then echo BLAST; fi

Execute Command
    Check Test Case    ${TEST NAME}

Execute Command And Strip Prompt
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[1, 1]}    ${HOME}\n${FULL PROMPT}
    Check Log Message    ${tc[3, 1]}    ${HOME}\n${FULL PROMPT}    DEBUG

Writing and reading fails if there is no connection
    Check Test Case    ${TEST NAME}
