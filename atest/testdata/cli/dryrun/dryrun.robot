*** Settings ***
Library  OperatingSystem
Variables  vars.py
Resource  ${RESOURCE PATH_FROM_VARS}

Library  DoesNotExist
Variables  wrong_path.py
Resource  NonExisting.tsv

# Library keywords get NOT_RUN status. That should be OK teardown status.
Suite Teardown    No Operation


*** Variables ***
${value}    value

*** Test Cases ***

Passing keywords
    Log  Hello from test
    ${contents}=  List Directory  .
    Simple UK

Keywords with embedded arguments
    Embedded arguments here
    Embedded args rock here

Keywords that would fail
    Fail  Not actually executed so won't fail.
    Fail In Uk
    No Operation

Scalar variables are not checked in keyword arguments
    [Documentation]  Variables are too often set somehow dynamically that we cannot expect them to always exist.
    Log  ${TESTNAME}
    Log  ${this does not exist}

List variables are not checked in keyword arguments
    [Documentation]  See the doc of the previous test
    @{list} =  Create List  1  2  3  4
    Log  @{list}
    Anarchy in the UK  @{list}
    Anarchy in the UK  @{nonex}
    Fail   @{list}  @{nonex}

Variables are not checked in when arguments are embedded
    [Documentation]  See the doc of the previous test
    Embedded ${TESTNAME} here
    Embedded ${nonex} here

User keyword return value
    ${quux}=  Some Return Value  ${foo}  ${bar}

Test Setup And Teardown
    [Documentation]  FAIL No keyword with name 'Does not exist' found.\n\nAlso teardown failed:\nNo keyword with name 'Does not exist' found.
    [Setup]  Log  Hello Setup
    Does not exist
    [Teardown]  Does not exist

Keyword Teardown
    [Documentation]  FAIL Keyword teardown failed:\nNo keyword with name 'Does not exist' found.
    Keyword with Teardown

For Loops
    [Documentation]  FAIL Keyword 'resource.Anarchy in the UK' expected 3 arguments, got 2.
    ::FOR  ${i}  IN RANGE  10
    \   Log  ${i}
    \   Simple UK
    For Loop in UK
    ::FOR  ${a}  ${b}  IN RANGE  ${NONE}
    \   Anarchy in the UK  1  2

Non-existing keyword name
    [Documentation]  FAIL No keyword with name 'Does not exist' found.
    Does not exist

Invalid syntax in UK
    [Documentation]  FAIL Invalid argument specification: Invalid argument syntax '${arg'.
    Invalid Syntax UK

Multiple Failures
    [Documentation]  FAIL Several failures occurred:\n\n
    ...  1) Keyword 'BuiltIn.Should Be Equal' expected 2 to 4 arguments, got 1.\n\n
    ...  2) Invalid argument specification: Invalid argument syntax '${arg'.\n\n
    ...  3) Keyword 'BuiltIn.Log' expected 1 to 5 arguments, got 6.\n\n
    ...  4) No keyword with name 'Yet another non-existing keyword' found.\n\n
    ...  5) No keyword with name 'Does not exist' found.
    Should Be Equal  1
    UK with multiple failures
    Does not exist


*** Keywords ***
Embedded ${args} here
    No Operation

Keyword with Teardown
    No Operation
    [Teardown]  Does not exist

Invalid Syntax UK
    [Arguments]  ${arg
    No Operation

Some Return Value
    [Arguments]  ${a1}  ${a2}
    [Return]  ${a1}-${a2}

UK with multiple failures
    Invalid Syntax UK
    Log  too  many  arguments  here  we  have
    Yet another non-existing keyword
