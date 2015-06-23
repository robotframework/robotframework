*** Settings ***
Library          DateTime
Variables        datesandtimes.py
Test Template    Addition should succeed

*** Variables ***
${DATE1}           ${datetime(2014, 4, 24, 21, 45, 12, 123000)}
${DATE2}           ${datetime(2014, 4, 24, 22, 45, 12, 123000)}
${DATE2B}          ${datetime(2014, 4, 24, 22, 45, 12)}

*** Test Cases ***
Time addition to date should succeed
    ${DATE1}                   1 hour             ${DATE2}                   result_format=datetime
    ${DATE1}                   1h                 ${DATE2}                   result_format=datetime    exclude_millis=false
    ${DATE1}                   1h                 ${DATE2B}                  result_format=datetime    exclude_millis=yes
    22:45:12 2014.04.24        01:02:03           23:47:15 2014.04.24        result_format=%H:%M:%S %Y.%m.%d    date_format=%H:%M:%S %Y.%m.%d

Time addition to date over DST boundary
    2015-10-25                 1 day              2015-10-26 00:00:00        exclude_millis=yes
    20151001 02:03:04.005      31 days            2015-11-01 02:03:04.005
    ${datetime(2015,10,25)}    ${timedelta(1)}    ${datetime(2015,10,26)}    result_format=datetime

*** Keywords ***
Addition Should Succeed
    [Arguments]    ${date}    ${time}    ${expected}     &{config}
    ${new_date} =    Add Time To Date    ${date}    ${time}    &{config}
    Should Be Equal    ${new_date}    ${expected}
