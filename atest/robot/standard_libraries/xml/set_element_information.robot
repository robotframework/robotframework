*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/set_element_information.robot
Resource         xml_resource.robot

*** Test Cases ***
Set Element Tag
    Check Test Case    ${TESTNAME}

Set Element Tag Using Xpath
    Check Test Case    ${TESTNAME}

Set Element Tag Returns Root Element
    Check Test Case    ${TESTNAME}

Set Elements Tag
    Check Test Case    ${TESTNAME}

Set Elements Tag returns root element
    Check Test Case    ${TESTNAME}

Set Element Text
    Check Test Case    ${TESTNAME}

Set Element Text And Tail
    Check Test Case    ${TESTNAME}

Set Element Text Returns Root Element
    Check Test Case    ${TESTNAME}

Set Elements Text
    Check Test Case    ${TESTNAME}

Set Elements Text Returns Root Element
    Check Test Case    ${TESTNAME}

Set Element Text none
    Check Test Case    ${TESTNAME}

Set Element Attribute
    Check Test Case    ${TESTNAME}

Set Element Attribute should fail with empty name
    Check Test Case    ${TESTNAME}

Overwrite Element Attribute
    Check Test Case    ${TESTNAME}

Set Element Attribute Returns Root Element
    Check Test Case    ${TESTNAME}

Set Elements Attribute
    Check Test Case    ${TESTNAME}

Set Elements Attribute Returns Root Element
    Check Test Case    ${TESTNAME}

Remove Element Attribute
    Check Test Case    ${TESTNAME}

Removing Non-Existing Attribute Passes
    Check Test Case    ${TESTNAME}

Remove Element Attribute Returns Root Element
    Check Test Case    ${TESTNAME}

Remove Elements Attribute
    Check Test Case    ${TESTNAME}

Remove Elements Attribute Returns Root Element
    Check Test Case    ${TESTNAME}

Remove Element Attributes
    Check Test Case    ${TESTNAME}

Remove Element Attributes Returns Root Element
    Check Test Case    ${TESTNAME}

Remove Elements Attributes
    Check Test Case    ${TESTNAME}

Remove Elements Attributes Returns Root Element
    Check Test Case    ${TESTNAME}
