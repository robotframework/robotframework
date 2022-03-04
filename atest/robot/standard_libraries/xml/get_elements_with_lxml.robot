*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/get_elements_with_lxml.robot
Force Tags       require-lxml
Resource         xml_resource.robot

*** Test Cases ***
Get element from parent element
    Check Test Case    ${TESTNAME}

Get element from xml file
    Check Test Case    ${TESTNAME}

Get element from xml file using pathlib.Path
    Check Test Case    ${TESTNAME}

Get element from xml string
    Check Test Case    ${TESTNAME}

Get element from xml bytes
    Check Test Case    ${TESTNAME}

Get element with named xpath
    Check Test Case    ${TESTNAME}

Get element without xpath
    Check Test Case    ${TESTNAME}

Get element fails when multiple elements match
    Check Test Case    ${TESTNAME}

Get element fails when no elements match
    Check Test Case    ${TESTNAME}

Get elements
    Check Test Case    ${TESTNAME}

Get elements using pathlib.Path
    Check Test Case    ${TESTNAME}

Get elements from xml string
    Check Test Case    ${TESTNAME}

Get elements from xml bytes
    Check Test Case    ${TESTNAME}

Get elements returns empty list when no elements match
    Check Test Case    ${TESTNAME}

Get child elements
    Check Test Case    ${TESTNAME}

Get child elements fails when multiple parent elements match
    Check Test Case    ${TESTNAME}

Get child elements fails when no parent element matches
    Check Test Case    ${TESTNAME}

Non-ASCII
    Check Test Case    ${TESTNAME}
