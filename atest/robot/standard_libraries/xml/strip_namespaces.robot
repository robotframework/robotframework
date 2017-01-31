*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/strip_namespaces.robot
Resource         atest_resource.robot

*** Test Cases ***
Tag names contain no namespaces
    Check Test Case    ${TESTNAME}

Namespaces are not needed in xpath
    Check Test Case    ${TESTNAME}

xmlns attributes are not needed
    Check Test Case    ${TESTNAME}

Saved XML has correct content and no namespaces
    Check Test Case    ${TESTNAME}

Attribute namespaces are not stripped
    Check Test Case    ${TESTNAME}
