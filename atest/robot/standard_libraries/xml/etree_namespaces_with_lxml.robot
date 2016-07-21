*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/etree_namespaces_with_lxml.robot
Force Tags       require-lxml
Resource         xml_resource.robot

*** Test Cases ***
Tag names contain namespace in Clark Notation
    Check Test Case    ${TESTNAME}

Clarck Notation must be used in xpaths
    Check Test Case    ${TESTNAME}

xmlns attributes are removed
    Check Test Case    ${TESTNAME}

Parsed XML is semantically same as original
    Check Test Case    ${TESTNAME}

Saved XML has same namespaces as original
    Check Test Case    ${TESTNAME}

Attribute namespaces
    Check Test Case    ${TESTNAME}
