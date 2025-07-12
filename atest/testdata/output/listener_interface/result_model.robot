*** Settings ***
Suite Setup       Log    Library keyword
Suite Teardown    User keyword

*** Test Cases ***
Test
    Log    Library keyword
    User keyword
    TRY
        Wait Until Keyword Succeeds    1x    0s    Fail    Ooops!
    EXCEPT    Keyword 'Fail' failed after retrying 1 time. The last error was: Ooops!
        No Operation
    END

*** Keywords ***
User keyword
    Log    User keyword    DEBUG
    Log    Not logged      TRACE
    Log    Remove me!
