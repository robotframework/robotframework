*** Settings ***
Documentation     Tests for finding keywords from test case file, resource files
...               and libraries works correctly and keywords from different
...               sources have correct priorities. More than one keyword with
...               same name existing is tested too. Non-existing keywords are
...               tested in keyword_not_found.robot.
Suite Setup       Run Tests    ${EMPTY}    keywords/keyword_namespaces.robot
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

Keyword From Custom Library Overrides Keywords From Standard Library
    ${tc} =    Check Test Case    ${TEST NAME}
    Verify Override Message    ${ERRORS[1]}    ${tc.kws[0].msgs[0]}    Comment    BuiltIn
    Verify Override Message    ${ERRORS[2]}    ${tc.kws[1].msgs[0]}    Copy Directory    OperatingSystem

Keyword From Custom Library Overrides Keywords From Standard Library Even When Std Lib Imported With Different Name
    ${tc} =    Check Test Case    ${TEST NAME}
    Verify Override Message    ${ERRORS[3]}    ${tc.kws[0].msgs[0]}    Replace String
    ...    String    MyLibrary2    Std With Name    My With Name

No Warning When Custom Library Keyword Is Registered As RunKeyword Variant And It Has Same Name As Std Keyword
    Check Test Case    ${TEST NAME}
    Stderr Should Not Contain    Run Keyword If

Keyword In More Than One Custom Library And Standard Library
    Check Test Case    ${TEST NAME}
    Syslog Should Not Contain    BuiltIn.No Operation

Keywords are first searched from test case file even if they contain dot
    ${tc} =    Check Test Case    ${TESTNAME}
    Check log message    ${tc.kws[0].kws[0].msgs[0]}    Keyword in test case file overriding keyword in my_resource_1
    Check log message    ${tc.kws[0].kws[1].kws[0].msgs[0]}    Keyword in resource 1
    Check log message    ${tc.kws[1].kws[0].msgs[0]}    Keyword in test case file overriding keyword in BuiltIn
    Check log message    ${tc.kws[1].kws[1].msgs[0]}    Using keyword in test case file here!

*** Keywords ***
Verify override message
    [Arguments]    ${error msg}    ${kw msg}    ${kw}    ${standard}    ${custom}=MyLibrary1
    ...    ${std with name}=    ${ctm with name}=
    ${std imported as} =    Set Variable If    "${std with name}"    ${SPACE}imported as '${std with name}'    ${EMPTY}
    ${ctm imported as} =    Set Variable If    "${ctm with name}"    ${SPACE}imported as '${ctm with name}'    ${EMPTY}
    ${std long} =    Set Variable If    "${std with name}"    ${std with name}    ${standard}
    ${ctm long} =    Set Variable If    "${ctm with name}"    ${ctm with name}    ${custom}
    ${expected} =    Catenate
    ...    Keyword '${kw}' found both from a custom test library '${custom}'${ctm imported as}
    ...    and a standard library '${standard}'${std imported as}. The custom keyword is used.
    ...    To select explicitly, and to get rid of this warning, use either '${ctm long}.${kw}'
    ...    or '${std long}.${kw}'.
    Check Log Message    ${error msg}    ${expected}    WARN
    Check Log Message    ${kw msg}    ${expected}    WARN
