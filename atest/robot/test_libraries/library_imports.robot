*** Settings ***
Documentation     Importing test libraries normally, using variable in library name, and importing libraries accepting arguments.
Suite Setup       Run Tests    ${EMPTY}    test_libraries/library_import_normal.robot
Resource          atest_resource.robot

*** Test Cases ***
Normal Library Import
    Check Test Case    ${TESTNAME}
    Check Syslog Contains    | INFO \ |    Imported library 'OperatingSystem' with arguments [ ] (version

Library Import With Spaces In Name Does Not Work
    Check Test Case    ${TESTNAME}
    Check Log Message    ${ERRORS[0]}
    ...    Error in file '*': Importing test library 'Date Time' failed: *Error: *
    ...    ERROR    pattern=true

Importing Library Class Should Have Been Syslogged
    [Tags]    no-standalone
    ${source} =    Normalize Path And Ignore Drive    ${CURDIR}/../../../src/robot/libraries/OperatingSystem
    Syslog Should Contain Match    | INFO \ |    Imported test library class 'robot.libraries.OperatingSystem' from '${source}*'
    ${base} =    Normalize Path And Ignore Drive    ${CURDIR}/../../testresources/testlibs
    Syslog Should Contain Match    | INFO \ |    Imported test library module 'libmodule' from '${base}${/}libmodule*'
    Syslog Should Contain Match    | INFO \ |    Imported test library class 'libmodule.LibClass2' from '${base}${/}libmodule*'

Number Of Keywords In Imported Library Is Reported In Syslog
    Check Syslog Contains    | INFO \ |    Imported library 'libmodule.LibClass1' with arguments [ ] (version <unknown>, class type, test case scope, 1 keywords)
    Check Syslog Contains    | INFO \ |    Imported library 'NamespaceUsingLibrary' with arguments [ ] (version <unknown>, class type, test case scope, 2 keywords)

Warning Should Be Written To Syslog If Library Contains No Keywords
    Check Syslog Contains    | INFO \ |    Imported library 'libmodule' with arguments [ ] (version <unknown>, module type, global scope, 0 keywords)
    Check Syslog Contains    | WARN \ |    Imported library 'libmodule' contains no keywords.

Importing Python Class From Module
    Check Test Case    ${TESTNAME}

Namespace is initialized during library init
    Check Test Case    ${TEST NAME}

Library Import With Variables
    Run Tests    ${EMPTY}    test_libraries/library_import_with_variable.robot
    Check Test Case    Verify Library Import With Variable In Name
    Check Test Case    Verify Library Import With List Variable

Library Import With Variables From Resource File
    Run Tests    ${EMPTY}    test_libraries/library_import_with_variable_from_resource.robot
    Check Test Case    Verify Library Import With Variable In Name
    Check Test Case    Verify Library Import With List Variable

Importing Zero Length Library
    Run Tests    ${EMPTY}     test_libraries/library_import_zero_len.robot
    Check Test Case    Verify Zero Length Library Import

Arguments To Library
    ${sources} =    Catenate
    ...    test_libraries/library_with_0_parameters.robot
    ...    test_libraries/library_with_1_parameters.robot
    ...    test_libraries/library_with_2_parameters.robot
    Run Tests    ${EMPTY}    ${sources}
    Check Test Case    Two Default Parameters
    Check Test Case    One Default and One Set Parameter
    Check Test Case    Two Set Parameters

*** Keywords ***
Normalize Path And Ignore Drive
    [Arguments]    ${path}
    ${path} =    Normalize Path    ${path}
    Return From Keyword If    os.sep == '/'    ${path}
    Return From Keyword    ?${path[1:]}
