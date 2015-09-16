*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/xpath_with_lxml.robot
Force Tags       require-lxml
Resource         xml_resource.robot

*** Test Cases ***
Tag
    Check Test Case    ${TESTNAME}

Path
    Check Test Case    ${TESTNAME}

Path matching multiple elements
    Check Test Case    ${TESTNAME}

'*'
    Check Test Case    ${TESTNAME}

'.'
    Check Test Case    ${TESTNAME}

'//'
    Check Test Case    ${TESTNAME}

'//' matching multiple elements
    Check Test Case    ${TESTNAME}

'..'
    Check Test Case    ${TESTNAME}

'[@attrib]'
    Check Test Case    ${TESTNAME}

'[@attrib="value"]'
    Check Test Case    ${TESTNAME}

'[tag]'
    Check Test Case    ${TESTNAME}

'[position]'
    Check Test Case    ${TESTNAME}

Stacked predicates
    Check Test Case    ${TESTNAME}

Non-ASCII tag names
    Check Test Case    ${TESTNAME}

More complex non-ASCII xpath
    Check Test Case    ${TESTNAME}

Advanced xpath supported by lxml
    Check Test Case    ${TESTNAME}

Advanced xpath supported by lxml matching multiple elements
    Check Test Case    ${TESTNAME}

Evaluate xpath
    Check Test Case    ${TESTNAME}
