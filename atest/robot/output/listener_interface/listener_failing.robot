*** Settings ***
Suite Setup       Run Tests With Failing Listener
Resource          listener_resource.robot

*** Test Cases ***
Failing listener does not break output file
    Test statuses should be correct
    Log and report should be created

Listener errors are shown
    ${path} =    Normalize Path    ${DATADIR}/output/listeners/failing_listener.py
    : FOR    ${index}    ${method}    IN ENUMERATE
    ...    message    start_suite    start_keyword    log_message    end_keyword
    ...    start_test    end_test    end_suite
    \    Check log message    @{ERRORS}[${index}]
    \    ...  Calling method '${method}' of listener '${path}' failed: Expected failure in ${method}!    ERROR
    : FOR    ${method}    IN    output_file    log_file    report_file    close
    \    Check stderr contains    [ ERROR ] Calling method '${method}' of listener '${path}' failed: Expected failure in ${method}!

*** Keywords ***
Run Tests With Failing Listener
    ${path} =    Normalize Path    ${DATADIR}/output/listeners/failing_listener.py
    Run Tests    --listener ${path} -l l.html -r r.html    misc/pass_and_fail.robot

Test statuses should be correct
    Check Test Case    Pass
    Check Test Case    Fail

Log and report should be created
    File Should Not Be Empty    ${OUTDIR}/l.html
    File Should Not Be Empty    ${OUTDIR}/r.html
