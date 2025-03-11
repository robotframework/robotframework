*** Settings ***
Suite Setup       Keyword
Suite Teardown    Keyword

*** Test Cases ***
Basics
    GROUP    1st group
        Log    Inside group
        Log    Still inside
    END
    GROUP
    ...    second
        Log    Inside second group
    END
    Log    After

Failing
    [Documentation]    FAIL    Failing inside GROUP!
    GROUP    Fails
        Fail    Failing inside GROUP!
        Fail    Not run
    END
    GROUP    Not run
        Fail    Not run
    END

Anonymous
    GROUP
       Log    Inside unnamed group
    END

Variable in name
    GROUP    Test is named: ${TEST_NAME}
        Log    ${TEST_NAME}
    END
    GROUP    ${42}
        Log    Should be 42
    END

In user keyword
    Keyword

*** Keywords ***
Keyword
    Log    Before
    GROUP    First
        Log    low level
        Log    another low level
    END
    GROUP    Second
        Log    yet another low level
    END
    Log    After
