*** Settings ***
Documentation   NO RIDE because it would clean-up too much data.
Test Template  Should Be Equal

*** Variables ***
${VARIABLE}       Variable content
${SAME VARIABLE}  Variable content

*** Test Cases ***
Test Using Normal Keyword Is Not Possible With Template
  Fail  Fail

Test Default Template
  [Documentation]  FAIL Something != Different
  Same  Same
  42  42
  Something  Different

Test Continue On Failure
  [Documentation]  FAIL Several failures occurred:\n\n1) 42 != 43\n\n2) Something != Different
  Same  Same
  42  43
  Something  Different

Test Overriding Default Template In Test
  [Documentation]  FAIL Same == Same
  [Template]  Should Not Be Equal
  Same  Same
  42  43
  Something  Different

Test Overriding Default Template In Test With Empty Value
  [documentation]  FAIL This should be executed as normal keyword
  [Template]
  Fail  This should be executed as normal keyword

Test Overriding Default Template In Test With NONE Value
  [documentation]  FAIL This should be executed as normal keyword
  [Template]    NoNe
  Fail  This should be executed as normal keyword

Test Template With Variables
  [Template]  Expect Exactly Two Args
  ${VARIABLE}  ${VARIABLE}

Test Template With @{EMPTY} Variable
  [Template]   Test Template With Default Parameters
  @{EMPTY}

Test Template With Variables And Keyword Name
  [template]  Expect Exactly Three Args
  ${SAME VARIABLE}  Variable content  ${VARIABLE}

Test Template With Variable And Assign Mark (=)
  [Documentation]  FAIL  1= != 2=
  [Template]  Expect Exactly Two Args
  ${42} =     42 =
  ${42}=      42=
  ${1}=       ${2}=

Test Named Arguments
  [Documentation]  FAIL Several failures occurred:\n\n
  ...  1) foo != default\n\n
  ...  2) default != fool
  [Template]  Test Template With Default Parameters
  first=foo
  foo           second=foo
  first=foo     second=foo
  second=foo    first=foo
  second=fool

Test Varargs
  [Documentation]  FAIL 1 != 2 3
  [Template]  Test Template With Varargs
  ${EMPTY}
  Hello  Hello
  Hello world  Hello  world
  1 2 3 4 5 6 7 8 9 10  1  2  3  4  5  6  7  8  9  10
  1  2  3

Test Empty Values
  [Template]  Expect Exactly Two Args
  \           \
  ${EMPTY}    \

Test Template With FOR Loop
  [Documentation]  FAIL Several failures occurred:\n\n
  ...  1) This != Fails\n\n
  ...  2) This != Fails\n\n
  ...  3) Same != Different\n\n
  ...  4) This != Fails\n\n
  ...  5) Samething != Different
  Same  Same
  :FOR  ${item}  IN  Same  Different  Same
  \  Same  Same
  \  This  Fails
  \  Same  ${item}
  Samething  Different

Test Template With FOR Loop Containing Variables
  [Documentation]  FAIL Variable content != 42
  [Tags]  42
  :FOR  ${item}  IN  ${VARIABLE}  ${SAME VARIABLE}  @{TEST TAGS}
  \  ${VARIABLE}  ${item}

Test Template With FOR IN RANGE Loop
  [Documentation]  FAIL Several failures occurred:\n\n
  ...  1) 0 != 1\n\n
  ...  2) 0 != 2\n\n
  ...  3) 0 != 3\n\n
  ...  4) 0 != 4
  :FOR  ${index}  IN RANGE  5
  \  ${0}  ${index}

Test User Keywords Should Not Be Continued On Failure
    [Documentation]  FAIL Several failures occurred:\n\n1) expected failure\n\n2) second expected failure
    [Template]  Failing Uk With Multiple Fails
    expected failure
    second expected failure

Commented Rows With Test Template
    [Documentation]  FAIL Sanity != Check
    # My comment
    Same  Same  # Another comment
    # Yet another comment
    42  42
    Sanity  Check  # with comment

Templates with Run Keyword
    [Documentation]  FAIL  Several failures occurred:\n\n1) First failure\n\n2) No keyword with name 'Variable content =' found.
    [Template]  Run Keyword
    Should be equal  42  42
    Fail  First failure
    Expect exactly three args  xxx  xxx  xxx
    ${VARIABLE} =  Set variable  this doesn't work

Templates with continuable failures
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) Continuable 1\n\n
    ...  2) Continuable 1\n\n
    ...  3) Continuable 2\n\n
    ...  4) Continuable 1\n\n
    ...  5) Continuable 2\n\n
    ...  6) Continuable 3\n\n
    ...  7) Continuable 1\n\n
    ...  8) Continuable 2\n\n
    ...  9) Continuable 3\n\n
    ...  10) Continuable 4\n\n
    ...  11) Continuable 5
    [Template]  Continuable failures
    1
    2
    3
    5

Templates and timeouts
    [Documentation]  FAIL  Timeout error should happen only once
    [Timeout]  0.1 seconds  Timeout error should happen only once
    [Template]  Sleep
    0.3 seconds
    0.2 seconds
    0.1 seconds

Templates, timeouts, and for loops
    [Documentation]  FAIL  Timeout error should happen only once
    [Timeout]  0.1 seconds  Timeout error should happen only once
    [Template]  Sleep
    :FOR  ${i}  IN RANGE  10
    \    0.05 seconds

Templated test ends after syntax errors
    [Documentation]  FAIL Keyword 'BuiltIn.Should Be Equal' expected 2 to 4 arguments, got 5.
    syntax    error    makes    test    end
    not compared    anymore

Templated test continues after variable error
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) Variable '\${this does not exist}' not found.\n\n
    ...  2) compared and not equal != fails
    ${this does not exist}    ${this does not exist either}
    compared and equal        compared and equal
    compared and not equal    fails

Templates and fatal errors 1
    [Documentation]  FAIL  Several failures occurred:\n\n
    ...  1) First error\n\n
    ...  2) Second error is fatal and should stop execution
    [Template]  Run Keyword
    Fail  First error
    Fatal Error  Second error is fatal and should stop execution
    Fail  This should not be executed

Templates and fatal errors 2
    [Documentation]  FAIL  Test execution stopped due to a fatal error.
    Fail  This should not be executed

*** Keywords ***
Test Template With Default Parameters
  [Arguments]  ${first}=default  ${second}=default
  Should Be Equal  ${first}  ${second}

Test Template With Varargs
  [Arguments]  ${first}  @{second}
  ${second} =  Catenate  @{second}
  Should Be Equal  ${first}  ${second}

Expect Exactly Two Args  [arguments]  ${a1}  ${a2}
  Should Be Equal  ${a1}  ${a2}

Expect Exactly Three Args  [arguments]  ${a1}  ${a2}  ${a3}
  Should Be Equal  ${a1}  ${a2}
  Should Be Equal  ${a1}  ${a3}

Failing Uk With Multiple Fails  [arguments]  ${msg}
  Fail  ${msg}
  Fail  this should not occur

Continuable failures  [arguments]  ${count}
  :FOR  ${i}  IN RANGE  ${count}
  \  Run keyword and continue on failure  Fail  Continuable ${i+1}
