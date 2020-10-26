*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/type_conversion/unions.robot
Resource         atest_resource.robot
Force Tags       require-py3

*** Test Cases ***
Union
     Check Test Case    ${TESTNAME}

Argument not matching union
     Check Test Case    ${TESTNAME}

Union with None
     Check Test Case    ${TESTNAME}
     Check Test Case    ${TESTNAME} and string

Union with custom type
     Check Test Case    ${TESTNAME}

Multiple types using tuple
     Check Test Case    ${TESTNAME}

Argument not matching tuple types
     Check Test Case    ${TESTNAME}

Optional argument
     Check Test Case    ${TESTNAME}

Optional argument with default
     Check Test Case    ${TESTNAME}
