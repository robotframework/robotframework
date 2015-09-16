*** Settings ***
Resource          atest_resource.robot

*** Test Cases ***
Import Libraries Only Once
    [Setup]    Run Tests And Set $SYSLOG    parsing/library_caching
    : FOR    ${name}    IN    Test 1.1    Test 1.2    Test 2.1    Test 2.2
    \    Check Test Case    ${name}
    Should Contain X Times    ${SYSLOG}    Imported library 'BuiltIn' with arguments [ ]    1
    Should Contain X Times    ${SYSLOG}    Found test library 'BuiltIn' with arguments [ ] from cache    2
    Should Contain X Times    ${SYSLOG}    Imported library 'OperatingSystem' with arguments [ ]    1
    Should Contain X Times    ${SYSLOG}    Found test library 'OperatingSystem' with arguments [ ] from cache    3
    Check Syslog Contains    | INFO \ |    Test library 'OperatingSystem' already imported by suite 'Library Caching.File1'
    Check Syslog Contains    | INFO \ |    Test library 'OperatingSystem' already imported by suite 'Library Caching.File2'

Process Resource Files Only Once
    [Setup]    Run Tests And Set $SYSLOG    parsing/resource_parsing
    Comment    Check that tests are run ok
    ${tc} =    Check Test Case    Test 1.1
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    variable value from 02 resource
    Check Log Message    ${tc.kws[1].msgs[0]}    variable value from 02 resource
    ${tc} =    Check Test Case    Test 4.1
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    variable value from 02 resource
    Check Log Message    ${tc.kws[1].msgs[0]}    variable value from 02 resource
    ${tc} =    Check Test Case    Test 4.2
    Check Log Message    ${tc.kws[0].kws[0].msgs[0]}    variable value from 03 resource
    Check Log Message    ${tc.kws[0].kws[1].msgs[0]}    variable value from 02 resource
    Check Log Message    ${tc.kws[0].kws[2].kws[0].msgs[0]}    variable value from 02 resource
    Check Log Message    ${tc.kws[1].msgs[0]}    variable value from 03 resource
    ${dir} =    Join Path    ${CURDIR}/../../testdata    parsing/resource_parsing
    Comment    These messages come twice. Once when they are parsed as test case    files and a second time when parsed as resource files.
    Should Contain X Times    ${SYSLOG}    Parsing file '${dir}${/}02_resource.robot'    2
    Should Contain X Times    ${SYSLOG}    Parsing file '${dir}${/}03_resource.robot'    2
    Comment    Check that resources were parsed only once
    Syslog File Should Contain In Order    Parsing test data directory    '${dir}'
    Syslog File Should Contain In Order    Parsing file    '${dir}${/}01_tests.robot'
    Syslog File Should Contain In Order    Parsing data source '${dir}${/}02_resource.robot' failed: File has no test case table.
    Syslog File Should Contain In Order    Parsing data source '${dir}${/}03_resource.robot' failed: File has no test case table.
    Syslog File Should Contain In Order    Parsing file    '${dir}${/}04_tests.robot'
    Syslog File Should Contain In Order    Started test suite    'Resource Parsing'
    Syslog File Should Contain In Order    Imported resource file    '${dir}${/}02_resource.robot'
    Syslog File Should Contain In Order    Imported resource file    '${dir}${/}03_resource.robot'
    Syslog File Should Contain In Order    Found resource file    '${dir}${/}02_resource.robot'    from cache
    Syslog File Should Contain In Order    Resource file    '${dir}${/}02_resource.robot'    already imported by suite 'Resource Parsing.04 Tests'
    Syslog File Should Contain In Order    Tests execution ended.

*** Keywords ***
Syslog File Should Contain In Order
    [Arguments]    @{parts}
    ${text} =    Catenate    @{parts}
    Should Contain X Times    ${SYSLOG}    ${text}    1
    ${pre}    ${post} =    Set Variable    ${SYSLOG.split("${text.replace('\\','\\\\')}")}
    Set Suite Variable    ${SYSLOG}    ${post}

Run Tests And Set $SYSLOG
    [Arguments]    ${path}
    Run Tests    ${EMPTY}    ${path}
    ${SYSLOG} =    Get Syslog
    Set Suite Variable    ${SYSLOG}
