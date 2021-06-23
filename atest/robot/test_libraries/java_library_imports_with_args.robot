*** Settings ***
Documentation     Tests for checking that library initialization arguments are handled correctly.
...               Taking libraries without arguments is not tested here, because almost every other suite does that.
Suite Setup       Run Tests    ${EMPTY}    test_libraries/java_library_imports_with_args.robot
Force Tags        require-jython
Test Template     Library import should have been successful
Resource          resource_for_importing_libs_with_args.robot

*** Variables ***
${KEY: VALUE}     ${{ "{key: value}" if $INTERPRETER.version_info < (2, 7, 2) else "{u'key': u'value'}" }}

*** Test Cases ***
Mandatory arguments
    MandatoryArgs    first arg    another arg

Default values
    DefaultArgs    m1
    DefaultArgs    m2    d1
    DefaultArgs    m3    1    2

Variables containing objects
    MandatoryArgs    42    The name of the JavaObject
    MandatoryArgs    ${KEY: VALUE}    True

Too Few Arguments
    [Template]    Library import should have failed
    MandatoryArgs    2 arguments, got 1.
    DefaultArgs    1 to 3 arguments, got 0.

Too Many Arguments
    [Template]    Library import should have failed
    MandatoryArgs    2 arguments, got 4.
    DefaultArgs    1 to 3 arguments, got 5.

Non-existing variables
    [Template]
    Syslog Should Contain    Variable '\${NON EXISTING}' not found.

*** Keywords ***
Library import should have been successful
    [Arguments]    ${lib}    @{params}
    Check Test Case    ${TEST NAME}
    ${par} =    Catenate    SEPARATOR=${SPACE}|${SPACE}    @{params}
    Syslog Should Contain    Imported library class    '${lib}' from unknown location.
    Syslog Should Contain    Imported library '${lib}' with arguments [ ${par} ]

Library import should have failed
    [Arguments]    ${lib}    ${err}
    Syslog Should Contain    Library '${lib}' expected ${err}
