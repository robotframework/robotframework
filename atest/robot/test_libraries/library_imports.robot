*** Settings ***
Documentation     Importing test libraries normally, using variable in library name,
...               and importing libraries accepting arguments.
Suite Setup       Run Tests    ${EMPTY}    test_libraries/library_import_normal.robot
Resource          atest_resource.robot

*** Test Cases ***
Normal Library Import
    Check Test Case    ${TESTNAME}
    Syslog Should Contain    | INFO \ |    Imported library 'OperatingSystem' with arguments [ ] (version

Library Import With Spaces In Name Does Not Work
    Check Test Case    ${TESTNAME}
    Error In File    0    test_libraries/library_import_normal.robot    3
    ...    Importing library 'Date Time' failed: *Error: *
    ...    traceback=None

Importing Library Class Should Have Been Syslogged
    ${source} =    Normalize Path    ${CURDIR}/../../../src/robot/libraries/OperatingSystem
    Syslog Should Contain Match    | INFO \ |    Imported library class 'robot.libraries.OperatingSystem' from '${source}*'
    ${base} =    Normalize Path    ${CURDIR}/../../testresources/testlibs
    Syslog Should Contain Match    | INFO \ |    Imported library module 'libmodule' from '${base}${/}libmodule*'
    Syslog Should Contain Match    | INFO \ |    Imported library class 'libmodule.LibClass2' from '${base}${/}libmodule*'

Number Of Keywords In Imported Library Is Reported In Syslog
    Syslog Should Contain    | INFO \ |    Imported library 'libmodule.LibClass1' with arguments [ ] (version <unknown>, class type, TEST scope, 1 keywords)
    Syslog Should Contain    | INFO \ |    Imported library 'NamespaceUsingLibrary' with arguments [ ] (version <unknown>, class type, TEST scope, 2 keywords)

Warning Should Be Written To Syslog If Library Contains No Keywords
    Syslog Should Contain    | INFO \ |    Imported library 'libmodule' with arguments [ ] (version <unknown>, module type, GLOBAL scope, 0 keywords)
    Syslog Should Contain    | WARN \ |    Imported library 'libmodule' contains no keywords.

Importing Python Class From Module
    Check Test Case    ${TESTNAME}

Namespace is initialized during library init
    Check Test Case    ${TEST NAME}

Second import without parameters is ignored without warning
    Syslog Should Contain    | INFO \ |    Suite 'Library Import Normal' has already imported library 'libmodule' with same arguments. This import is ignored.

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
    Run Tests    --name Root    ${sources}
    Check Test Case    Two Default Parameters
    Check Test Case    One Default and One Set Parameter
    Check Test Case    Two Set Parameters

Second import with same parameters is ignored without warning
    Syslog Should Contain    | INFO \ |    Suite 'Root.Library With 1 Parameters' has already imported library 'ParameterLibrary' with same arguments. This import is ignored.

Second import with different parameters is ignored with warning
    Error in file    0    test_libraries/library_with_1_parameters.robot    4
    ...    Suite 'Root.Library With 1 Parameters' has already imported library 'ParameterLibrary' with different arguments. This import is ignored.
    ...    level=WARN
