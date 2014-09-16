*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/element_text_with_lxml.robot
Test Teardown    Make test non-critical if lxml not available
Force Tags       regression    pybot    jybot
Resource         xml_resource.robot

*** Test Cases ***
Get text of current element
    Check Test Case    ${TESTNAME}

Get text of child element
    Check Test Case    ${TESTNAME}

Get text of element with no text
    Check Test Case    ${TESTNAME}

Get text with whitespace
    Check Test Case    ${TESTNAME}

Get text with whitespace normalized
    Check Test Case    ${TESTNAME}

Get text of element containing children
    Check Test Case    ${TESTNAME}

Get texts of elements
    Check Test Case    ${TESTNAME}

Get texts of elements whitespace normalized
    Check Test Case    ${TESTNAME}

Element text should be
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Empty    ${tc.kws[0].msgs}

Element text should match
    Check Test Case    ${TESTNAME}
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Empty    ${tc.kws[0].msgs}

Element text should be with whitespace normalized
    Check Test Case    ${TESTNAME}

Element text should match with whitespace normalized
    Check Test Case    ${TESTNAME}

Element text should be failing with custom message
    Check Test Case    ${TESTNAME}

Element text should match failing with custom message
    Check Test Case    ${TESTNAME}

Non-ASCII
    Check Test Case    ${TESTNAME}
