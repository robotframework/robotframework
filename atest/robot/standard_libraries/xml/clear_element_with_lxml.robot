*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/clear_element_with_lxml.robot
Force Tags       require-lxml
Resource         xml_resource.robot

*** Test Cases ***
Clear Element
    Check Test Case    ${TESTNAME}

Clear Element Returns Root Element
    Check Test Case    ${TESTNAME}

Tail Text Is Not Cleared By Default
    Check Test Case    ${TESTNAME}

Tail Text Can Be Cleared
    Check Test Case    ${TESTNAME}
