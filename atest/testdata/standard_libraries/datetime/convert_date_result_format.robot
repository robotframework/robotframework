*** Settings ***
Test Template     Date Conversion Should Succeed
Library           DateTime
Variables         datesandtimes.py

*** Variables ***
${DT}                 ${datetime(2018, 11, 22, 13, 13, 42)}
${DT w/ MILLIS}       ${datetime(2018, 11, 22, 13, 13, 42, 123000)}
${DT w/ MICRO}        ${datetime(2018, 11, 22, 13, 13, 42, 123456)}

*** Test Cases ***    INPUT                      FORMAT               OUTPUT                     INPUT FORMAT
Timestamp             2014-04-24 21:45:12.123    timeSTAMP            2014-04-24 21:45:12.123
                      3014-04-24 21:45:12.123    timeSTAMP            3014-04-24 21:45:12.123
                      2014-04-24 21:45:12.123    tImestamp            2014-04-24 21:45:12.123    %Y-%m-%d %H:%M:%S.%f
                      20140424 21:45:12.12399    tImestamp            2014-04-24 21:45:12.124    %Y%m%d %H:%M:%S.%f
                      ${EPOCH}                   TIMEstamp            2018-11-22 13:13:42.000
                      ${DT}                      TimeStamp            2018-11-22 13:13:42.000
                      ${DT w/ MILLIS}            TimeStamp            2018-11-22 13:13:42.123
                      ${DT w/ MICRO}             TimeStamp            2018-11-22 13:13:42.123

Milliseconds handling with timestamps
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

Custom timestamp      2014-04-24 21:45:12.123    %H:%M:%S %Y-%m-%d    21:45:12 2014-04-24
                      2014-04-24 21:45:12.999    %H:%M:%S %Y-%m-%d    21:45:12 2014-04-24
                      20140424 21:45:12.123456   %Y%m%d %H:%M:%S.%f   20140424 21:45:12.123456
                      2014-04-24 21:45:12.123    %H:%M:%S.%f %Y-%m-%d  21:45:12.123000 2014-04-24
                      20140424 21:45:12.123456   %H:%M:%S.%f          21:45:12.123456
                      20140424 21:45:12.123      %H:%M:%S.%f          21:45:12.123000
                      20140424 21:45             %H:%M:%S.%f          21:45:00.000000
                      2014/04/24 21:45:12.123    %H:%M %Y-%m-%d       21:45 2014-04-24           %Y/%m/%d %H:%M:%S.%f

Datetime              20181122 13:13:42.123456   datetime             ${DT w/ MICRO}
                      20181122 13:13:42.123456   datetime             ${DT w/ MICRO}           %Y%m%d %H:%M:%S.%f
                      ${EPOCH + 0.123456}        DateTiMe             ${DT w/ MICRO}
                      ${DT}                      datetime             ${DT}
                      ${DT w/ MILLIS}            datetime             ${DT w/ MILLIS}
                      ${DT w/ MICRO}             datetime             ${DT w/ MICRO}

Date                  20260806 13:17:42.123456   date                 ${date(2026, 8, 6)}
                      20260806 13:17:42.123456   date                 ${date(2026, 8, 6)}        %Y%m%d %H:%M:%S.%f
                      ${EPOCH + 0.123456}        DATE                 ${date(2018, 11, 22)}
                      ${DT}                      date                 ${date(2018, 11, 22)}
                      ${DT w/ MILLIS}            date                 ${date(2018, 11, 22)}
                      ${DT w/ MICRO}             date                 ${date(2018, 11, 22)}

Epoch                 2018-11-22 13:13:42.123    epoch                ${EPOCH + 0.123}
                      2018-11-22 13:13:42.123    epoch                ${EPOCH + 0.123}           %Y-%m-%d %H:%M:%S.%f
                      ${EPOCH}                   epoch                ${EPOCH}
                      ${DT w/ MICRO}             epoch                ${EPOCH + 0.123456}

Excluding milliseconds
                      [Template]    Date Conversion Should Succeed Without Milliseconds
                      2014-04-24 21:45:12.123    timestamp            2014-04-24 21:45:12
                      2014-04-24 21:45:12.999    timestamp            2014-04-24 21:45:13
                      2014-04-24 21:45:12.99999  timestamp            2014-04-24 21:45:13
                      ${DT}                      timestamp            2018-11-22 13:13:42
                      ${EPOCH + 0.123}           %Y-%m-%d %H:%M:%S    2018-11-22 13:13:42
                      ${EPOCH + 0.500}           %Y-%m-%d %H:%M:%S    2018-11-22 13:13:43
                      ${DT}                      datetime             ${datetime(2018, 11, 22, 13, 13, 42)}
                      ${DT w/ MILLIS}            datetime             ${datetime(2018, 11, 22, 13, 13, 42)}
                      ${DT w/ MICRO}             datetime             ${datetime(2018, 11, 22, 13, 13, 42)}
                      ${EPOCH + 0.123}           datetime             ${datetime(2018, 11, 22, 13, 13, 42)}
                      ${EPOCH + 0.500}           datetime             ${datetime(2018, 11, 22, 13, 13, 43)}
                      ${EPOCH + 0.123}           epoch                ${EPOCH}
                      ${EPOCH + 0.500}           epoch                ${EPOCH + 1}

Epoch is float regardless are millis included or not
                      [Template]    Epoch time format should be
                      ${1000000.123}             1000000.123          false
                      ${1000000}                 1000000.0            ${EMPTY}
                      ${1000000.123}             1000000.0            true
                      ${1000000}                 1000000.0            no millis

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
    Should Be Equal    ${result}    ${expected}    type=float
