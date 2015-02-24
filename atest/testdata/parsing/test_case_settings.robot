*** Setting ***
T e s t S e t u p        Log    Default setup
testteardown     Log    Default teardown    INFO
Force T a g s        \    force-1       # Empty tags should be ignored
DefaultTags      @{DEFAULT TAGS}    \    default-3
Test Timeout      ${TIMEOUT} milliseconds

*** Variable ***
${VERSION}            1.2
@{DEFAULT TAGS}       default-1    default-2    # default-3 added separately
${TAG BASE}      test
@{TEST TAGS}          ${TAG BASE}-1    ${TAG BASE}-2    ${TAG BASE}-3
${LOG}                Log
${TIMEOUT}            99999

*** Test Case ***
Normal name
    No Operation

test_case names are NOT _forMatted_
    No Operation

Documentation
    [Documentation]    Documentation for this test case
    No Operation

Documentaion using old [Document] setting
    [Document]    This should be deprecated...
    No Operation

Documentation in multiple columns
    [Documentation]    Documentation    for this test case    in multiple columns
    No Operation

Documentation in multiple rows
    [DOCUMENTATION]    ${1}st line is shortdoc.
    ...                Documentation for this test case
    ...                in    multiple    rows.
    No Operation

Documentation multiple times
    [DOCUMENTATION]    This functionality should be deprecated.
    [DOCUMENT]         Documentation for this test case
    ...                multiple
    No Operation
    [DOCUMENTATION]    times.

Documentation with variables
    [Documentation]    Variables work in documentation since Robot ${VERSION}.
    No Operation

Documentation with non-existing variables
    [Documentation]    Starting from RF ${2}.1 ${NONEX} variables are just
    ...                left unchanged in all documentations. Existing ones
    ...                are replaced: "${TIMEOUT}"
    No Operation

Documentation with escaping
    [Documentation]    \${XXX}    c:\\temp    \    \\
    No Operation

Tags
    [Tags]    test-1    test-2
    No Operation

Empty and NONE tags are ignored
    [Tags]    test-2    \    ${EMPTY}    NONE    test-1    \    NONE    test-3
    No Operation

Duplicate tags are ignored and first used format has precedence
    [Documentation]    Case, space and underscore insensitive
    [Tags]    test 2    TEST 2    Test_2    Test_1    test 1    TEST1    __test__1__    FORCE-1
    No Operation

Tags in multiple rows
    [Tags]    test-0    ${EMPTY}
    ...    @{TEST TAGS}
    ...    test-4    TEST-0
    ...    \    test-5
    No Operation

Tags multiple times
    [Tags]    Should    deprecate
    No Operation
    [Tags]
    [Tags]    this

No own tags
    No Operation

Override default tags using empty setting
    [Tags]
    No Operation

Override default tags using NONE
    [Tags]    NONE
    No Operation

Tags with variables
    [TAGS]    @{TEST TAGS}    ${TAG BASE}-${4}    ${EMPTY}    test-5
    No Operation

Tags with non-existing variables
    [Documentation]    FAIL Replacing variables from test tags failed: Variable '\${non_existing}' not found.
    [t a g s]    @{non_existing}    ${non_existing}
    Fail    Not executed
Setup
    [Setup]    Log    Test case setup
    No Operation

Teardown
    No Operation
    [Teardown]    Log    Test case teardown

Default setup and teardown
    No Operation

Setup and teardown with variables
    [Setup]    ${LOG}    ${LOG}ged using variables ${1}
    No Operation
    [Teardown]    ${LOG}    ${LOG}ged using variables ${2}

Override setup and teardown using empty settings
    [Setup]
    No Operation
    [Teardown]

Override setup and teardown using NONE
    [Setup]    NONE
    No Operation
    [Teardown]    NONE

Setup and teardown with escaping
    [ s e t u p ]    Log    One backslash \\
    No Operation
    [ T E A R D O W N ]    Log    \${notvar} is not a variable

Template
    [Template]    Log
    Hello, world!
    Hi, tellus!    INFO

Timeout
    [Timeout]    1d
    No Operation

Timeout with message
    [Timeout]    123456ms    Message
    No Operation

Default timeout
    No Operation

Timeout with variables
    [TIME out]    ${TIMEOUT}
    No Operation

Override timeout using empty setting
    [Timeout]
    No Operation

Override timeout using NONE
    [Timeout]    NONE
    No Operation

Invalid timeout
    [Documentation]    FAIL Setup failed:
    ...    Setting test timeout failed: Invalid time string 'invalid'.
    [Timeout]    invalid    timeout value
    No Operation

Multiple settings
    [Documentation]    Documentation for this test case
    [Tags]    test-1    test-2
    [Timeout]    12345ms
    [Setup]    Log    Test case setup
    No Operation
    [Teardown]    Log    Test case teardown

Invalid setting
    [Documentation]    There is an error but test is run anyway.
    [Invalid]    This is invalid
    No Operation
