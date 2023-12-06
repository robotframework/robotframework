*** Settings ***
Resource          listener_resource.robot

*** Test Cases ***
Failing listeners don't affect execution otherwise
    Run Tests With Failing Listener
    Test statuses should be correct
    Log and report should be created
    Listener errors should be reported

Failing library listeners don't affect execution otherwise
    Run Tests With Failing Library Listener
    Test statuses should be correct
    Log and report should be created
    Library listener errors should be reported

*** Keywords ***
Run Tests With Failing Listener
    ${path} =    Normalize Path    ${LISTENER DIR}/failing_listener.py
    Run Tests    --listener ${path} -l l.html -r r.html    misc/pass_and_fail.robot

Run Tests With Failing Library Listener
    Run Tests    -l l.html -r r.html    ${LISTENER DIR}/failing_library_listener.robot

Test statuses should be correct
    Check Test Case    Pass
    Check Test Case    Fail

Log and report should be created
    File Should Not Be Empty    ${OUTDIR}/l.html
    File Should Not Be Empty    ${OUTDIR}/r.html

Listener errors should be reported
    ${path} =    Normalize Path    ${LISTENER DIR}/failing_listener.py
    FOR    ${index}    ${method}    IN ENUMERATE
    ...    message    start_suite    start_keyword    log_message    end_keyword
    ...    start_test    end_test    end_suite
        Error should be reported in execution errors    ${index}    ${method}    ${path}
    END
    FOR    ${method}    IN    output_file    log_file    report_file    close
        Error should be reported in stderr    ${method}    ${path}
    END

Library listener errors should be reported
    FOR    ${index}    ${method}    IN ENUMERATE
    ...    start_suite    start_test    start_keyword    log_message
    ...    end_keyword    end_test    end_suite
        Error should be reported in execution errors    ${index}    ${method}    failing_listener
    END
    Error should be reported in stderr    close    failing_listener

Error should be reported in execution errors
    [Arguments]    ${index}    ${method}    ${listener}
    ${error} =    Catenate
    ...    Calling method '${method}' of listener '${listener}' failed:
    ...    Expected failure in ${method}!
    Check log message    ${ERRORS}[${index}]    ${error}    ERROR

Error should be reported in stderr
    [Arguments]    ${method}    ${listener}
    ${error} =    Catenate
    ...    Calling method '${method}' of listener '${listener}' failed:
    ...    Expected failure in ${method}!
    Stderr Should Contain    [ ERROR ] ${error}
