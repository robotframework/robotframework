*** Settings ***
Suite Setup     Run Tests  --loglevel TRACE  keywords/trace_log_return_value.robot
Resource        atest_resource.robot

*** Test Cases ***

Return from Userkeyword
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: 'value'  TRACE
    Check Log Message  ${test.kws[0].kws[0].msgs[1]}  Return: 'value'  TRACE

Return from Library Keyword
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: 'value'  TRACE

Return from Run Keyword
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: 'value'  TRACE
    Check Log Message  ${test.kws[0].kws[0].msgs[1]}  Return: 'value'  TRACE

Return Non String Object
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[2]}  Return: 1  TRACE

Return None
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: None  TRACE

Return Non Ascii String
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: 'Hyv\\xe4\\xe4 P\\xe4iv\\xe4\\xe4'  TRACE

Return Object With Unicode Repr
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[2]}  Return: u'Circle is 360\\xb0, Hyv\\xe4\\xe4 \\xfc\\xf6t\\xe4, \\u0989\\u09c4 \\u09f0 \\u09fa \\u099f \\u09eb \\u09ea \\u09b9'  TRACE

Return Object with Invalid Unicode Repr
    [Documentation]  How the return value is logged depends on the interpreter.
    ${test} =    Check Test Case  ${TESTNAME}
    ${ret} =    Set Variable If    $INTERPRETER.is_python
    ...    <Unrepresentable object InvalidRepr. Error: UnicodeEncodeError: *    Hyv*
    Check Log Message    ${test.kws[0].msgs[1]}    Return: ${ret}    TRACE    pattern=yes

Return Object with Non Ascii String from Repr
    [Documentation]  How the return value is logged depends on the interpreter.
    ${test} =    Check Test Case    ${TESTNAME}
    ${ret} =    Set Variable If    $INTERPRETER.is_ironpython    Hyvä    Hyv\\xe4
    Check Log Message    ${test.kws[0].msgs[1]}    Return: ${ret}    TRACE
