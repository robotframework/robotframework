*** Settings ***
Variables         telnet_variables.py

*** Keyword ***
Login and set prompt
    [Arguments]    ${alias}=${NONE}    ${encoding}=${NONE}    ${terminal_emulation}=${NONE}    ${window_size}=${NONE}   ${terminal_type}=${NONE}
    ${index} =    Open Connection    ${HOST}    prompt=${PROMPT}
    ...    alias=${alias}    encoding=${encoding}    terminal_emulation=${terminal_emulation}
    ...    window_size=${window_size}     terminal_type=${terminal_type}
    Login    ${USERNAME}    ${PASSWORD}
    Set Timeout    0.3 seconds    # Must set after login to give login time to succeed
    [Return]    ${index}

Should fail because no connection
    [Arguments]    ${kw}    @{args}
    Run Keyword And Expect Error    No connection open    ${kw}    @{args}

Environment variable should be
    [arguments]    ${var}    ${value}
    ${out} =    Execute command    echo ${var}
    Should match   ${out}    ${value}\r\n*