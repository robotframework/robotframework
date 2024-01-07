*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/namespaces_with_lxml.robot
Force Tags       require-lxml
Resource         xml_resource.robot

*** Test Cases ***
Tag names contain no namespaces
    Check Test Case    ${TESTNAME}

Namespaces are not needed in xpath
    Check Test Case    ${TESTNAME}

xmlns attributes with default namespaces are added when needed
    Check Test Case    ${TESTNAME}

Saved XML is semantically same as original
    Check Test Case    ${TESTNAME}

Saved XML has same namespaces as original
    Check Test Case    ${TESTNAME}

Element To String with namespaces
    Check Test Case    ${TESTNAME}

Element without namepace inside element with namespace
    Check Test Case    ${TESTNAME}

Attribute namespaces are not handled
    Check Test Case    ${TESTNAME}
