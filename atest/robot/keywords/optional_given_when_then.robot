*** Settings ***
Suite Setup     Run Tests    --lang fi    keywords/optional_given_when_then.robot
Resource        atest_resource.robot

*** Test Cases ***
In user keyword name with normal arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].full_name}    Given we don't drink too many beers
    Should Be Equal    ${tc.kws[1].full_name}    When we are in
    Should Be Equal    ${tc.kws[2].full_name}    But we don't drink too many beers
    Should Be Equal    ${tc.kws[3].full_name}    And time
    Should Be Equal    ${tc.kws[4].full_name}    Then we get this feature ready today
    Should Be Equal    ${tc.kws[5].full_name}    and we don't drink too many beers

In user keyword name with embedded arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].full_name}    Given we are in Berlin city
    Should Be Equal    ${tc.kws[1].full_name}    When it does not rain
    Should Be Equal    ${tc.kws[2].full_name}    And we get this feature implemented
    Should Be Equal    ${tc.kws[3].full_name}    Then we go to walking tour
    Should Be Equal    ${tc.kws[4].full_name}    but it does not rain

In library keyword name
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].full_name}    BuiltIn.Given Should Be Equal
    Should Be Equal    ${tc.kws[1].full_name}    BuiltIn.And Should Not Match
    Should Be Equal    ${tc.kws[2].full_name}    BuiltIn.But Should Match
    Should Be Equal    ${tc.kws[3].full_name}    BuiltIn.When set test variable
    Should Be Equal    ${tc.kws[4].full_name}    BuiltIn.THEN should be equal

In user keyword in resource file
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].full_name}    optional_given_when_then.Given Keyword Is In Resource File
    Should Be Equal    ${tc.kws[1].full_name}    optional_given_when_then.and another resource file

Correct Name Shown in Keyword Not Found Error
      Check Test Case    ${TEST NAME}

Keyword can be used with and without prefix
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].full_name}    GiveN we don't drink too many beers
    Should Be Equal    ${tc.kws[1].full_name}    and we don't drink too many beers
    Should Be Equal    ${tc.kws[2].full_name}    We don't drink too many beers
    Should Be Equal    ${tc.kws[3].full_name}    When time
    Should Be Equal    ${tc.kws[4].full_name}    Time
    Should Be Equal    ${tc.kws[5].full_name}    Then we are in Berlin city
    Should Be Equal    ${tc.kws[6].full_name}    we are in Berlin city

Localized prefixes
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].full_name}    Oletetaan we don't drink too many beers
    Should Be Equal    ${tc.kws[1].full_name}    Kun we are in
    Should Be Equal    ${tc.kws[2].full_name}    mutta we don't drink too many beers
    Should Be Equal    ${tc.kws[3].full_name}    Ja time
    Should Be Equal    ${tc.kws[4].full_name}    Niin we get this feature ready today
    Should Be Equal    ${tc.kws[5].full_name}    ja we don't drink too many beers

Prefix consisting of multiple words
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].full_name}    Étant donné multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc.kws[1].full_name}    Zakładając, że multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc.kws[2].full_name}    Diyelim ki multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc.kws[3].full_name}    Eğer ki multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc.kws[4].full_name}    O zaman multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc.kws[5].full_name}    В случай че multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc.kws[6].full_name}    Fie ca multipart prefixes didn't work with RF 6.0

Prefix must be followed by space
    Check Test Case    ${TEST NAME}
