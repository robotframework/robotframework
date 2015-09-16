*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/xml/element_attribute_with_lxml.robot
Force Tags       require-lxml
Resource         xml_resource.robot

*** Test Cases ***
Get attribute of current element
    Check Test Case    ${TESTNAME}

Get attribute of child element
    Check Test Case    ${TESTNAME}

Getting non-existing attribute returns None
    Check Test Case    ${TESTNAME}

Default value is used when attribute does not exist
    Check Test Case    ${TESTNAME}

Get element attributes
    Check Test Case    ${TESTNAME}

Modifying returned attributes does not affect original element
    Check Test Case    ${TESTNAME}

Element attribute should be
    Check Test Case    ${TESTNAME}

Element attribute should be when no attribute exists
    Check Test Case    ${TESTNAME}

Element attribute should be with custom error message
    Check Test Case    ${TESTNAME}

Element attribute should match
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Empty    ${tc.kws[0].msgs}

Element attribute should match when no attribute exists
    Check Test Case    ${TESTNAME}

Element attribute should match with custom error message
    Check Test Case    ${TESTNAME}

Element should not have attribute
    Check Test Case    ${TESTNAME}

Element should not have attribute with custom error message
    Check Test Case    ${TESTNAME}

Non-ASCII
    Check Test Case    ${TESTNAME}
