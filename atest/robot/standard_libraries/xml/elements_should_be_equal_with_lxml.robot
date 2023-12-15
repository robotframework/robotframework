*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/elements_should_be_equal_with_lxml.robot
Force Tags       require-lxml
Resource         xml_resource.robot

*** Test Cases ***
Elements should be equal
    Check Test Case    ${TESTNAME}

Tail text is not checked with root element
    Check Test Case    ${TESTNAME}

Different tag names
    Check Test Case    ${TESTNAME}

Different attributes
    Check Test Case    ${TESTNAME}

Different texts
    Check Test Case    ${TESTNAME}

Different tail texts
    Check Test Case    ${TESTNAME}

Different number of children
    Check Test Case    ${TESTNAME}

Differences in children
    Check Test Case    ${TESTNAME}

Differences in children with same name
    Check Test Case    ${TESTNAME}

Differences in children with non-ASCII path
    Check Test Case    ${TESTNAME}

Normalize whitespace
    Check Test Case    ${TESTNAME}

Exclude children
    Check Test Case    ${TESTNAME}

Sort children
    Check Test Case    ${TESTNAME}
