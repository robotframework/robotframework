*** Settings ***
Library           OperatingSystem
Library           EmbeddedArgs.py
Variables         vars.py
Resource          ${RESOURCE PATH_FROM_VARS}

Library           DoesNotExist
Variables         wrong_path.py
Resource          NonExisting.robot

# Non-existing variables in suite setups should be fine
Suite Setup       ${SUITE SETUP}
# Library keywords get NOT_RUN status. That should be OK teardown status.
Suite Teardown    No Operation

*** Variables ***
${SETUP}          No Operation
${TEARDOWN}       Teardown

*** Test Cases ***
Passing keywords
    Log    Hello from test
    ${contents}=    List Directory    .
    Simple UK
    This is validated

Keywords with embedded arguments
    Embedded arguments here
    Embedded args rock here
    Some embedded and normal args    42
    Some embedded and normal args    ${does not exist}
    This is validated

Library keyword with embedded arguments
    Log 42 times
    This is validated

Keywords that would fail
    Fail    Not actually executed so won't fail.
    Fail In Uk
    This is validated

Scalar variables are not checked in keyword arguments
    [Documentation]    Variables are too often set somehow dynamically that we cannot expect them to always exist.
    Log    ${TESTNAME}
    Log    ${this does not exist}
    This is validated

List variables are not checked in keyword arguments
    [Documentation]    See the doc of the previous test
    @{list} =    Create List    1    2    3    4
    Log    @{list}
    Anarchy in the UK    @{list}
    Anarchy in the UK    @{nonex}
    Fail    @{list}    @{nonex}
    This is validated

Dict variables are not checked in keyword arguments
    [Documentation]    See the doc of the previous test
    &{dict} =    Create Dictionary    a1=1    a2=2    a3=3
    Anarchy in the UK    &{dict}
    Anarchy in the UK    &{nonex}
    Fail    &{list}    &{nonex}
    This is validated

Variables are not checked in when arguments are embedded
    [Documentation]    See the doc of the previous test
    Embedded ${TESTNAME} here
    Embedded ${nonex} here
    This is validated

Setup/teardown with non-existing variable is ignored
    [Setup]    ${nonex setup}
    This is validated
    [Teardown]   ${nonex teardown}    ${nonex arg}

Setup/teardown with existing variable is resolved and executed
    [Setup]    ${SETUP}
    This is validated
    [Teardown]    ${TEARDOWN}    ${nonex arg}

User keyword return value
    ${quux}=    Some Return Value    ${foo}    ${bar}
    This is validated

Non-existing variable in user keyword return value
    Ooops Return Value
    This is validated

Test Setup And Teardown
    [Documentation]    FAIL    No keyword with name 'Does not exist' found.\n\n
    ...    Also teardown failed:\n
    ...    No keyword with name 'Does not exist' found.
    [Setup]  Log  Hello Setup
    Does not exist
    This is validated
    [Teardown]  Does not exist

Keyword Teardown
    [Documentation]    FAIL    Keyword teardown failed:
    ...    No keyword with name 'Does not exist' found.
    Keyword with Teardown
    This is validated

Keyword teardown with non-existing variable is ignored
    Keyword with teardown with non-existing variable
    This is validated

Keyword teardown with existing variable is resolved and executed
    Keyword with teardown with existing variable
    This is validated

Non-existing keyword name
    [Documentation]    FAIL    No keyword with name 'Does not exist' found.
    Does not exist
    This is validated

Invalid syntax in UK
    [Documentation]    FAIL
    ...    Invalid argument specification: Multiple errors:
    ...    - Invalid argument syntax '\${oops'.
    ...    - Non-default argument after default arguments.
    Invalid Syntax UK
    This is validated

Multiple Failures
    [Documentation]    FAIL    Several failures occurred:\n\n
    ...    1) Keyword 'BuiltIn.Should Be Equal' expected 2 to 8 arguments, got 1.\n\n
    ...    2) Invalid argument specification: Multiple errors:\n
    ...    - Invalid argument syntax '\${oops'.\n
    ...    - Non-default argument after default arguments.\n\n
    ...    3) Keyword 'Some Return Value' expected 2 arguments, got 3.\n\n
    ...    4) No keyword with name 'Yet another non-existing keyword' found.\n\n
    ...    5) No keyword with name 'Does not exist' found.
    Should Be Equal    1
    UK with multiple failures
    Does not exist
    This is validated

Avoid keyword in dry-run
    Keyword not run in dry-run
    Another keyword not run in dry-run
    Keyword with keywords not run in dry-run
    This is validated

*** Keywords ***
Embedded ${args} here
    No Operation

Some ${type} and normal args
    [Arguments]    ${meaning of life}
    No Operation

Keyword with Teardown
    No Operation
    [Teardown]    Does not exist

Keyword with teardown with non-existing variable
    No Operation
    [Teardown]    ${I DO NOT EXIST}

Keyword with teardown with existing variable
    No Operation
    [Teardown]    ${TEARDOWN}    ${I DO NOT EXIST}

Invalid Syntax UK
    [Arguments]    ${arg}=def    ${oops
    No Operation

Some Return Value
    [Arguments]    ${a1}    ${a2}
    RETURN    ${a1}-${a2}

Ooops return value
    RETURN    ${ooops}

UK with multiple failures
    Invalid Syntax UK
    Some Return Value    too    many    arguments
    Yet another non-existing keyword

Teardown
    [Arguments]    ${arg}
    Log    ${arg}

Keyword not run in dry-run
    [Tags]    robot:no-dry-run
    I don't exist and I'm OK (at least in dry-run)
    Should Be Equal    More arguments would be needed
    Invalid Syntax UK

Another keyword not run in dry-run
    [Tags]    ROBOT: no-dry-run
    non-existing
    ${invalid}

Keyword with keywords not run in dry-run
    Keyword not run in dry-run
    Another keyword not run in dry-run
    This is validated
