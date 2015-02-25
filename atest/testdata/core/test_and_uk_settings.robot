*** Setting ***
T e s t S e t u p        Log    Default test setup
testteardown     Log    Default test teardown    INFO
Force T a g s        \    force-1       # Empty tags should be ignored
DefaultTags      @{default_tags}    \    default-3
Test Timeout      ${test_timeout}


*** Variable ***
${version}        1.2
@{default_tags}    default-1    default-2    # default-3 added separately
${test_tag_base}    test
@{test_tags}      ${test_tag_base}-1    ${test_tag_base}-2    ${test_tag_base}-3
${default}        Default
${log}            Log
${test_timeout}    999 milliseconds
${keyword_timeout}    ${test_timeout}
${10ms}              10 milliseconds

*** Test Case ***
lower case test case name
    [Timeout]    5 seconds    First tests are sometimes slooow with IronPython
    No Operation

Test Case Documentation
    [Documentation]    Documentation for this test case
    [Timeout]    5 seconds    First tests are sometimes slooow with IronPython
    No Operation

Test Case Documentation in Multiple Columns
    [Document]    Documentation    for this test case    in multiple columns
    No Operation

Test Case Documentation in Multiple Lines
    [DOCUMENTATION]    ${1}st line is shortdoc.
    ...                Documentation for this test case
    [DOCUMENT]         in\nmultiple\nlines
    No Operation

Test Case Documentation With Variables
    [Documentation]    Variables work in documentation since Robot ${version}
    No Operation

Test Case Documentation With Non-Existing Variables
    [Documentation]    Starting from RF ${2}.1 ${NONEX} variables are just
    ...                left unchanged in all documentations. Existing ones
    ...                are replaced: "${10ms}"
    No Operation

Test Case Tags
    [Documentation]    Test case with tags. Empty tags should be ignored
    [Tags]    test-1    \    test-2
    No Operation

Test Case Tags With Variables
    [TAGS]    \    @{test_tags}    ${test_tag_base}-4    ${EMPTY}    test-5
    No Operation

Test Case Tags With Non-Existing Variables
    [Documentation]    FAIL Replacing variables from test tags failed: Variable '\${non_existing}' not found.
    [t a g s]    @{non_existing}    ${non_existing}
    Fail    Not executed

Test Case Tags In Multiple Rows
    [Tags]    @{test_tags}    test-4    test-5
    No Operation

Test Case Default Tags
    [Documentation]    Should contain tags as defined in settings Default Tags and Force Tags
    No Operation

Test Case Setup
    [Setup]    Log    Test case setup
    No Operation

Test Case Teardown
    No Operation
    [Teardown]    Log    Test case teardown

Test Case Setup With Escapes
    [ s e t u p ]    Log    One backslash \\
    No Operation

Test Case Teardown With Escapes
    No Operation
    [ T E A R D O W N ]    Log    \${notvar} is not a variable

Suite Level Test Timeout
    [Documentation]    FAIL Test timeout ${test_timeout} exceeded.
    Sleep    4

Test Case Timeout
    [Documentation]    FAIL Test timeout 1 millisecond exceeded.
    [Setup]    NONE
    [Timeout]    0.001 second
    Sleep    3

Test Case Timeout 2
    [ timeout ]
    Sleep    1111 ms

Test Case Timeout With Variables
    [Documentation]    FAIL Test timeout 10 milliseconds exceeded.
    [Setup]    NONE
    [TIME out]    ${10ms}
    Sleep    2

Test Case With Invalid Timeout
    [Documentation]    FAIL Setup failed:
    ...    Setting test timeout failed: Invalid time string 'invalid'.
    [Timeout]    invalid    timeout value
    No Operation

Multiple Test Case Metas
    [Documentation]    Documentation for this test case
    [Tags]    test-1    test-2
    [Setup]    Log    Test case setup
    No Operation
    [Teardown]    Log    Test case teardown

Test Case With Invalid Metadata
    [Documentation]    There should be an error at parsing time but test ought to be executed anyway.
    [Invalid Test Meta]    This is invalid
    No Operation

Escaping Metadata in Test Case Table
    [Documentation]    Two backslashes \\\\
    No Operation

Lower Case User Keyword Name
    uk with lower case name
    UK WITH LOWERCASE NAME
    UkWith LOWER case n a m e

User Keyword Documentation
    UK Documentation
    Multicolumn UK Documentation

User Keyword With Short Documentation
    UK With Short Documentation

User Keyword Documentation with Variables
    UK Documentation With Variables

User Keyword Documentation with non Existing Variables
    UK Documentation With Non-Existing Variables

User Keyword Arguments
    UK With One Argument    one
    UK With Multiple Arguments    one    two    three

User Keyword Return
    ${ret}    UK With Return
    Should Be Equal    ${ret}    Return value
    ${ret1}    ${ret2}    ${ret3} =    UK With Return Multiple    one    two
    Should Be Equal    ${ret1}    one
    Should Be Equal    ${ret2}    \${arg2}
    Should Be Equal    ${ret3}    three

User Keyword Timeout
    [Documentation]    FAIL Keyword timeout 10 milliseconds exceeded.
    [Timeout]    60s
    User Keyword Timeout

User Keyword Timeout With Variables
    [Documentation]    FAIL Keyword timeout ${keyword_timeout} exceeded.
    [Timeout]
    User Keyword Timeout With Variables

User Keyword With Invalid Timeout
    [Documentation]    FAIL Setting keyword timeout failed: Invalid time string 'invalid uk'.
    User Keyword With Invalid Timeout

User Keyword With Multiple Metas
    ${ret} =    UK With Multiple Metas    World
    Should Be Equal    ${ret}    Hello World!!

User Keyword With Invalid Metadata
    [Documentation]    There should be an error at parsing time but user keywords ought to be executed anyway FAIL This keyword is executed
    UK With Invalid Meta Passing
    UK With Invalid Meta Failing    This keyword is executed

*** Keyword ***
UK Documentation
    [Documentation]    Documentation for a user keyword
    No Operation

Multicolumn UK Documentation
    [Doc U Ment A Tion]    Documentation     in     multiple     columns
    No Operation

UK With Short Documentation
    [Document]    This is the short doc and also the only thing logged.
    ...    Nothing after the first newline is logged. So here we can have
    ...    anything else we want and only Libdoc will see it.
    No Operation

UK Documentation With Variables
    [Documentation]    Variables work in documentation since Robot ${version}
    No Operation

UK Documentation With Non-Existing Variables
    [Documentation]    Starting from RF ${2}.1 @{non_existing} variables are left unchanged in docs.
    ...    Also after ${short doc}.
    No Operation

UK With One Argument
    [Arguments]    ${arg}
    Log    ${arg}

UK With Multiple Arguments
    [arguments]    ${arg1}    ${arg2}    ${arg3}
    Log    ${arg1} ${arg2} ${arg3}

UK With Return
    No Operation
    [Return]    Return value

UK With Return Multiple
    [A R G U M E N T S]    ${arg1}    ${arg2}
    No Operation
    [R E T U R N]    ${arg1}    \${arg2}    three

UK With Multiple Metas
    [Arguments]    ${name}
    [Documentation]    Documentation for a user keyword
    No Operation
    [Return]    Hello ${name}!!

UK With Invalid Meta Passing
    [Documentation]    Invalid metadata causes an error but user keyword itself is executed
    [Invalid UK Meta]    This is invalid
    No Operation

UK With Invalid Meta Failing
    [Arguments]    ${msg}
    [Documentation]    Invalid metadata causes an error but user keyword itself is executed
    [Invalid]    Yes, this is also invalid
    Fail    ${msg}

uk with lower case name
    No Operation

User Keyword Timeout
    [Timeout]    0.01s
    Sleep    3

User Keyword Timeout With Variables
    [TIMEOUT]    ${keyword_timeout}
    Sleep    4

User Keyword With Invalid Timeout
    [timeout]    invalid uk    timeout value
    Sleep    4
