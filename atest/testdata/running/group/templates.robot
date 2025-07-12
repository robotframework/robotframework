*** Settings ***
Test Template     Run Keyword

*** Test Cases ***
Pass
    GROUP    1
        Log     1.1
    END
    GROUP    2
        Log     2.1
        Log     2.2
    END

Pass and fail
    [Documentation]    FAIL    2.1
    GROUP    1
        Log     1.1
    END
    GROUP    2
        Fail    2.1
        Log     2.2
    END
    GROUP    3
        Log     3.1
    END

Fail multiple times
    [Documentation]    FAIL    Several failures occurred:
    ...
    ...    1) 1.1
    ...
    ...    2) 2.1
    ...
    ...    3) 2.3
    ...
    ...    4) 4.1
    GROUP    1
        Fail    1.1
    END
    GROUP    2
        Fail    2.1
        Log     2.2
        Fail    2.3
    END
    GROUP    3
        Log     3.1
    END
    GROUP    4
        Fail    4.1
    END

Pass and skip
    GROUP    1
        Skip    1.1
    END
    GROUP    2
        Log     2.1
    END
    GROUP    3
        Skip    3.1
        Log     3.2
    END

Pass, fail and skip
    [Documentation]    FAIL    1.1
    GROUP    1
        Fail    1.1
        Skip    1.2
        Log     1.3
    END
    GROUP    2
        Skip    2.1
    END
    GROUP    3
        Log     3.1
    END

Skip all
    [Documentation]    SKIP    All iterations skipped.
    GROUP    1
        Skip    1.1
        Skip    1.2
    END
    GROUP    2
        Skip    2.1
    END

Just one that is skipped
    [Documentation]    SKIP    1.1
    GROUP    1
        Skip    1.1
    END
