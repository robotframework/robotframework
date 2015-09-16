*** Settings ***
Suite Setup      Run Tests    --loglevel debug    standard_libraries/xml/to_string.robot
Resource         xml_resource.robot

*** Test Cases ***
Element to string
    Check Test Case    ${TESTNAME}

Element to string with encoding
    Check Test Case    ${TESTNAME}

Child element to string
    Check Test Case    ${TESTNAME}

Log element
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    <root>\n\t<täg attr="hyvä">sisältö</täg>\n</root>
    Check Log Message    ${tc.kws[2].msgs[0]}    <root><tag a="1" c="3">päivää</tag></root>    DEBUG
    Check Log Message    ${tc.kws[3].msgs[0]}    <test name="root">*</test>    pattern=yes

Log child element
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    <täg attr="hyvä">sisältö</täg>
