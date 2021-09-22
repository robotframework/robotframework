*** Settings ***
Suite Setup       Run Tests    --loglevel TRACE    keywords/trace_log_return_value.robot
Resource          atest_resource.robot

*** Test Cases ***
Return from user keyword
    ${test} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${test.kws[0].msgs[1]}    Return: 'value'    TRACE
    Check Log Message    ${test.kws[0].kws[0].msgs[1]}    Return: 'value'    TRACE

Return from library keyword
    ${test} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${test.kws[0].msgs[1]}    Return: 'value'    TRACE

Return from Run Keyword
    ${test} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${test.kws[0].msgs[1]}    Return: 'value'    TRACE
    Check Log Message    ${test.kws[0].kws[0].msgs[1]}    Return: 'value'    TRACE

Return non-string value
    ${test} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${test.kws[0].msgs[2]}    Return: 1    TRACE

Return None
    ${test} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${test.kws[0].msgs[1]}    Return: None    TRACE

Return non-ASCII string
    ${test} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${test.kws[0].msgs[1]}    Return: "Hyvää 'Päivää'\\n"    TRACE

Return object with non-ASCII repr
    ${test} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${test.kws[0].msgs[1]}    Return: Hyvä    TRACE

Return object with invalid repr
    ${test} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${test.kws[0].msgs[1]}
    ...    Return: <Unrepresentable object InvalidRepr. Error: ValueError>    TRACE
