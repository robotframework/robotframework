*** Settings ***
Library          DateTime
Variables        datesandtimes.py
Test Template    Month subtraction should succeed

*** Test Cases ***
Subtracting one month from a mid-month date
    2024-04-15 12:05:03          1                   2024-03-15 12:05:03.000

Subtracting using datetime input format
    ${datetime(2024,4,15,12,5,3)}    1              ${datetime(2024,3,15,12,5,3)}    result_format=datetime

Subtracting 12 months lands on the prior year
    2024-03-15                   12                  2023-03-15 00:00:00.000

Subtracting one month from Mar 31 clamps to Feb 29 (leap)
    2024-03-31                   1                   2024-02-29 00:00:00.000

Subtracting one month from Mar 31 clamps to Feb 28 (non-leap)
    2025-03-31                   1                   2025-02-28 00:00:00.000

Subtracting five months from Mar 31 lands on Oct 31
    2024-03-31 11:22:33.444       5                  2023-10-31 11:22:33.444

Negative subtraction adds months
    2024-04-15                   -2                  2024-06-15 00:00:00.000

*** Keywords ***
Month Subtraction Should Succeed
    [Arguments]    ${date}    ${months}    ${expected}    &{config}
    ${new_date} =    Subtract Months From Date    ${date}    ${months}    &{config}
    Should Be Equal    ${new_date}    ${expected}
