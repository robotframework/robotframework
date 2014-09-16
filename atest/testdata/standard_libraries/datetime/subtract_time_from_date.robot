*** Settings ***
Library          DateTime
Variables        datesandtimes.py
Test Template    Time Subtraction Should Succeed

*** Variables ***
${DATE1}           ${datetime(2014, 4, 24, 21, 45, 12, 123000)}
${DATE2}           ${datetime(2014, 4, 24, 22, 45, 12, 123000)}

*** Test Cases ***
Time subtraction from date should succeed
    ${DATE2}               1 hour                  ${DATE1}
    ${DATE2}               ${timedelta(hours=1)}   ${DATE1}
    23:47:13 2014.04.24    01:02:01.000            22:45:12 2014.04.24     %H:%M:%S %Y.%m.%d
    23:47:13 2014.04.24    00:00:00.100            23:47:12 2014.04.24     %H:%M:%S %Y.%m.%d

*** Keywords ***
Time Subtraction Should Succeed
    [Arguments]    ${date}    ${time}    ${expected}    ${format}=datetime
    ${new_date} =    Subtract Time From Date    ${date}    ${time}    ${format}    date_format=${format}
    Should Be Equal    ${new_date}    ${expected}
