*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/builtin/reload_library/reload_library.robot
Resource         atest_resource.robot

*** Test Cases ***
Reload and add keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Check log message     ${tc.kws[2].msgs[0]}    Reloaded library Reloadable with 7 keywords.

Reloading changes args
    ${tc}=    Check Test Case    ${TESTNAME}
    Should be equal    ${tc.kws[0].doc}   Doc for original 1 with args arg
    Should be equal    ${tc.kws[3].doc}   Doc for original 1 with args arg1, arg2

Reloading can remove a keyword
    Check Test Case    ${TESTNAME}

Reloading with instance
    Check Test Case    ${TESTNAME}

Changes are reflected in next instance
    Check Test Case    ${TESTNAME}

Reloading non-existing
    Check Test Case    ${TESTNAME}

Reloading non-existing instance
    Check Test Case    ${TESTNAME}

Reloading None fails
    Check Test Case    ${TESTNAME}

Static library
    ${tc}=    Check Test Case    ${TESTNAME}
    Should be equal    ${tc.kws[2].doc}    This doc for static

Module library
    ${tc}=    Check Test Case    ${TESTNAME}
    Should be equal    ${tc.kws[3].doc}    This doc for module
