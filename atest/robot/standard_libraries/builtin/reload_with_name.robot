*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/builtin/reload_library/reload_with_name.robot
Resource         atest_resource.robot

*** Test Cases ***
Reload with name
    ${tc}=    Check Test Case    ${TESTNAME}
    Check log message     ${tc.kws[1].msgs[0]}    Reloaded library foo with 7 keywords.

Reload with instance
    Check Test Case    ${TESTNAME}

Original name is not usable when import with WITH NAME
    Check Test Case    ${TESTNAME}
