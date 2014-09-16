*** Settings ***
Library          DateTime
Variables        datesandtimes.py
Test Template    Addition should succeed

*** Variables ***
${DATE1}           ${datetime(2014, 4, 24, 21, 45, 12, 123000)}
${DATE2}           ${datetime(2014, 4, 24, 22, 45, 12, 123000)}

*** Test Cases ***
Time addition to date should succeed
    ${DATE1}               1 hour           ${DATE2}
    ${DATE1}               1h               ${DATE2}
    22:45:12 2014.04.24    01:02:01.000     23:47:13 2014.04.24    %H:%M:%S %Y.%m.%d

*** Keywords ***
Addition Should Succeed
    [Arguments]    ${date}    ${time}    ${expected}     ${format}=datetime
    ${new_date} =    Add Time To Date    ${date}    ${time}    ${format}    date_format=${format}
    Should Be Equal    ${new_date}    ${expected}
