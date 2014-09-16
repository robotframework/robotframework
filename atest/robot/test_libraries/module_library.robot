*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  test_libraries/module_library.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***
Passing
    Check Test Case  ${TESTNAME}

Failing
    Check Test Case  ${TESTNAME}

Logging
    ${test} =  Check Test Case  ${TESTNAME}
    Check Log Message  ${test.kws[0].msgs[0]}  Hello from module library
    Check Log Message  ${test.kws[0].msgs[1]}  WARNING!  WARN

Returning
    Check Test Case  ${TESTNAME}

One Argument
    Check Test Case  ${TESTNAME}

Many Arguments
    Check Test Case  ${TESTNAME}

Default Arguments
    Check Test Case  ${TESTNAME}

Variable Arguments
    Check Test Case  ${TESTNAME}

Only Methods And Functions Are Keywords
    Check Test Case  ${TESTNAME}

Class Methods In Module Library Are Not Keywords
    Check Test Case  ${TESTNAME}

Functions starting with underscore are not keywords
    Check Test Case  ${TESTNAME}

If __all__ is present, only functions listed there are available
    Check Test Case  ${TESTNAME} 1
    Check Test Case  ${TESTNAME} 2
    Check Test Case  ${TESTNAME} 3
    Check Test Case  ${TESTNAME} 4
    Keyword should not have been added  join
    Keyword should not have been added  not_in_all

Class Method Assigned To Module Variable
    Check Test Case  ${TESTNAME}

Lambda Keyword
    Check Test Case  ${TESTNAME}

Lambda Keyword With Arguments
    Check Test Case  ${TESTNAME}

Attribute With Same Name As Module
    Check Test Case  ${TESTNAME}

Importing Submodule As Library
    Check Test Case  ${TESTNAME}

Module Library Scope Should Be Global
    Check Syslog Contains  Imported library 'module_library' with arguments [ ] (version test, module type, global scope, 12 keywords)

Importing Module Should Have Been Syslogged
    ${path} =  Normalize Path  ${CURDIR}/../../testresources/testlibs/module_library
    Check Syslog Contains  Imported test library module 'module_library' from '${path}


***Keywords***

Keyword should not have been added
    [Arguments]  ${kw}  ${lib}=module_lib_with_all
    Check Syslog Contains  Adding keyword '${kw}' to library '${lib}' failed: Not exposed as a keyword
