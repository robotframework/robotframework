*** Settings ***
Suite Setup     Run Tests    --lang fi    keywords/optional_given_when_then.robot
Resource        atest_resource.robot

*** Test Cases ***
In user keyword name with normal arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    Given we don't drink too many beers
    Should Be Equal    ${tc[1].full_name}    When we are in
    Should Be Equal    ${tc[2].full_name}    But we don't drink too many beers
    Should Be Equal    ${tc[3].full_name}    And time
    Should Be Equal    ${tc[4].full_name}    Then we get this feature ready today
    Should Be Equal    ${tc[5].full_name}    and we don't drink too many beers

In user keyword name with embedded arguments
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    Given we are in Berlin city
    Should Be Equal    ${tc[1].full_name}    When it does not rain
    Should Be Equal    ${tc[2].full_name}    And we get this feature implemented
    Should Be Equal    ${tc[3].full_name}    Then we go to walking tour
    Should Be Equal    ${tc[4].full_name}    but it does not rain

In library keyword name
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    BuiltIn.Given Should Be Equal
    Should Be Equal    ${tc[1].full_name}    BuiltIn.And Should Not Match
    Should Be Equal    ${tc[2].full_name}    BuiltIn.But Should Match
    Should Be Equal    ${tc[3].full_name}    BuiltIn.When set test variable
    Should Be Equal    ${tc[4].full_name}    BuiltIn.THEN should be equal

In user keyword in resource file
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    optional_given_when_then.Given Keyword Is In Resource File
    Should Be Equal    ${tc[1].full_name}    optional_given_when_then.and another resource file

Correct Name Shown in Keyword Not Found Error
      Check Test Case    ${TEST NAME}

Keyword can be used with and without prefix
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    GiveN we don't drink too many beers
    Should Be Equal    ${tc[1].full_name}    and we don't drink too many beers
    Should Be Equal    ${tc[2].full_name}    We don't drink too many beers
    Should Be Equal    ${tc[3].full_name}    When time
    Should Be Equal    ${tc[4].full_name}    Time
    Should Be Equal    ${tc[5].full_name}    Then we are in Berlin city
    Should Be Equal    ${tc[6].full_name}    we are in Berlin city

Only one prefix is processed
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    Given we are in Berlin city
    Should Be Equal    ${tc[1].full_name}    but then we are in Berlin city

First word of a keyword can be a prefix
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    Given the prefix is part of the keyword

First word in a keyword can be an argument
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    Given we don't drink too many beers
    Should Be Equal    ${tc[1].full_name}    Then Pekka drinks lonkero instead
    Should Be Equal    ${tc[2].full_name}    and Miikka drinks water instead
    Should Be Equal    ${tc[3].full_name}    Étant donné Miikka drinks water instead

Localized prefixes
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    Oletetaan we don't drink too many beers
    Should Be Equal    ${tc[1].full_name}    Kun we are in
    Should Be Equal    ${tc[2].full_name}    mutta we don't drink too many beers
    Should Be Equal    ${tc[3].full_name}    Ja time
    Should Be Equal    ${tc[4].full_name}    Niin we get this feature ready today
    Should Be Equal    ${tc[5].full_name}    ja we don't drink too many beers

Prefix consisting of multiple words
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    Étant donné que multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc[1].full_name}    Zakładając, że multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc[2].full_name}    Diyelim ki multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc[3].full_name}    Eğer ki multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc[4].full_name}    O zaman multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc[5].full_name}    В случай че multipart prefixes didn't work with RF 6.0
    Should Be Equal    ${tc[6].full_name}    Fie ca multipart prefixes didn't work with RF 6.0

Prefix being part of another prefix
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc[0].full_name}    Étant donné que l'utilisateur se trouve sur la page de connexion
    Should Be Equal    ${tc[1].full_name}    étant Donné QUE l'utilisateur SE trouve sur la pAGe de connexioN
    Should Be Equal    ${tc[2].full_name}    Étant donné que if multiple prefixes match, longest prefix wins

Prefix must be followed by space
    Check Test Case    ${TEST NAME}
