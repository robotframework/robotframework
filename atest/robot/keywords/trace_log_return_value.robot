*** Settings ***
Suite Setup     Run Tests  --loglevel TRACE  keywords/trace_log_return_value.txt
Force Tags      regression  pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***

Return from Userkeyword
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: u'value'  TRACE
    Check Log Message  ${test.kws[0].kws[0].msgs[1]}  Return: u'value'  TRACE

Return from Library Keyword
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: u'value'  TRACE

Return from Run Keyword
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: u'value'  TRACE
    Check Log Message  ${test.kws[0].kws[0].msgs[1]}  Return: u'value'  TRACE

Return Non String Object
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[2]}  Return: 1  TRACE

Return None
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: None  TRACE

Return Non Ascii String
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[1]}  Return: u'Hyv\\xe4\\xe4 P\\xe4iv\\xe4\\xe4'  TRACE

Return Object With Unicode Repr
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[2]}  Return: u'Circle is 360\\xb0, Hyv\\xe4\\xe4 \\xfc\\xf6t\\xe4, \\u0989\\u09c4 \\u09f0 \\u09fa \\u099f \\u09eb \\u09ea \\u09b9'  TRACE

Return Object with Invalid Unicode Repr
    [Documentation]  How the return value is logged depends on the interpreter.
    ${test} =    Check Test Case  ${TESTNAME}
    ${path}    ${base} =    Split Path    ${INTERPRETER}
    ${ret} =    Set Variable If    'python' in '${base}'    u'Hyv\\xe4'    Hyvä
    Check Log Message    ${test.kws[0].msgs[1]}    Return: ${ret}    TRACE

Return Object with Non Ascii String from Repr
    [Documentation]  How the return value is logged depends on the interpreter.
    ${test} =    Check Test Case    ${TESTNAME}
    ${path}    ${base} =    Split Path    ${INTERPRETER}
    ${ret} =    Set Variable If    'ipy' in '${base}'    Hyvä    Hyv\\xe4
    Check Log Message    ${test.kws[0].msgs[1]}    Return: ${ret}    TRACE
