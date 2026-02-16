*** Settings ***
Resource          atest_resource.robot

*** Test Cases ***
Import Libraries Only Once
    [Setup]    Run Tests And Set $SYSLOG    parsing/library_caching
    FOR    ${name}    IN    Test 1.1    Test 1.2    Test 2.1    Test 2.2
        Check Test Case    ${name}
    END
    Should Contain X Times    ${SYSLOG}    Imported library 'BuiltIn' with arguments [ ] (version    1
    Should Contain X Times    ${SYSLOG}    Found library 'BuiltIn' with arguments [ ] from cache.    2
    Should Contain X Times    ${SYSLOG}    Imported library 'OperatingSystem' with arguments [ ] (version    1
    Should Contain X Times    ${SYSLOG}    Found library 'OperatingSystem' with arguments [ ] from cache.    3
    Syslog Should Contain    | INFO \ |    Suite 'Library Caching.File1' has already imported library 'OperatingSystem' with same arguments. This import is ignored.
    Syslog Should Contain    | INFO \ |    Suite 'Library Caching.File2' has already imported library 'OperatingSystem' with same arguments. This import is ignored.

Process Resource Files Only Once
    [Setup]    Run Tests And Set $SYSLOG    parsing/resource_parsing
    # Check that tests are run ok
    ${tc} =    Check Test Case    Test 1.1
    Check Log Message    ${tc[0, 0, 0]}    variable value from 02 resource
    Check Log Message    ${tc[1, 0]}    variable value from 02 resource
    ${tc} =    Check Test Case    Test 4.1
    Check Log Message    ${tc[0, 0, 0]}    variable value from 02 resource
    Check Log Message    ${tc[1, 0]}    variable value from 02 resource
    ${tc} =    Check Test Case    Test 4.2
    Check Log Message    ${tc[0, 0, 0]}    variable value from 03 resource
    Check Log Message    ${tc[0, 1, 0]}    variable value from 02 resource
    Check Log Message    ${tc[0, 2, 0, 0]}    variable value from 02 resource
    Check Log Message    ${tc[1, 0]}    variable value from 03 resource
    ${dir} =    Normalize Path    ${DATADIR}/parsing/resource_parsing
    Should Contain X Times    ${SYSLOG}    Parsing file '${dir}${/}02_resource.robot'             1
    Should Contain X Times    ${SYSLOG}    Parsing resource file '${dir}${/}02_resource.robot'    1
    Should Contain X Times    ${SYSLOG}    Parsing file '${dir}${/}03_resource.robot'             1
    Should Contain X Times    ${SYSLOG}    Parsing resource file '${dir}${/}03_resource.robot'    1
    # Check that resources were parsed only once
    Syslog File Should Contain In Order    Parsing directory '${dir}'.
    Syslog File Should Contain In Order    Parsing file '${dir}${/}01_tests.robot'.
    Syslog File Should Contain In Order    Data source '${dir}${/}02_resource.robot' has no tests or tasks.
    Syslog File Should Contain In Order    Data source '${dir}${/}03_resource.robot' has no tests or tasks.
    Syslog File Should Contain In Order    Parsing file '${dir}${/}04_tests.robot'.
    Syslog File Should Contain In Order    Started suite 'Resource Parsing'
    Syslog File Should Contain In Order    Imported resource file '${dir}${/}02_resource.robot'
    Syslog File Should Contain In Order    Imported resource file '${dir}${/}03_resource.robot'
    Syslog File Should Contain In Order    Found resource file '${dir}${/}02_resource.robot' from cache
    Syslog File Should Contain In Order    Resource file '${dir}${/}02_resource.robot' already imported by suite 'Resource Parsing.04 Tests'
    Syslog File Should Contain In Order    Tests execution ended.

*** Keywords ***
Syslog File Should Contain In Order
    [Arguments]    ${text}
    Should Contain X Times    ${SYSLOG}    ${text}    1
    ${pre}    ${post} =    Set Variable    ${SYSLOG.split("${text.replace('\\','\\\\')}")}
    Set Suite Variable    ${SYSLOG}    ${post}

Run Tests And Set $SYSLOG
    [Arguments]    ${path}
    Run Tests    ${EMPTY}    ${path}
    ${SYSLOG} =    Get Syslog
    Set Suite Variable    ${SYSLOG}
