*** Settings ***
Library          DateTime
Variables        datesandtimes.py
Test Template    Month addition should succeed

*** Test Cases ***
Adding one month to a mid-month date
    2014-01-15 12:05:03          1                   2014-02-15 12:05:03.000

Adding one month using datetime input format
    ${datetime(2014,1,15,12,5,3)}    1              ${datetime(2014,2,15,12,5,3)}    result_format=datetime

Adding multiple months crosses a year boundary
    2024-11-15                   3                   2025-02-15 00:00:00.000

Adding ten months to Mar 31 lands on Jan 31 the year after next
    2024-03-31 23:59:59          10                  2025-01-31 23:59:59.000

Adding one month to Jan 31 clamps to Feb 29 in a leap year
    2024-01-31                   1                   2024-02-29 00:00:00.000

Adding one month to Jan 31 clamps to Feb 28 in a non-leap year
    2025-01-31                   1                   2025-02-28 00:00:00.000

Adding one month to Mar 31 clamps to Apr 30
    2024-03-31 11:22:33.444       1                  2024-04-30 11:22:33.444

Adding a negative month subtracts months
    2024-06-15                   -2                  2024-04-15 00:00:00.000

Subtracting two months from Mar 31 yields Jan 31
    2024-03-31                   -2                  2024-01-31 00:00:00.000

Large positive month delta spans many years
    2024-01-15                   25                  2026-02-15 00:00:00.000

*** Keywords ***
Month Addition Should Succeed
    [Arguments]    ${date}    ${months}    ${expected}    &{config}
    ${new_date} =    Add Months To Date    ${date}    ${months}    &{config}
    Should Be Equal    ${new_date}    ${expected}
