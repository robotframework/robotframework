*** Settings ***
Library          DateTime
Variables        datesandtimes.py
Test Template    Subtraction Should Succeed

*** Variables ***
${DATE1}           ${datetime(2014, 4, 24, 21, 45, 12, 123000)}
${DATE2}           ${datetime(2014, 4, 24, 22, 45, 12, 123000)}

*** Test Cases ***
Subtraction between two dates should succeed
    [Template]  Subtraction should succeed
    ${DATE2}                   ${DATE1}               1 hour
    ${DATE1}                   ${DATE2}               - 1 hour
    ${DATE2}                   ${DATE1}               ${3600.0}               result_format=number
    ${DATE2}                   ${DATE1}               01:00:00.000            result_format=timer
    ${DATE2}                   ${DATE1}               1h                      result_format=compact
    ${DATE2}                   ${DATE1}               ${timedelta(hours=1)}   result_format=timedelta
    2014.04.24 22:45:12.123    ${DATE1}               1 hour
    22:45:12 2014.04.24        2014-04-24 21.43.11    01:02:01.000            result_format=timer   date1_format=%H:%M:%S %Y.%m.%d     date2_format=%Y-%m-%d %H.%M.%S

Date subtraction over DST boundary
    2015-10-26                 2015-10-25               1 day
    ${datetime(2015,11,1)}    ${datetime(2015,10,1)}    ${timedelta(days=31)}    result_format=timedelta

*** Keywords ***
Subtraction Should Succeed
    [Arguments]    ${latter_date}    ${former_date}    ${expected}    ${result_format}=verbose    ${date1_format}=${NONE}    ${date2_format}=${NONE}
    ${diff} =    Subtract Date From Date    ${latter_date}    ${former_date}    ${result_format}    date1_format=${date1_format}    date2_format=${date2_format}
    Should Be Equal    ${diff}    ${expected}
