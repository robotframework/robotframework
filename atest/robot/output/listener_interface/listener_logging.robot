*** Settings ***
Suite Setup       Run Tests With Logging Listener
Resource          listener_resource.robot

*** Test Cases ***
Logging from listener does not break output file
    Test statuses should be correct
    Log and report should be created

All start and end methods can log warnings to execution errors
    Correct warnings should be shown in execution errors

Methods inside start_keyword and end_keyword can log normal messages
    Correct messages should be logged to normal log

Methods outside start_keyword and end_keyword can log messages to syslog
    Correct messages should be logged to syslog

Listener works with if/else structure
    ${path} =    Normalize Path    ${DATADIR}/output/listeners/logging_listener.py
    Run Tests    --listener ${path} -l l.html -r r.html    misc/if_else.robot
    Log and report should be created

*** Keywords ***
Run Tests With Logging Listener
    ${path} =    Normalize Path    ${DATADIR}/output/listeners/logging_listener.py
    Run Tests    --listener ${path} -l l.html -r r.html    misc/pass_and_fail.robot

Test statuses should be correct
    Check Test Case    Pass
    Check Test Case    Fail

Log and report should be created
    File Should Not Be Empty    ${OUTDIR}/l.html
    File Should Not Be Empty    ${OUTDIR}/r.html

Correct warnings should be shown in execution errors
    Execution errors should have messages from message and log_message methods
    Correct start/end warnings should be shown in execution errors

Execution errors should have messages from message and log_message methods
    Check Log Message    ${ERRORS[0]}    message: INFO Robot Framework *    WARN    pattern=yes
    Check Log Message    ${ERRORS[-4]}    log_message: FAIL Expected failure    WARN

Correct start/end warnings should be shown in execution errors
    ${msgs} =    Get start/end messages    ${ERRORS.msgs}
    @{kw} =    Create List    start_keyword    end_keyword
    @{uk} =    Create List    start_keyword    @{kw}    @{kw}    @{kw}    end_keyword
    FOR    ${index}    ${method}    IN ENUMERATE
    ...    start_suite
    ...    @{uk}
    ...    start_test
    ...    @{uk}
    ...    end_test
    ...    start_test
    ...    @{uk}
    ...    @{kw}
    ...    end_test
    ...    end_suite
         Check Log Message    ${msgs[${index}]}    ${method}    WARN
    END
    Length Should Be    ${msgs}    ${index + 1}

Get start/end messages
    [Arguments]    ${all msgs}
    @{all msgs} =    Set Variable    ${all msgs}
    ${return} =    Create List
    FOR    ${msg}    IN    @{all msgs}
        Run Keyword Unless    "message: " in $msg.message
        ...    Append To List    ${return}    ${msg}
    END
    [Return]    ${return}

Correct messages should be logged to normal log
    'My Keyword' has correct messages    ${SUITE.setup}    Suite Setup
    ${tc} =    Check Test Case    Pass
    'My Keyword' has correct messages    ${tc.kws[0]}    Pass
    ${tc} =    Check Test Case    Fail
    'My Keyword' has correct messages    ${tc.kws[0]}    Fail
    'Fail' has correct messages    ${tc.kws[1]}

'My Keyword' has correct messages
    [Arguments]    ${kw}    ${name}
    Check Log Message    ${kw.kws[0].msgs[0]}    start_keyword    INFO
    Check Log Message    ${kw.kws[0].msgs[1]}    start_keyword    WARN
    Check Log Message    ${kw.kws[0].msgs[2]}    log_message: INFO Hello says "${name}"!    INFO
    Check Log Message    ${kw.kws[0].msgs[3]}    log_message: INFO Hello says "${name}"!    WARN
    Check Log Message    ${kw.kws[0].msgs[4]}    Hello says "${name}"!    INFO
    Check Log Message    ${kw.kws[0].msgs[5]}    end_keyword    INFO
    Check Log Message    ${kw.kws[0].msgs[6]}    end_keyword    WARN
    Check Log Message    ${kw.kws[1].msgs[0]}    start_keyword    INFO
    Check Log Message    ${kw.kws[1].msgs[1]}    start_keyword    WARN
    Check Log Message    ${kw.kws[1].msgs[2]}    end_keyword    INFO
    Check Log Message    ${kw.kws[1].msgs[3]}    end_keyword    WARN
    Check Log Message    ${kw.msgs[0]}    start_keyword    INFO
    Check Log Message    ${kw.msgs[1]}    start_keyword    WARN
    Check Log Message    ${kw.msgs[2]}    end_keyword    INFO
    Check Log Message    ${kw.msgs[3]}    end_keyword    WARN

'Fail' has correct messages
    [Arguments]    ${kw}
    Check Log Message    ${kw.msgs[0]}    start_keyword    INFO
    Check Log Message    ${kw.msgs[1]}    start_keyword    WARN
    Check Log Message    ${kw.msgs[2]}    log_message: FAIL Expected failure    INFO
    Check Log Message    ${kw.msgs[3]}    log_message: FAIL Expected failure    WARN
    Check Log Message    ${kw.msgs[4]}    Expected failure    FAIL
    Check Log Message    ${kw.msgs[5]}    end_keyword    INFO
    Check Log Message    ${kw.msgs[6]}    end_keyword    WARN

Correct messages should be logged to syslog
    FOR    ${msg}    IN
    ...    message: INFO Robot Framework
    ...    start_suite
    ...    end_suite
    ...    start_test
    ...    end_test
    ...    output_file
    ...    log_file
    ...    report_file
        Syslog Should Contain    | INFO \ | ${msg}
        Syslog Should Contain    | WARN \ | ${msg}
    END
