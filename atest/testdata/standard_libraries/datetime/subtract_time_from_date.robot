*** Settings ***
Library          DateTime
Variables        datesandtimes.py
Test Template    Time Subtraction Should Succeed

*** Variables ***
${DATE1}           ${datetime(2014, 4, 24, 21, 45, 12, 123000)}
${DATE2}           ${datetime(2014, 4, 24, 22, 45, 12, 123000)}

*** Test Cases ***
Time subtraction from date should succeed
    ${DATE2}               1 hour                  ${DATE1}                datetime
    ${DATE2}               ${timedelta(hours=1)}   ${DATE1}                datetime
    23:47:13 2014.04.24    01:02:01.000            22:45:12 2014.04.24     %H:%M:%S %Y.%m.%d    %H:%M:%S %Y.%m.%d
    23:47:13 2014.04.24    00:00:00.100            23:47:12 2014.04.24     %H:%M:%S %Y.%m.%d    %H:%M:%S %Y.%m.%d

Time subtraction over DST boundary
    2015-10-26                1 day                    2015-10-25 00:00:00.000    timestamp
    ${datetime(2015,11,1)}    ${timedelta(days=31)}    ${datetime(2015,10,1)}     datetime

Calendar time subtraction from date should succeed
    2025-03-31                   1 month              2025-02-28 00:00:00.000    timestamp
    2024-03-31                   1 month 1 day        2024-02-28 00:00:00.000    timestamp
    2024-02-29                   1 year               2023-02-28 00:00:00.000    timestamp
    2025-01-31                   - 1 month            2025-02-28 00:00:00.000    timestamp
    ${datetime(2024,3,31,12)}    1 month              ${datetime(2024,2,29,12)}    datetime

*** Keywords ***
Time Subtraction Should Succeed
    [Arguments]    ${date}    ${time}    ${expected}    ${result_format}    ${date_format}=${NONE}
    ${new_date} =    Subtract Time From Date    ${date}    ${time}    ${result_format}    date_format=${date_format}
    Should Be Equal    ${new_date}    ${expected}
