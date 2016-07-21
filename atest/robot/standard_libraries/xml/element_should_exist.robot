*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/element_should_exist.robot
Resource         xml_resource.robot

*** Test Cases ***

Get Element Count
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}   0 elements matched 'nonex'.
    Check Log Message    ${tc.kws[1].kws[0].msgs[0]}   1 element matched 'another'.
    Check Log Message    ${tc.kws[2].kws[0].msgs[0]}   1 element matched '.'.
    Check Log Message    ${tc.kws[3].kws[0].msgs[0]}   4 elements matched './/child'.

Element Should Exist Passes When There Are One Or More Matches
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}   1 element matched 'another/child'.
    Check Log Message    ${tc.kws[1].msgs[0]}   3 elements matched 'child'.

Element Should Exist Fails When There Are No Matches
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}   0 elements matched 'nönëx'.

Element Should Exist With Custom Error Message
    Check Test Case    ${TESTNAME}

Element Should Not Exist Passes When There Are No Matches
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}   0 elements matched 'nonex'.

Element Should Not Exist Fails When There Is One Match
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}   1 element matched 'another/child'.

Element Should Not Exist Fails When There Are Multiple Matches
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}   4 elements matched './/child'.

Element Should Not Exist With Custom Error Message
    Check Test Case    ${TESTNAME}
