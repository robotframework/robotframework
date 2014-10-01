*** Settings ***
Documentation     Tests for finding keywords from test case file, resource files
...               and libraries works correctly and keywords from different
...               sources have correct priorities. More than one keyword with
...               same name existing is tested too. Non-existing keywords are
...               tested in keyword_not_found.robot.
Suite Setup       Run Tests    ${EMPTY}    keywords/keyword_namespaces.robot
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Test Cases ***
Keywords With Unique Name Are Ok
    Check Test Case    ${TEST NAME}

Full Name Works With Non-Unique Keyword Names
    Check Test Case    ${TEST NAME}

Non-Unique Keywords Without Full Name Fails
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2
    Check Test Case    ${TEST NAME} 3

Keyword From Test Case File Overrides Keywords From Resources And Libraries
    Check Test Case    ${TEST NAME}

Keyword From Resource Overrides Keywords From Libraries
    Check Test Case    ${TEST NAME}

Keyword From User Library Overrides Keywords From Standard Library
    Check Test Case    ${TEST NAME}
    Verify Override Message    ${ERRORS.msgs[0]}    Comment    BuiltIn
    Verify Override Message    ${ERRORS.msgs[1]}    Copy Directory    OperatingSystem

Keyword From User Library Overrides Keywords From Standard Library Even When Std Lib Imported With Different Name
    Check Test Case    ${TEST NAME}
    Verify Override Message    ${ERRORS.msgs[2]}    Replace String    String    Std Lib With Custom Name

No Warning When User Library Keyword Is Registered As RunKeyword Variant And It Has Same Name As Std Keyword
    Check Test Case    ${TEST NAME}
    Check Stderr Does Not Contain    Run Keyword If

Keyword In More Than One User Library And Standard Library
    Check Test Case    ${TEST NAME}
    Check Syslog Does Not Contain    BuiltIn.No Operation

*** Keywords ***
Verify override message
    [Arguments]    ${msg}    ${kw}    ${stdlib}    ${custom}=
    ${stdlib2} =    Set Variable If    "${custom}"    ${custom}    ${stdlib}
    ${expected} =    Catenate
    ...    Keyword '${kw}' found both from a user created test library
    ...    'MyLibrary1' and Robot Framework standard library '${stdlib}'.
    ...    The user created keyword is used. To select explicitly, and to get
    ...    rid of this warning, use either 'MyLibrary1.${kw}' or '${stdlib2}.${kw}'.
    Check Log Message    ${msg}    ${expected}    WARN
