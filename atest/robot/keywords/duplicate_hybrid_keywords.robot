*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/duplicate_hybrid_keywords.robot
Resource         atest_resource.robot

*** Test Cases ***
Using keyword defined multiple times fails
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].full_name}    DupeHybridKeywords.Defined Twice
    Error in library    DupeHybridKeywords
    ...    Adding keyword 'DEFINED TWICE' failed:
    ...    Keyword with same name defined multiple times.

Keyword with embedded arguments defined multiple times fails at run-time
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].full_name}    Embedded twice
    Length Should Be    ${ERRORS}    1

Exact duplicate is accepted
    Check Test Case    ${TESTNAME}
