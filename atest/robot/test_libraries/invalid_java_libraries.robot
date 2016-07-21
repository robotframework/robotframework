*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    test_libraries/invalid_java_libraries.robot
Force Tags       require-jython
Resource         atest_resource.robot

*** Test Cases ***

Importing Abstract Java Library Fails Cleanly
    Init Error    0    AbstractJavaLibrary

Importing Java Library Without Public Constructor Fails Cleanly
    Init Error    1    JavaLibraryWithoutPublicConstructor

Importing Abstract Java Library Without Public Constructor Fails Cleanly
    Init Error    3    java.lang.Enum

Arguments For Java Library Without Public Constructor
    Limit Error    2    JavaLibraryWithoutPublicConstructor    3
    Limit Error    4    java.lang.Enum    2

Invalid Java Libraries Do Not Cause Fatal Errors
    Check Test Case    ${TESTNAME}


*** Keywords ***

Init Error
    [Arguments]    ${index}    ${name}
    Verify Error    ${index}
    ...   Initializing test library '${name}' with no arguments failed: TypeError: *

Limit Error
    [Arguments]    ${index}    ${name}    ${arg count}
    Verify Error    ${index}
    ...   Test Library '${name}' expected 0 arguments, got ${arg count}.

Verify Error
    [Arguments]    ${index}    ${error}
    ${path} =    Normalize Path    ${DATADIR}/test_libraries/invalid_java_libraries.robot
    Check Log Message    ${ERRORS.msgs[${index}]}
    ...    Error in file '${path}': ${error}
    ...    ERROR    pattern=yes
