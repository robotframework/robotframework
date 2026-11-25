*** Settings ***
Library           DateTime

*** Test Cases ***
Non-finite time inputs
    FOR    ${value}    IN    inf    -INF    NaN    1e400    -1e400    1e308 days
        Run Keyword And Expect Error    ValueError: Time value * is not finite.
        ...    Convert Time    ${value}
    END
    FOR    ${value}    IN    ${{float('inf')}}    ${{float('-inf')}}    ${{float('nan')}}
        Run Keyword And Expect Error    ValueError: Time value * is not finite.
        ...    Convert Time    ${value}
    END

Non-finite times fail before formatting or rounding
    FOR    ${format}    IN    number    verbose    compact    timer    timedelta
        FOR    ${exclude_millis}    IN    ${False}    ${True}
            Run Keyword And Expect Error    ValueError: Time value * is not finite.
            ...    Convert Time    inf    ${format}    ${exclude_millis}
        END
    END

Integers too large for time conversion
    FOR    ${value}    IN    ${{10**400}}    ${{-10**400}}
        Run Keyword And Expect Error    ValueError: Time value * is too large.
        ...    Convert Time    ${value}
    END

Time arithmetic producing infinity
    Run Keyword And Expect Error    ValueError: Time value * is not finite.
    ...    Add Time To Time    1e308    1e308
    Run Keyword And Expect Error    ValueError: Time value * is not finite.
    ...    Subtract Time From Time    -1e308    1e308

Non-finite epoch inputs
    FOR    ${value}    IN    ${{float('inf')}}    ${{float('-inf')}}    ${{float('nan')}}
        Run Keyword And Expect Error    ValueError: Epoch time * is not finite.
        ...    Convert Date    ${value}
    END

Epoch inputs outside supported range
    FOR    ${value}    IN    ${{10**400}}    ${{-10**400}}    ${1e20}    ${-1e20}    ${3e11}
        Run Keyword And Expect Error    ValueError: Epoch time * is outside the supported date range.
        ...    Convert Date    ${value}
    END

Date calculations use timedelta range error
    FOR    ${keyword}    IN    Add Time To Date    Subtract Time From Date
        Run Keyword And Expect Error
        ...    ValueError: * cannot be represented as a timedelta object. Values must be between -999999999 and 999999999 days.
        ...    ${keyword}    2024-01-01    1e20
    END
    Run Keyword And Expect Error
    ...    ValueError: * cannot be represented as a timedelta object. Values must be between -999999999 and 999999999 days.
    ...    Get Current Date    increment=1e20

Date arithmetic outside supported range
    Run Keyword And Expect Error    ValueError: Resulting date is outside the supported date range.
    ...    Add Time To Date    2024-01-01    1e7 days
    Run Keyword And Expect Error    ValueError: Resulting date is outside the supported date range.
    ...    Subtract Time From Date    0001-01-01    1 day
    Run Keyword And Expect Error    ValueError: Resulting date is outside the supported date range.
    ...    Get Current Date    increment=1e7 days

Rounding outside supported date range
    Run Keyword And Expect Error    ValueError: Resulting date is outside the supported date range.
    ...    Convert Date    9999-12-31 23:59:59.9999    exclude_millis=yes
    Run Keyword And Expect Error    ValueError: Resulting date is outside the supported date range.
    ...    Convert Date    9999-12-31 23:59:59.9999

Finite numeric inputs still work
    ${value} =    Convert Time    1e100
    Should Be Equal    ${value}    ${1e100}
    ${value} =    Add Time To Time    1e100    -1e100
    Should Be Equal    ${value}    ${0.0}
    ${value} =    Convert Date    ${0}    result_format=epoch
    Should Be Equal    ${value}    ${0.0}
    ${value} =    Add Time To Date    9999-12-30    1 day
    Should Be Equal    ${value}    9999-12-31 00:00:00.000
    ${value} =    Subtract Time From Date    0001-01-02    1 day    result_format=datetime
    Should Be Equal As Strings    ${value}    0001-01-01 00:00:00
