*** Settings ***
Library           DateTime
Variables         datesandtimes.py

*** Test Cases ***
Date is not altered
    FOR    ${date}    IN    @{ALL_DAYS_FOR_YEAR(2015)}
        Date conversion should not alter value    ${date}
    END

Date is not altered during DST changes
    [Documentation]    DST changes as in Finland
    FOR    ${time}    IN    02:30    03:00    03:30    04:00    04:30    05:00
        Date conversion should not alter value    2015-03-29 ${time}:00
        Date conversion should not alter value    2015-10-25 ${time}:00
    END

Timestamps support years since 1900
    FOR    ${date}    IN    @{YEAR_RANGE(1900, 2200)}
        Date conversion should not alter value    ${date}    format=timestamp
    END

Datetime supports years since 1
    FOR    ${date}    IN    @{YEAR_RANGE(1, 2200, 10, format='datetime')}
        Date conversion should not alter value    ${date}    format=datetime
    END

Epoch supports years since 1970
    [Documentation]    This is minimum. Some platforms support 1900 or even earlier.
    FOR    ${date}    IN    @{YEAR_RANGE(1970, 2200, format='epoch')}
        Date conversion should not alter value    ${date}    format=epoch
    END

Too low year
    [Documentation]    Actual minimum depends on the platform.
    [Template]    Date conversion should fail
    0       timestamp
    -1      timestamp
    0       epoch
    -1      epoch
    0       datetime
    -1      datetime

*** Keywords ***
Date conversion should not alter value
    [Arguments]    ${date}    ${format}=timestamp
    ${result} =    Convert Date    ${date}    exclude_millis=yes    result_format=${format}
    Should Be Equal    ${result}    ${date}

Date conversion should fail
    [Arguments]    ${year}    ${format}
    Run Keyword And Expect Error    ValueError: *
    ...    Convert Date    ${year}-01-01    result_format=${format}
