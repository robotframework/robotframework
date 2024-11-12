*** Settings ***
Suite Setup        Run Logging Tests On Thread
Resource           atest_resource.robot

*** Variables ***
${RUNNER}          ${DATA DIR}/test_libraries/run_logging_tests_on_thread.py

*** Test Cases ***
robot.api.logger
    VAR    ${tc}    ${SUITE.suites[0].tests[0]}
    Check Log Message    ${tc.body[1].msgs[5]}    info msg 1         INFO
    Check Log Message    ${tc.body[1].msgs[6]}    info msg 2         INFO
    Check Log Message    ${tc.body[1].msgs[7]}    warn msg 1         WARN
    Check Log Message    ${ERRORS[0]}             warn msg 1         WARN

logging
    VAR    ${tc}    ${SUITE.suites[1].tests[1]}
    Check Log Message    ${tc.body[0].msgs[1]}    info message       INFO
    Check Log Message    ${tc.body[0].msgs[2]}    warning message    WARN
    Check Log Message    ${ERRORS[6]}             warning message    WARN

print
    VAR    ${tc}    ${SUITE.suites[2].tests[1]}
    Check Log Message    ${tc.body[0].msgs[3]}    Info message       INFO
    Check Log Message    ${tc.body[0].msgs[7]}    Error message      ERROR
    Check Log Message    ${ERRORS[-1]}            Error message      ERROR

*** Keywords ***
Run Logging Tests On Thread
    Set Execution Environment
    Run Process    @{INTERPRETER.interpreter}    ${RUNNER}    ${OUTFILE}
    ...    stdout=${STDOUTFILE}    stderr=${STDERRFILE}    output_encoding=SYSTEM
    ...    timeout=1min    on_timeout=terminate
    Process Output    ${OUTFILE}
