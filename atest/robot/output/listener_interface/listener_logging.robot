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

*** Keywords ***
Run Tests With Logging Listener
    ${path} =    Normalize Path    ${LISTENER DIR}/logging_listener.py
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
    Check Log Message    ${ERRORS[0]}     message: INFO Robot Framework *       WARN    pattern=yes
    Check Log Message    ${ERRORS[-4]}    log_message: FAIL Expected failure    WARN

Correct start/end warnings should be shown in execution errors
    ${msgs} =    Get start/end messages    ${ERRORS}
    @{kw} =        Create List    start keyword    end keyword
    @{var} =       Create List    start var        end var
    @{return} =    Create List    start return     end return
    @{setup} =     Create List    start setup      @{kw}    @{kw}    @{kw}    @{var}    @{kw}    @{return}    end setup
    @{uk} =        Create List    start keyword    @{kw}    @{kw}    @{kw}    @{var}    @{kw}    @{return}    end keyword
    FOR    ${index}    ${method}    IN ENUMERATE
    ...    start_suite
    ...    @{setup}
    ...    start_test
    ...    @{uk}
    ...    end_test
    ...    start_test
    ...    @{uk}
    ...    @{kw}
    ...    end_test
    ...    end_suite
         Check Log Message    ${msgs}[${index}]    ${method}    WARN
    END
    Length Should Be    ${msgs}    ${index + 1}

Get start/end messages
    [Arguments]    ${messages}
    ${result} =    Create List
    FOR    ${msg}    IN    @{messages}
        IF    "message: " not in $msg.message
        ...    Append To List    ${result}    ${msg}
    END
    RETURN    ${result}

Correct messages should be logged to normal log
    'My Keyword' has correct messages    ${SUITE.setup}    Suite Setup
    ${tc} =    Check Test Case    Pass
    'My Keyword' has correct messages    ${tc.kws[0]}    Pass
    ${tc} =    Check Test Case    Fail
    'My Keyword' has correct messages    ${tc.kws[0]}    Fail
    'Fail' has correct messages    ${tc.kws[1]}

'My Keyword' has correct messages
    [Arguments]    ${kw}    ${name}
    IF    '${name}' == 'Suite Setup'
        ${type} =    Set Variable    setup
    ELSE
        ${type} =    Set Variable    keyword
    END
    Check Log Message    ${kw.body[0]}            start ${type}    INFO
    Check Log Message    ${kw.body[1]}            start ${type}    WARN
    Check Log Message    ${kw.body[2].body[0]}    start keyword    INFO
    Check Log Message    ${kw.body[2].body[1]}    start keyword    WARN
    Check Log Message    ${kw.body[2].body[2]}    log_message: INFO Hello says "${name}"!    INFO
    Check Log Message    ${kw.body[2].body[3]}    log_message: INFO Hello says "${name}"!    WARN
    Check Log Message    ${kw.body[2].body[4]}    Hello says "${name}"!    INFO
    Check Log Message    ${kw.body[2].body[5]}    end keyword      INFO
    Check Log Message    ${kw.body[2].body[6]}    end keyword      WARN
    Check Log Message    ${kw.body[3].body[0]}    start keyword    INFO
    Check Log Message    ${kw.body[3].body[1]}    start keyword    WARN
    Check Log Message    ${kw.body[3].body[2]}    end keyword      INFO
    Check Log Message    ${kw.body[3].body[3]}    end keyword      WARN
    Check Log Message    ${kw.body[4].body[0]}    start keyword    INFO
    Check Log Message    ${kw.body[4].body[1]}    start keyword    WARN
    Check Log Message    ${kw.body[4].body[2]}    log_message: INFO \${assign} = JUST TESTING...    INFO
    Check Log Message    ${kw.body[4].body[3]}    log_message: INFO \${assign} = JUST TESTING...    WARN
    Check Log Message    ${kw.body[4].body[4]}    \${assign} = JUST TESTING...    INFO
    Check Log Message    ${kw.body[4].body[5]}    end keyword      INFO
    Check Log Message    ${kw.body[4].body[6]}    end keyword      WARN
    Check Log Message    ${kw.body[5].body[0]}    start var        INFO
    Check Log Message    ${kw.body[5].body[1]}    start var        WARN
    Check Log Message    ${kw.body[5].body[2]}    log_message: INFO \${expected} = JUST TESTING...    INFO
    Check Log Message    ${kw.body[5].body[3]}    log_message: INFO \${expected} = JUST TESTING...    WARN
    Check Log Message    ${kw.body[5].body[4]}    \${expected} = JUST TESTING...    INFO
    Check Log Message    ${kw.body[5].body[5]}    end var          INFO
    Check Log Message    ${kw.body[5].body[6]}    end var          WARN
    Check Log Message    ${kw.body[6].body[0]}    start keyword    INFO
    Check Log Message    ${kw.body[6].body[1]}    start keyword    WARN
    Check Log Message    ${kw.body[6].body[2]}    end keyword      INFO
    Check Log Message    ${kw.body[6].body[3]}    end keyword      WARN
    Check Log Message    ${kw.body[7].body[0]}    start return     INFO
    Check Log Message    ${kw.body[7].body[1]}    start return     WARN
    Check Log Message    ${kw.body[7].body[2]}    end return       INFO
    Check Log Message    ${kw.body[7].body[3]}    end return       WARN
    Check Log Message    ${kw.body[8]}            end ${type}      INFO
    Check Log Message    ${kw.body[9]}            end ${type}      WARN

'Fail' has correct messages
    [Arguments]    ${kw}
    Check Log Message    ${kw.body[0]}    start keyword    INFO
    Check Log Message    ${kw.body[1]}    start keyword    WARN
    Check Log Message    ${kw.body[2]}    log_message: FAIL Expected failure    INFO
    Check Log Message    ${kw.body[3]}    log_message: FAIL Expected failure    WARN
    Check Log Message    ${kw.body[4]}    Expected failure    FAIL
    Check Log Message    ${kw.body[5]}    end keyword    INFO
    Check Log Message    ${kw.body[6]}    end keyword    WARN

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
