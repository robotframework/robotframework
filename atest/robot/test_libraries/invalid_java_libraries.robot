*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    test_libraries/invalid_java_libraries.robot
Force Tags       require-jython
Resource         atest_resource.robot

*** Test Cases ***
Importing Abstract Java Library Fails Cleanly
    Init Error     0    2    AbstractJavaLibrary

Importing Java Library Without Public Constructor Fails Cleanly
    Init Error     1    3    JavaLibraryWithoutPublicConstructor

Importing Abstract Java Library Without Public Constructor Fails Cleanly
    Init Error     3    5    java.lang.Enum

Arguments For Java Library Without Public Constructor
    Limit Error    2    4    JavaLibraryWithoutPublicConstructor    3
    Limit Error    4    6    java.lang.Enum    2

Invalid Java Libraries Do Not Cause Fatal Errors
    Check Test Case    ${TESTNAME}

*** Keywords ***
Init Error
    [Arguments]    ${index}    ${lineno}    ${name}
    Error In File
    ...    ${index}    test_libraries/invalid_java_libraries.robot    ${lineno}
    ...    Initializing library '${name}' with no arguments failed:
    ...    TypeError: *

Limit Error
    [Arguments]    ${index}    ${lineno}    ${name}    ${arg count}
    Error In File
    ...    ${index}    test_libraries/invalid_java_libraries.robot    ${lineno}
    ...    Library '${name}' expected 0 arguments, got ${arg count}.
