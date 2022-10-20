*** Settings ***
Suite Setup     Run Tests  --lang fi  keywords/optional_given_when_then.robot
Resource        atest_resource.robot

*** Test Cases ***
In user keyword name with normal arguments
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  Given we don't drink too many beers
    Should Be Equal  ${tc.kws[1].name}  When we are in
    Should Be Equal  ${tc.kws[2].name}  But we don't drink too many beers
    Should Be Equal  ${tc.kws[3].name}  And time
    Should Be Equal  ${tc.kws[4].name}  Then we get this feature ready today
    Should Be Equal  ${tc.kws[5].name}  and we don't drink too many beers

In user keyword name with embedded arguments
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  Given we are in Berlin city
    Should Be Equal  ${tc.kws[1].name}  When it does not rain
    Should Be Equal  ${tc.kws[2].name}  And we get this feature implemented
    Should Be Equal  ${tc.kws[3].name}  Then we go to walking tour
    Should Be Equal  ${tc.kws[4].name}  but it does not rain

In library keyword name
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  BuiltIn.Given Should Be Equal
    Should Be Equal  ${tc.kws[1].name}  BuiltIn.And Should Not Match
    Should Be Equal  ${tc.kws[2].name}  BuiltIn.But Should Match
    Should Be Equal  ${tc.kws[3].name}  BuiltIn.When set test variable
    Should Be Equal  ${tc.kws[4].name}  BuiltIn.THEN should be equal

In user keyword in resource file
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  optional_given_when_then.Given Keyword Is In Resource File
    Should Be Equal  ${tc.kws[1].name}  optional_given_when_then.and another resource file

Correct Name Shown in Keyword Not Found Error
    Check Test Case  ${TEST NAME}

Keyword can be used with and without prefix
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  GiveN we don't drink too many beers
    Should Be Equal  ${tc.kws[1].name}  and we don't drink too many beers
    Should Be Equal  ${tc.kws[2].name}  We don't drink too many beers
    Should Be Equal  ${tc.kws[3].name}  When time
    Should Be Equal  ${tc.kws[4].name}  Time
    Should Be Equal  ${tc.kws[5].name}  Then we are in Berlin city
    Should Be Equal  ${tc.kws[6].name}  we are in Berlin city

Localized prefixes
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  Oletetaan we don't drink too many beers
    Should Be Equal  ${tc.kws[1].name}  Kun we are in
    Should Be Equal  ${tc.kws[2].name}  mutta we don't drink too many beers
    Should Be Equal  ${tc.kws[3].name}  Ja time
    Should Be Equal  ${tc.kws[4].name}  Niin we get this feature ready today
    Should Be Equal  ${tc.kws[5].name}  ja we don't drink too many beers

Prefix consisting of multiple words
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Equal  ${tc.kws[0].name}  Étant donné multipart prefixes didn't work with RF 6.0
    Should Be Equal  ${tc.kws[1].name}  Zakładając, że multipart prefixes didn't work with RF 6.0
    Should Be Equal  ${tc.kws[2].name}  Diyelim ki multipart prefixes didn't work with RF 6.0
    Should Be Equal  ${tc.kws[3].name}  Eğer ki multipart prefixes didn't work with RF 6.0
    Should Be Equal  ${tc.kws[4].name}  O zaman multipart prefixes didn't work with RF 6.0
    Should Be Equal  ${tc.kws[5].name}  В случай че multipart prefixes didn't work with RF 6.0
    Should Be Equal  ${tc.kws[6].name}  Fie ca multipart prefixes didn't work with RF 6.0

Prefix must be followed by space
    Check Test Case  ${TEST NAME}
