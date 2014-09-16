*** Settings ***
Documentation   Importing test libraries normally, using variable in library name, and importing libraries accepting arguments.
Force Tags      regression
Default Tags    pybot  jybot
Resource        atest_resource.robot
Suite Setup     Run Tests  ${EMPTY}  test_libraries/library_import_normal.robot


*** Test Cases ***
Normal Library Import
    Check Test Case  ${TESTNAME}

Library Import With Spaces In Name
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].messages[0]}  It works!
    Check Log Message  ${test.kws[1].messages[0]}  It really workz!!

Importing Library Class Should Have Been Syslogged
    ${base} =  Normalize Path  ${CURDIR}/../../testresources/testlibs
    Check Syslog Contains  Imported test library class 'ExampleLibrary'
    ...    from '${base}${/}ExampleLibrary
    ${path} =  Normalize Path  ${CURDIR}/../../testresources/testlibs/libmodule
    Check Syslog Contains  Imported test library module 'libmodule'
    ...    from '${base}${/}libmodule

Number Of Keywords In Imported Library Is Reported In Syslog
    Check Syslog Contains  | INFO \ |  Imported library 'ExampleLibrary' with arguments [ ] (version <unknown>, class type, testcase scope, 30 keywords)
    Check Syslog Contains  | INFO \ |  Imported library 'libmodule.LibClass1' with arguments [ ] (version <unknown>, class type, testcase scope, 1 keywords)

Warning Should Be Written To Syslog If Library Contains No Keywords
    Check Syslog Contains  | INFO \ |  Imported library 'libmodule' with arguments [ ] (version <unknown>, module type, global scope, 0 keywords)
    Check Syslog Contains  | WARN \ |  Imported library 'libmodule' contains no keywords

Importing Python Class From Module
    Check Test Case  ${TESTNAME}

Namespace is initialized during library init
    Check Test Case   ${TEST NAME}

Library Import With Variables
    Run Tests  ${EMPTY}  test_libraries/library_import_with_variable.robot
    Check Test Case  Verify Library Import With Variable In Name
    Check Test Case  Verify Library Import With List Variable

Library Import With Variables From Resource File
    Run Tests  ${EMPTY}  test_libraries/library_import_with_variable_from_resource.robot
    Check Test Case  Verify Library Import With Variable In Name
    Check Test Case  Verify Library Import With List Variable

Arguments To Library
    Run Tests  ${EMPTY}  test_libraries/library_with_0_parameters.robot  test_libraries/library_with_1_parameters.robot  test_libraries/library_with_2_parameters.robot
    Check Test Case  Two Default Parameters
    Check Test Case  One Default and One Set Parameter
    Check Test Case  Two Set Parameters

