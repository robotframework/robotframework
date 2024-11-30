*** Settings ***
Suite Setup    Keyword With A Group
Suite Teardown    Keyword With A Group


*** Test Cases ***
Simple GROUP
    GROUP
    ...    name 1
        Log    low level
        Log    another low level
    END
    GROUP    name 2
        Log    yet another low level
    END
    Log    this is the end

GROUP in keywords
    Keyword With A Group

Anonymous GROUP
    GROUP
       Log    this group has no name
    END

Test With Vars In GROUP Name
    GROUP    Test is named: ${TEST_NAME}
        Log    ${TEST_NAME}
    END
    GROUP    ${42}
        Log    Should be 42
    END


*** Keywords ***
Keyword With A Group
    Log    top level
    GROUP    frist keyword GROUP
        Log    low level
        Log    another low level
    END
    GROUP     second keyword GROUP
        Log    yet another low level
    END
    Log    this is the end