*** Settings ***
Suite Setup  Run Tests With Failing Listener
Resource  listener_resource.robot

*** Test Cases ***

Failing listener does not break output file
    Test statuses should be correct
    Log and report should be created

Listener errors are shown
    :FOR  ${method}  IN  start_suite  end_suite  start_test  end_test
    ...  start_keyword  end_keyword  log_message  message
    ...  output_file  log_file  report_file  close
    \  Syslog Should Match Regexp  | ERROR | Calling listener method '${method}' of listener '.*' failed: ${method}


*** Keywords ***
Run Tests With Failing Listener
    ${path} =  Normalize Path  ${DATADIR}/output/listeners/failing_listener.py
    Run Tests  --listener ${path} -l l.html -r r.html  misc/pass_and_fail.robot

Test statuses should be correct
    Check Test Case  Pass
    Check Test Case  Fail

Log and report should be created
    File Should Not Be Empty  ${OUTDIR}/l.html
    File Should Not Be Empty  ${OUTDIR}/r.html
