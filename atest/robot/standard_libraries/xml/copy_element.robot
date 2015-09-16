*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/copy_element.robot
Resource         xml_resource.robot

*** Test Cases ***

Elements Are Mutable
    Check Test Case    ${TESTNAME}

Copy Element
    Check Test Case    ${TESTNAME}

Copy Element Using Xpath
    Check Test Case    ${TESTNAME}

Copy Deeper Structure
    Check Test Case    ${TESTNAME}
