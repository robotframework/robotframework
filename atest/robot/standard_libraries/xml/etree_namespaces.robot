*** Settings ***
Documentation    Tests for using ElementTree's default namespace handling
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/etree_namespaces.robot
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

Prefixes are mangled when XML is saved
    Check Test Case    ${TESTNAME}

Attribute namespaces
    Check Test Case    ${TESTNAME}
