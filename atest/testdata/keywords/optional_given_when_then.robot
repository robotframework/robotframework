*** Settings ***
Resource        resources/optional_given_when_then.robot

*** Test Cases ***
In user keyword name with normal arguments
    Given we don't drink too many beers
    When we are in  museum  cafe
    But we don't drink too many beers
    And time  does  not  run  out
    Then we get this feature ready today
    and we don't drink too many beers

In user keyword name with embedded arguments
    Given we are in Berlin city
    When it does not rain
    And we get this feature implemented
    Then we go to walking tour
    but it does not rain

In library keyword name
    Given Should Be Equal  1  1
    And Should Not Match  foo  bar
    But Should Match  foo  foo
    When set test variable  $foo  bar
    THEN should be equal  ${foo}  bar

In user keyword in resource file
    Given Keyword Is In Resource File
    and another resource file  keyword
    but another resource file  keyword

Correct Name Shown In Keyword Not Found Error
    [Documentation]  FAIL No keyword with name 'Given this keyword does not exist' found.
    Given this keyword does not exist

Keyword can be used with and without prefix
    GiveN we don't drink too many beers
    and we don't drink too many beers
    we don't drink too many beers
    When time  s  they  are  a-changing
    time  to  commit  soon  !
    Then we are in Berlin city
    we are in Berlin city

*** Keywords ***
We don't drink too many beers
    No Operation

We are in
    [Arguments]  ${a1}  ${a2}
    Should Be Equal  ${a1}-${a2}  museum-cafe

Time
    [Arguments]  @{args}
    Length Should Be  ${args}  4

we get this feature ready today
    Given we don't drink too many beers

We Are In ${name} city
    Should be equal  ${name}  Berlin

It Does Not ${x}
    Should Be Equal  ${x}  rain

We ${x} This ${thing} Implemented
    Should Be Equal  ${x}-${thing}  get-feature

We Go To ${somewhere}
    Should Be Equal  ${somewhere}  walking tour

