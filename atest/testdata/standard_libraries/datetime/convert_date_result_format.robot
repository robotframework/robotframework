*** Settings ***
Test Template     Date Conversion Should Succeed
Library           DateTime
Variables         datesandtimes.py

*** Variables ***
${DATE}              ${datetime(2014, 4, 24, 21, 45, 12)}
${DATE w/ MILLIS}    ${datetime(2014, 4, 24, 21, 45, 12, 123000)}
${DATE w/ MICRO}     ${datetime(2014, 4, 24, 21, 45, 12, 123456)}

*** Test Cases ***    INPUT                      FORMAT               OUTPUT                     INPUT FORMAT
Should convert to timestamp
                      2014-04-24 21:45:12.123    timeSTAMP            2014-04-24 21:45:12.123
                      2014-04-24 21:45:12.123    tImestamp            2014-04-24 21:45:12.123    %Y-%m-%d %H:%M:%S.%f
                      20140424 21:45:12.12399    tImestamp            2014-04-24 21:45:12.124    %Y%m%d %H:%M:%S.%f
                      ${EPOCH}                   TIMEstamp            2014-04-24 21:45:12.000
                      ${DATE}                    TimeStamp            2014-04-24 21:45:12.000
                      ${DATE w/ MILLIS}          TimeStamp            2014-04-24 21:45:12.123
                      ${DATE w/ MICRO}           TimeStamp            2014-04-24 21:45:12.123

Timestamp should contain millis rounded to three digits
                      2014-07-30 17:31:00        timestamp            2014-07-30 17:31:00.000
                      2014-07-30 17:31:00.000    timestamp            2014-07-30 17:31:00.000
                      2014-07-30 17:31:00.0000   timestamp            2014-07-30 17:31:00.000
                      2014-07-30 17:31:00.5      timestamp            2014-07-30 17:31:00.500
                      2014-07-30 17:31:00.500    timestamp            2014-07-30 17:31:00.500
                      2014-07-30 17:31:00.5000   timestamp            2014-07-30 17:31:00.500
                      2014-07-30 17:31:00.9      timestamp            2014-07-30 17:31:00.900
                      2014-07-30 17:31:00.999    timestamp            2014-07-30 17:31:00.999
                      2014-07-30 17:31:00.9995   timestamp            2014-07-30 17:31:01.000
                      2014-12-31 23:59:59.99999  timestamp            2015-01-01 00:00:00.000

Should convert to timestamp with format
                      2014-04-24 21:45:12.123    %H:%M:%S %Y-%m-%d    21:45:12 2014-04-24
                      2014-04-24 21:45:12.999    %H:%M:%S %Y-%m-%d    21:45:12 2014-04-24
                      20140424 21:45:12.123456   %Y%m%d %H:%M:%S.%f   20140424 21:45:12.123456
                      20140424 21:45:12.123456   %H:%M:%S.%f          21:45:12.123456
                      20140424 21:45:12.123      %H:%M:%S.%f          21:45:12.123000
                      20140424 21:45             %H:%M:%S.%f          21:45:00.000000
                      2014/04/24 21:45:12.123    %H:%M %Y-%m-%d       21:45 2014-04-24           %Y/%m/%d %H:%M:%S.%f

Should convert to epoch
                      2014-04-24 21:45:12.123    epoch                ${EPOCH + 0.123}
                      2014-04-24 21:45:12.123    epoch                ${EPOCH + 0.123}           %Y-%m-%d %H:%M:%S.%f
                      ${EPOCH}                   epoch                ${EPOCH}
                      ${DATE w/ MICRO}           epoch                ${EPOCH + 0.123456}

Should convert to datetime
                      20140424 21:45:12.123456   datetime             ${DATE w/ MICRO}
                      20140424 21:45:12.123456   datetime             ${DATE w/ MICRO}           %Y%m%d %H:%M:%S.%f
                      ${EPOCH + 0.123456}        DateTiMe             ${DATE w/ MICRO}
                      ${DATE}                    datetime             ${DATE}
                      ${DATE w/ MILLIS}          datetime             ${DATE w/ MILLIS}
                      ${DATE w/ MICRO}           datetime             ${DATE w/ MICRO}

Should exclude milliseconds
                      [Template]    Date Conversion Should Succeed Without Milliseconds
                      2014-04-24 21:45:12.123    timestamp            2014-04-24 21:45:12
                      2014-04-24 21:45:12.999    timestamp            2014-04-24 21:45:13
                      2014-04-24 21:45:12.99999  timestamp            2014-04-24 21:45:13
                      ${DATE}                    timestamp            2014-04-24 21:45:12
                      ${EPOCH + 0.123}           %Y-%m-%d %H:%M:%S    2014-04-24 21:45:12
                      ${EPOCH + 0.500}           %Y-%m-%d %H:%M:%S    2014-04-24 21:45:13
                      ${DATE}                    datetime             ${datetime(2014, 4, 24, 21, 45, 12)}
                      ${DATE w/ MILLIS}          datetime             ${datetime(2014, 4, 24, 21, 45, 12)}
                      ${DATE w/ MICRO}           datetime             ${datetime(2014, 4, 24, 21, 45, 12)}
                      ${EPOCH + 0.123}           datetime             ${datetime(2014, 4, 24, 21, 45, 12)}
                      ${EPOCH + 0.500}           datetime             ${datetime(2014, 4, 24, 21, 45, 13)}
                      ${EPOCH + 0.123}           epoch                ${EPOCH}
                      ${EPOCH + 0.500}           epoch                ${EPOCH + 1}

Epoch time is float regardless are millis included or not
                      [Template]    Epoch time format should be
                      ${1000.123}                1000.123             false
                      ${1000}                    1000.0               ${EMPTY}
                      ${1000.123}                1000.0               true
                      ${1000}                    1000.0               no millis

Formatted with %f in middle
    [Template]    NONE
    Run Keyword If    sys.platform == 'cli'
    ...   Run Keyword And Expect Error    ValueError: %f directive is supported only at the end of the format string on this Python interpreter.
    ...   Date Conversion Should Succeed    2014-04-24 21:45:12.123    %H:%M:%S.%f %Y-%m-%d    21:45:12.123000 2014-04-24
    ...   ELSE
    ...   Date Conversion Should Succeed    2014-04-24 21:45:12.123    %H:%M:%S.%f %Y-%m-%d    21:45:12.123000 2014-04-24

*** Keywords ***
Date Conversion Should Succeed
    [Arguments]    ${input}    ${output_format}    ${expected}    ${input_format}=${NONE}
    ${ts} =    Convert Date    ${input}    ${output_format}    date_format=${input_format}
    Should Be Equal    ${ts}    ${expected}

Date Conversion Should Succeed Without Milliseconds
    [Arguments]    ${input}    ${output_format}    ${expected}
    ${ts} =    Convert Date    ${input}    ${output_format}    exclude_millis=True
    Should Be Equal    ${ts}    ${expected}

Epoch time format should be
    [Arguments]    ${input}    ${expected}    ${millis}
    ${result} =    Convert Date    ${input}    result_format=epoch    exclude_millis=${millis}
    Should Be Equal As Strings    ${result}    ${expected}
