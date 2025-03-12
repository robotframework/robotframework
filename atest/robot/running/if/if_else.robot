*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/if/if_else.robot
Resource          atest_resource.robot

*** Test Cases ***
If passing
    Check Test Case    ${TESTNAME}

If failing
    Check Test Case    ${TESTNAME}

If not executed
    Check Test Case    ${TESTNAME}

If not executed failing
    Check Test Case    ${TESTNAME}

If else - if executed
    Check Test Case    ${TESTNAME}

If else - else executed
    Check Test Case    ${TESTNAME}

If else - if executed - failing
    Check Test Case    ${TESTNAME}

If else - else executed - failing
    Check Test Case    ${TESTNAME}

If passing in keyword
    Check Test Case    ${TESTNAME}

If passing in else keyword
    Check Test Case    ${TESTNAME}

If failing in keyword
    Check Test Case    ${TESTNAME}

If failing in else keyword
    Check Test Case    ${TESTNAME}

Expression evaluation time is included in elapsed time
    ${tc} =    Check Test Case    ${TESTNAME}
    Elapsed Time Should Be Valid    ${tc[0].elapsed_time}       minimum=0.2
    Elapsed Time Should Be Valid    ${tc[0, 0].elapsed_time}    minimum=0.1
    Elapsed Time Should Be Valid    ${tc[0, 1].elapsed_time}    minimum=0.1
    Elapsed Time Should Be Valid    ${tc[0, 2].elapsed_time}    maximum=1.0
